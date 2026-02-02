from __future__ import annotations

from typing import Dict, Optional, Tuple, List

from ocr_service.core.utils.ocr_text import split_lines, normalize_ocr_line
from ocr_service.core.utils.normalize import parse_dates_iso
from ocr_service.documents.driving_license import rules as rr


def _normalize_dl_label(raw: str) -> str:
    """
    Normalize EU DL label variants:
      "4a", "4(a)", "4. a", "4.(a)" -> "4a"
      "1." -> "1"
    """
    s = (raw or "").lower()
    s = s.replace("(", "").replace(")", "")
    s = s.replace(".", "")
    s = "".join(s.split())  # remove whitespace
    return s


def _extract_anchor_pairs_from_line(line: str) -> List[Tuple[str, str]]:
    """
    Extract multiple (label, value) pairs from a single line using DL_EU_ANCHOR_ANYWHERE.

    Example:
      "4a. 03.07.2020 4c. SRPCIV HARGHITA"
      -> [("4a","03.07.2020"), ("4c","SRPCIV HARGHITA")]
    """
    s = normalize_ocr_line(line)
    if not s:
        return []

    matches = list(rr.DL_EU_ANCHOR_ANYWHERE.finditer(s))
    if not matches:
        return []

    pairs: List[Tuple[str, str]] = []
    for i, m in enumerate(matches):
        raw_label = m.group("label")
        label = _normalize_dl_label(raw_label)

        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(s)
        value = s[start:end].strip()

        # trim typical separators/noise
        value = value.strip(" .:-–—·|")
        value = " ".join(value.split())

        if value:
            pairs.append((label, value))

    return pairs


def collect_kv(text: str) -> Dict[str, str]:
    """
    Collect first-seen value per label across all lines.
    Labels are normalized: '4(a)' -> '4a', '1.' -> '1', etc.
    """
    kv: Dict[str, str] = {}
    for ln in split_lines(text or ""):
        for label, value in _extract_anchor_pairs_from_line(ln):
            kv.setdefault(label, value)

    return kv


def extract_full_name(kv: Dict[str, str]) -> Optional[str]:
    """
    EU DL:
      1 = surname
      2 = given names
    Must have both; otherwise return None.
    """
    surname = (kv.get("1") or "").strip()
    given = (kv.get("2") or "").strip()

    if not surname or not given:
        return None

    return f"{surname} {given}"



def extract_birth_date_and_place(kv: Dict[str, str]) -> Tuple[Optional[str], Optional[str]]:
    """
    EU DL field 3: date and place of birth.
    Value can be like: "06.04.2001 MIERCUREA CIUC, HR"
    We'll parse first ISO date from it and return remaining tail as birth_place.
    """
    raw = kv.get("3")
    if not raw:
        return None, None

    ds = parse_dates_iso(raw)
    if not ds:
        return None, raw

    birth_date = ds[0]

    # remove obvious date token(s) from raw heuristically
    # (later you can do robust regex substitution with date regexes if you want)
    tokens = raw.split()
    kept: List[str] = []
    for t in tokens:
        if any(ch.isdigit() for ch in t) and any(sep in t for sep in (".", "-", "/")):
            continue
        kept.append(t)

    birth_place = " ".join(kept).strip() or None
    return birth_date, birth_place


def extract_issue_date(kv: Dict[str, str]) -> Optional[str]:
    """
    EU DL field 4a: date of issue.
    """
    raw = kv.get("4a")
    if not raw:
        return None
    ds = parse_dates_iso(raw)
    return ds[0] if ds else None


def extract_expiry_date(kv: Dict[str, str]) -> Optional[str]:
    """
    EU DL field 4b: date of expiry.
    """
    raw = kv.get("4b")
    if not raw:
        return None
    ds = parse_dates_iso(raw)
    return ds[0] if ds else None


def extract_issuing_authority(kv: Dict[str, str]) -> Optional[str]:
    """
    EU DL field 4c: issuing authority.
    """
    return kv.get("4c")


def extract_licence_number(kv: Dict[str, str]) -> Optional[str]:
    """
    EU DL field 5: licence number.
    """
    raw = kv.get("5")
    if not raw:
        return None
    token = raw.split()[0].strip(".,;:")
    return token or None
