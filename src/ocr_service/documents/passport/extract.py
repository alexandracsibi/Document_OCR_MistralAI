from __future__ import annotations

from typing import Optional, Tuple

from ocr_service.core.utils.extract import (
    find_label_idx,
    is_stop_label,
    value_after_colon,
)
from ocr_service.core.utils.ocr_text import next_non_empty, normalize_ocr_line
from ocr_service.core.utils.normalize import parse_dates_iso, normalize_sex
from ocr_service.documents.passport import rules as pr



def _stop_pred(line: str) -> bool:
    return is_stop_label(line or "", pr.STOP_LABELS)


def _strip_dates_from_text(s: str) -> str:
    """
    Remove date tokens discovered by parse_dates_iso() from text.
    """
    if not s:
        return ""
    tmp = s
    for d in parse_dates_iso(tmp):
        tmp = tmp.replace(d, " ")
        tmp = tmp.replace(d.replace("-", "."), " ")
    return normalize_ocr_line(tmp) or ""


def _extract_label_value(
    lines: list[str],
    label_re,
    *,
    value_re=None,
    strip_dates: bool = False,
) -> Optional[str]:
    """
    Label-based extractor:
      - Same-line only if there's a ':' after the label match
      - Otherwise takes next non-empty line if not a stop-label
      - If label line contains '/', treat it as a header row and force next-line
    """
    idx = find_label_idx(lines, label_re)
    if idx is None:
        return None

    label_line = lines[idx]
    m = label_re.search(label_line)
    if not m:
        return None

    v: Optional[str] = None

    # same-line (only "Label: value")
    same = value_after_colon(label_line, start_pos=m.end())
    if same and "/" not in label_line:
        if value_re is None:
            v = same
        else:
            mv = value_re.search(same)
            if mv:
                vv = mv.groupdict().get("value") or (mv.group(mv.lastindex) if mv.lastindex else "")
                v = normalize_ocr_line(vv) or None

    # next-line
    if not v:
        nxt = next_non_empty(lines, idx)
        if nxt and not _stop_pred(nxt):
            if value_re is None:
                v = normalize_ocr_line(nxt) or None
            else:
                mv = value_re.search(nxt)
                if mv:
                    vv = mv.groupdict().get("value") or (mv.group(mv.lastindex) if mv.lastindex else "")
                    v = normalize_ocr_line(vv) or None

    if not v:
        return None

    if strip_dates:
        v2 = _strip_dates_from_text(v)
        return v2 or None

    return v


# ----------------------------
# Non-label fallbacks (value-first)
# ----------------------------

def _find_first_country_code(lines: list[str]) -> Optional[str]:
    for ln in lines[:30]:
        m = pr.COUNTRY_CODE_VALUE.search(ln)
        if m:
            return normalize_ocr_line(m.group("value")) or None
    return None


def _find_document_number_by_value(lines: list[str]) -> Optional[str]:
    for ln in lines:
        if "<<" in ln or ln.startswith("P<"):
            continue
        mv = pr.DOCUMENT_NUMBER_VALUE.fullmatch(ln)
        if mv:
            return normalize_ocr_line(mv.group("value")) or None
    return None


def _find_type_line_idx(lines: list[str]) -> int:
    for i, ln in enumerate(lines[:40]):
        if pr.COUNTRY_CODE_VALUE.search(ln):
            return i
    return 0


def _find_name_by_order(lines: list[str]) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Fallback when labels are missing:
      after the type/country line, values tend to appear as:
        surname (single token alpha)
        given names (alpha + spaces)
        birth name (alpha + spaces) [optional]
        nationality (contains '/...HUNGARIAN')
    """
    start = _find_type_line_idx(lines)

    surname = None
    given = None
    birth_name = None
    nationality = None

    def _letters_only(s: str) -> bool:
        t = (s or "").replace(" ", "").strip()
        return bool(t) and t.isalpha()

    for ln in lines[start : min(len(lines), start + 30)]:
        up = (ln or "").upper()

        if nationality is None and (("HUNGARIAN" in up) or up.startswith("MAGYAR/")) and "/" in (ln or ""):
            nationality = normalize_ocr_line((ln or "").lstrip("#").strip()) or None
            continue

        if surname is None and _letters_only(ln) and " " not in (ln or ""):
            surname = ln
            continue

        if surname and given is None and _letters_only(ln):
            given = ln
            continue

        if surname and given and birth_name is None and _letters_only(ln):
            if "/" not in (ln or ""):
                birth_name = ln
            continue

    return surname, given, birth_name, nationality


def _find_sex_and_birth_place(lines: list[str]) -> Tuple[Optional[str], Optional[str]]:
    for ln in lines:
        m = pr.SEX_RAW_VALUE.search(ln)
        if not m:
            continue
        raw = normalize_ocr_line(m.group("value") or "")
        sex = normalize_sex(raw or "")

        rest = normalize_ocr_line((ln or "").replace(m.group(0), " ", 1)).strip()
        return sex, (rest or None)

    return None, None


def _fallback_passport_dates(text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Passport policy:
      birth_date  = smallest date
      issue_date  = second smallest date
      expiry_date = largest date
    """
    ds = parse_dates_iso(text or "")
    if not ds:
        return None, None, None
    if len(ds) == 1:
        return ds[0], None, ds[0]
    if len(ds) == 2:
        return ds[0], ds[1], ds[1]
    return ds[0], ds[1], ds[-1]


