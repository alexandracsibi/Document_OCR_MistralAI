from __future__ import annotations

from typing import Callable, List, Optional, Pattern

from ocr_service.core.utils.extract import (
    extract_from_label,
    norm_lines
)
from ocr_service.core.utils.normalize import parse_dates_iso
from ocr_service.documents.registration import rules as rr



def _looks_like_c_label_line(line: str) -> bool:
    """
    Don't take C.* lines as continuation/next-line values.
    Additionally, for registration we stop reading entirely after the first C-block line.
    """
    s = (line or "").lstrip()
    if not s:
        return False
    if s[0].upper() != "C":
        return False
    if len(s) == 1:
        return True
    nxt = s[1]
    return nxt == "." or nxt.isdigit() or nxt.isspace()


def _reg_lines(text: str) -> list[str]:
    """
    Normalized non-empty lines, truncated at first C-block line.
    """
    out: list[str] = []
    for ln in norm_lines(text or ""):
        if _looks_like_c_label_line(ln):
            break
        out.append(ln)
    return out

def _x(
    text: str,
    *,
    label_re: Pattern[str],
    value_re: Optional[Pattern[str]] = None,
    fallback_re: Optional[Pattern[str]] = None,
    validator: Optional[Callable[[str], bool]] = None,
) -> Optional[str]:
    """
    REGISTRATION wrapper around the shared extract_from_label:
      - uses registration-specific normalized/truncated lines
      - uses rr.STOP_LABELS for inline cut + scan stop
      - supports optional validator/value_re/fallback
    """
    lines = _reg_lines(text)
    return extract_from_label(
        lines,
        label_re=label_re,
        stop_label_pats=rr.STOP_LABELS,
        value_re=value_re,
        validator=validator,
        fallback_re=fallback_re,
        full_text_for_fallback=(text or "") if fallback_re is not None else None,
        skip_pred=None,  # already truncated at C-block
    )

# can be moved to validate.py?
def _is_plain_int_no_leading_zero(s: str) -> bool:
    t = (s or "").strip()
    if not t.isdigit():
        return False
    return not t.startswith("0")

def _to_first_iso_date(s: str) -> Optional[str]:
    ds = parse_dates_iso(s or "")
    return ds[0] if ds else None

def extract_document_number(text: str) -> Optional[str]:
    """
    Registration document number: 2 letters + 5 digits.
    OCR usually contains it twice; accept only if the same token appears >= 2 times.
    """
    if not text:
        return None

    hits = rr.DOCUMENT_NUMBER_VALUE.findall(text)
    if not hits:
        return None
    
    seen: set[str] = set()
    for a, b in hits:
        tok = f"{a}{b}".upper()
        if tok in seen:
            return tok
        seen.add(tok)

    return None

def extract_A(text: str) -> Optional[str]:
    return _x(
        text,
        label_re=rr.A_LABEL,
        value_re=rr.PLATE_VALUE,     # accept only if plate-like near the label
        fallback_re=rr.PLATE_VALUE,  # otherwise search globally
    )


def extract_B(text: str) -> Optional[str]:
    raw = _x(
        text,
        label_re=rr.B_LABEL,
        validator=lambda s: bool(parse_dates_iso(s)),
    )
    return _to_first_iso_date(raw) if raw else None


def extract_D1(text: str) -> Optional[str]:
    return _x(text, label_re=rr.D1_LABEL)


def extract_D2(text: str) -> Optional[str]:
    return _x(text, label_re=rr.D2_LABEL)


def extract_D3(text: str) -> Optional[str]:
    return _x(text, label_re=rr.D3_LABEL)


def extract_E(text: str) -> Optional[str]:
    return _x(
        text,
        label_re=rr.E_LABEL,
        value_re=rr.VIN_VALUE,
        fallback_re=rr.VIN_VALUE,
    )


def extract_F1(text: str) -> Optional[str]:
    return _x(
        text,
        label_re=rr.F1_LABEL,
        value_re=rr.KG_VALUE,
        fallback_re=None,  # avoid grabbing G's weight globally
    )


def extract_G(text: str) -> Optional[str]:
    return _x(
        text,
        label_re=rr.G_LABEL,
        value_re=rr.KG_VALUE,
        fallback_re=None,
    )


def extract_H(text: str) -> Optional[str]:
    return _x(text, label_re=rr.H_LABEL)


def extract_I(text: str) -> Optional[str]:
    raw = _x(
        text,
        label_re=rr.I_LABEL,
        validator=lambda s: bool(parse_dates_iso(s)),
    )
    if not raw:
        raw = _x(
            text,
            label_re=rr.I_ALIAS_1_LABEL,
            validator=lambda s: bool(parse_dates_iso(s)),
        )
    return _to_first_iso_date(raw) if raw else None


