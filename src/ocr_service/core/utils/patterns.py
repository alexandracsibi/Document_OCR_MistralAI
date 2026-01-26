from __future__ import annotations

import re

# -------------------------------------------------------------
# ------------------------ ID_FRONT ---------------------------
# -------------------------------------------------------------


# ---------- Label-first (KV) regexes: ENGLISH FIRST ----------
# Family name and given name:
NAME_LABEL = re.compile(
    r"\b(family\s+name\s+and\s+given\s+name|csal[aá]di\s+[ée]s\s+ut[oó]n[eé]v)\b",
    re.IGNORECASE,
)

# Allow ':' or '.' or plain whitespace and capture value until end-of-line

SEX_INLINE = re.compile(
    r"""
    \b(SEX|NEM)\b
    (?:\s*[:.]\s*|\s+)
    (?P<value>[^\r\n]+?)
    \s*$
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)

NATIONALITY_INLINE = re.compile(
    r"""
    \b(NATIONALITY|[AÁ]LLAMPOLG[AÁ]RS[AÁ]G)\b
    (?:\s*[:.]\s*|\s+)
    (?P<value>[^\r\n]+?)
    \s*$
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)

DOCNO_INLINE = re.compile(
    r"""
    ^\s*
    (?: .*? )?
    \b(
        DOC\.?\s*NO\.? |
        DOC\s*NO |
        [OÖ]KM[AÁ]NYAZONOS[IÍ]T[OÓ]
    )\b
    (?:\s*/\s*(?:DOC\.?\s*NO\.?|DOC\s*NO))?
    (?:\s*[:.]\s*|\s+)
    (?P<value>[^\r\n]+?)
    \s*$
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)

# ---------- Global candidates ----------
# 6 digit-ish + 2 letter-ish (pre-normalization)
ID_NUMBER_CANDIDATE = re.compile(r"\b([0-9OIL\|]{6}[A-Z01IL\|]{2})\b", re.IGNORECASE)

# Nationality tokens (will force to HUN, but capture OCR token for warnings)
NATIONALITY_TOKEN = re.compile(r"\b(HUN|MAGYAR|HU[NM]|[A-Z]{3})\b", re.IGNORECASE)

# Sex token candidates (we normalize to NŐ / FÉRFI)
SEX_TOKEN = re.compile(r"\b(N/F|F/M|NŐ|NO|N|FÉRFI|FERFI|F|M)\b", re.IGNORECASE)

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


# -------------------------------------------------------------
# ------------------------ ID_BACK ----------------------------
# -------------------------------------------------------------


BIRTH_PLACE_LABEL = re.compile(
    r"\b(PLACE\s+OF\s+BIRTH|SZ[UÜ]LET[EÉ]SI\s+HELY)\b",
    re.IGNORECASE,
)

BIRTH_NAME_LABEL = re.compile(
    r"\b(FAMILY\s+NAME\s+AND\s+GIVEN\s+NAME\s+AT\s+BIRTH|SZ[UÜ]LET[EÉ]SI\s+CSAL[AÁ]DI\s+UT[OÓ]N[EÉ]V)\b",
    re.IGNORECASE,
)

MOTHERS_NAME_LABEL = re.compile(
    r"\b(MOTHER'?S\s+MAIDEN\s+NAME|ANYJA\s+SZ[UÜ]LET[EÉ]SI\s+NEVE)\b",
    re.IGNORECASE,
)

ORIGIN_PLACE_LABEL = re.compile(
    r"\b(PLACE\s+OF\s+ORIGIN|SZ[AÁ]RMAZ[AÁ]SI\s+HELY)\b",
    re.IGNORECASE,
)

ISSUING_AUTHORITY_INLINE = re.compile(
    r"""
    \b(ISSUING\s+AUTHORITY|KI[AÁ]L[IÍ]T[OÓ]\s+HAT[OÓ]S[AÁ]G)\b
    (?:\s*[:.]\s*|\s+)
    (?P<value>[^\r\n]+?)
    \s*$
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)

# -------------------------------------------------------------
# ------------------- DRIVING_LICENSE -------------------------
# -------------------------------------------------------------

# Finds EU driving license field anchors anywhere in a line, e.g.:
# "4a. 03.07.2020 4c. SRPCIV HARGHITA"
# "4 (b) 03.07.2030 4(d) 6010406190449"
# "1. CSIBI"
DL_EU_ANCHOR_ANYWHERE = re.compile(
    r"""
    (?P<prefix>^|(?<=\s))                 # start OR preceded by whitespace
    (?P<label>
        4\s*\(?\s*[abcd]\s*\)?\.?         # 4a / 4(a) / 4a. / 4(a). variants
        |
        [1235]                            # 1,2,3,5
    )
    \s*\.?\s*:?\s*                         # optional '.' and/or ':' and trailing spaces
    """,
    re.IGNORECASE | re.VERBOSE,
)