# ----------------------------
# Field extractors
# ----------------------------

def extract_country_code(lines: list[str]) -> Optional[str]:
    v = _extract_label_value(lines, pr.COUNTRY_CODE_LABEL, value_re=pr.COUNTRY_CODE_VALUE)
    return v or _find_first_country_code(lines)


def extract_document_number(lines: list[str]) -> Optional[str]:
    v = _extract_label_value(lines, pr.DOCUMENT_NUMBER_LABEL, value_re=pr.DOCUMENT_NUMBER_VALUE)
    return v or _find_document_number_by_value(lines)


def extract_surname(lines: list[str]) -> Optional[str]:
    v = _extract_label_value(lines, pr.SURNAME_LABEL)
    if v:
        return v
    s, _, _, _ = _find_name_by_order(lines)
    return s


def extract_given_names(lines: list[str]) -> Optional[str]:
    v = _extract_label_value(lines, pr.GIVEN_NAMES_LABEL)
    if v:
        return v
    _, g, _, _ = _find_name_by_order(lines)
    return g


def extract_full_name(lines: list[str]) -> Optional[str]:
    s = extract_surname(lines)
    g = extract_given_names(lines)
    if s and g:
        return normalize_ocr_line(f"{s} {g}") or None
    return s or g


def extract_birth_name(lines: list[str]) -> Optional[str]:
    v = _extract_label_value(lines, pr.BIRTH_NAME_LABEL)
    if v:
        return v

    # Only fallback to order when surname+given labels are missing
    if find_label_idx(lines, pr.SURNAME_LABEL) is not None:
        return None
    if find_label_idx(lines, pr.GIVEN_NAMES_LABEL) is not None:
        return None

    _, _, bn, _ = _find_name_by_order(lines)
    return bn


def extract_nationality(lines: list[str]) -> Optional[str]:

    v = _extract_label_value(lines, pr.NATIONALITY_LABEL)
    if v and ("/" in v or "HUNGARIAN" in v.upper()):
        return v

    for ln in lines:
        ln2 = normalize_ocr_line((ln or "").lstrip("#").strip()) or ""
        up = ln2.upper()
        if ("/" in ln2) and ("HUNGARIAN" in up or up.startswith("MAGYAR/")):
            return ln2 or None

    _, _, _, nat = _find_name_by_order(lines)
    return nat or (v if v and ("/" in v) else None)


def extract_sex(lines: list[str]) -> Optional[str]:
    raw = _extract_label_value(lines, pr.SEX_LABEL, value_re=pr.SEX_RAW_VALUE)
    if raw:
        return normalize_sex(raw or "")
    sex, _ = _find_sex_and_birth_place(lines)
    return sex


def extract_birth_place(lines: list[str]) -> Optional[str]:
    v = _extract_label_value(lines, pr.BIRTH_PLACE_LABEL, strip_dates=True)
    if v:
        parts = v.split()
        if parts and parts[0].upper() in {"N/F", "F/M", "F", "M", "NO", "NŐ", "NÓ", "FERFI", "FÉRFI"}:
            v = " ".join(parts[1:]).strip()
        return normalize_ocr_line(v) or None

    _, place = _find_sex_and_birth_place(lines)
    return (normalize_ocr_line(place) or None) if place else None


# IMPORTANT: for passports we always use min/2nd/max date policy (not label-based)
def extract_birth_date(text: str) -> Optional[str]:
    b, _, _ = _fallback_passport_dates(text)
    return b


def extract_issue_date(text: str) -> Optional[str]:
    _, i, _ = _fallback_passport_dates(text)
    return i


def extract_expiry_date(text: str) -> Optional[str]:
    _, _, e = _fallback_passport_dates(text)
    return e


def extract_issuing_authority(lines: list[str]) -> Optional[str]:
    return _extract_label_value(lines, pr.ISSUING_AUTHORITY_LABEL)
