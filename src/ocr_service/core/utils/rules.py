from __future__ import annotations

import re

# ---------- Dates ----------
# Numeric formats:
# 30 06 1979 / 30.06.1979 / 30-06-1979
# 30  06  1979   or 30.06.1979. or 30-06-1979
DATE_DDMMYYYY = re.compile(r"\b(\d{1,2})\s*[.\-/ ]\s*(\d{1,2})\s*[.\-/ ]\s*(\d{4})\b\.?")

# 1979 06 30 or 1979.06.30.
DATE_YYYYMMDD = re.compile(r"\b(\d{4})\s*[.\-/ ]\s*(\d{1,2})\s*[.\-/ ]\s*(\d{1,2})\b\.?")

# Month-abbrev formats you requested:
# YYYY Júl/Jul DD  (token can contain slash with HU/EN)
# Also allows single token (e.g., "Jul") and variable whitespace.
DATE_YYYY_MON_DD = re.compile(
    r"\b(\d{4})\s+([A-Za-zÁÉÍÓÖŐÚÜŰáéíóöőúüű]{3,}(?:/[A-Za-zÁÉÍÓÖŐÚÜŰáéíóöőúüű]{3,})?)\s+(\d{2})\b"
)

DATE_YYYY_HU_MON_DD = re.compile(
    r"""
    \b
    (\d{4})                  # year
    \s*\.?\s*                # optional dot after year
    ([A-Za-zÁÉÍÓÖŐÚÜŰáéíóöőúüű]+)   # month name (HU)
    \s+
    (\d{1,2})                # day
    \s*\.?                   # optional trailing dot
    \b
    """,
    re.VERBOSE,
)

DATE_DD_MON_YY = re.compile(
    r"\b(\d{1,2})\s*[.\-/ ]\s*([A-Za-zÁÉÍÓÖŐÚÜŰáéíóöőúüű]{3,}(?:/[A-Za-zÁÉÍÓÖŐÚÜŰáéíóöőúüű]{3,})?)\s*[.\-/ ]\s*(\d{2})\b\.?",
    re.IGNORECASE,
)

# Month mapping (HU + EN abbreviations). Keys are normalized to lowercase, accents preserved.
MONTH_MAP = {
    # Jan
    "jan": 1, "jan.": 1, "január": 1, "januar": 1,
    # Feb
    "feb": 2, "feb.": 2, "február": 2, "februar": 2,
    # Mar
    "márc": 3, "márc.": 3, "marc": 3, "marc.": 3, "mar": 3, "mar.": 3, "március": 3, "marcius": 3,
    # Apr
    "ápr": 4, "ápr.": 4, "apr": 4, "apr.": 4, "április": 4, "aprilis": 4,
    # May
    "máj": 5, "máj.": 5, "maj": 5, "maj.": 5, "may": 5, "may.": 5,
    # Jun
    "jún": 6, "jún.": 6, "jun": 6, "jun.": 6, "június": 6, "junius": 6, "june": 6,
    # Jul
    "júl": 7, "júl.": 7, "jul": 7, "jul.": 7, "július": 7, "julius": 7, "july": 7,
    # Aug
    "aug": 8, "aug.": 8, "augusztus": 8, "august": 8,
    # Sep
    "szept": 9, "szept.": 9, "sep": 9, "sep.": 9, "sept": 9, "sept.": 9, "szeptember": 9, "september": 9,
    # Oct
    "okt": 10, "okt.": 10, "oct": 10, "oct.": 10, "október": 10, "oktober": 10, "october": 10,
    # Nov
    "nov": 11, "nov.": 11, "november": 11,
    # Dec
    "dec": 12, "dec.": 12, "dez": 12, "dez.": 12, "december": 12,
}