def extract_J(text: str) -> Optional[str]:
    def is_category(s: str) -> bool:
        s = s or ""
        return any(ch.isalpha() for ch in s) and any(ch.isdigit() for ch in s)

    v = _x(text, label_re=rr.J_LABEL, validator=is_category)
    if v:
        return v
    return _x(text, label_re=rr.J_ALIAS_1_LABEL, validator=is_category)


def extract_K(text: str) -> Optional[str]:
    return _x(text, label_re=rr.K_LABEL)


def extract_O(text: str) -> Optional[str]:
    """
    Towing block is notoriously messy in OCR: O / O.1 / O.2 / (0)-(3) can degrade to 0/01/02 etc.
    We keep this doc-local. Output is a compact summary like: "O.1=1200 KG; O.2=650 KG".
    """
    lines = _reg_lines(text)

    anchors = [
        ("O.1", rr.O1_LABEL),
        ("O.2", rr.O2_LABEL),
        ("(0)", rr.PAREN_0_LABEL),
        ("(1)", rr.PAREN_1_LABEL),
        ("(2)", rr.PAREN_2_LABEL),
        ("(3)", rr.PAREN_3_LABEL),
    ]

    def _is_o_block_end(line: str) -> bool:
        return any(p.search(line or "") for p in rr.STOP_O_BLOCK_END)

    def _find_kg_near(start_idx: int, lookahead: int = 6) -> Optional[str]:
        for j in range(start_idx, min(len(lines), start_idx + lookahead)):
            if j > start_idx and _is_o_block_end(lines[j]):
                break
            m = rr.KG_VALUE.search(lines[j])
            if m:
                return (m.group(0) or "").strip() or None
        return None

    results: List[str] = []
    seen = set()

    for i, ln in enumerate(lines):
        for key, pat in anchors:
            if not pat.search(ln):
                continue

            kg = _find_kg_near(i, lookahead=6)
            if not kg:
                continue

            # Avoid S.2 collision: if "O.2" matched from bare "02" right after S.2 label, skip.
            if key == "O.2":
                prev = lines[i - 1] if i - 1 >= 0 else ""
                if rr.S2_LABEL.search(prev):
                    continue

            if key not in seen:
                seen.add(key)
                results.append(f"{key}={kg}")

    return "; ".join(results) if results else None


def extract_P1(text: str) -> Optional[str]:
    return _x(
        text,
        label_re=rr.P1_LABEL,
        value_re=rr.CM3_VALUE,
        fallback_re=rr.CM3_VALUE,
    )


def extract_P2(text: str) -> Optional[str]:
    return _x(
        text,
        label_re=rr.P2_LABEL,
        value_re=rr.KW_VALUE,
        fallback_re=rr.KW_VALUE,
    )


def extract_P3(text: str) -> Optional[str]:
    return _x(
        text,
        label_re=rr.P3_LABEL,
        value_re=rr.FUEL_VALUE,
        fallback_re=rr.FUEL_VALUE,
    )


def extract_P5(text: str) -> Optional[str]:
    return _x(text, label_re=rr.P5_LABEL)


def extract_Q(text: str) -> Optional[str]:
    def is_kw_or_kg(s: str) -> bool:
        s = s or ""
        return bool(rr.KW_VALUE.search(s)) or bool(rr.KG_VALUE.search(s))

    return _x(
        text,
        label_re=rr.Q_LABEL,
        validator=is_kw_or_kg,
        fallback_re=None,  # too risky globally
    )


def extract_R(text: str) -> Optional[str]:
    return _x(text, label_re=rr.R_LABEL)


def extract_S1(text: str) -> Optional[str]:
    return _x(
        text,
        label_re=rr.S1_LABEL,
        validator=_is_plain_int_no_leading_zero,
    )


def extract_S2(text: str) -> Optional[str]:
    return _x(
        text,
        label_re=rr.S2_LABEL,
        validator=_is_plain_int_no_leading_zero,
    )


def extract_V9(text: str) -> Optional[str]:
    return _x(
        text,
        label_re=rr.V9_LABEL,
        value_re=rr.V9_VALUE,
    )


def extract_manufacture_year(text: str) -> Optional[str]:
    return _x(
        text,
        label_re=rr.MANUFACTURE_YEAR_LABEL,
        value_re=rr.YEAR_VALUE,
    )


def extract_gearbox_type(text: str) -> Optional[str]:
    return _x(
        text,
        label_re=rr.GEARBOX_TYPE_LABEL,
        value_re=rr.GEARBOX_CODE_VALUE,
    )