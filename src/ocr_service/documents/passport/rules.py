from __future__ import annotations

import re

# ================================
# Labels (HU + EN, as per your mapping)
# ================================

COUNTRY_CODE_LABEL = re.compile(
    r"\b(?:K[OÓ]D|CODE)\b",
    re.IGNORECASE,
)

DOCUMENT_NUMBER_LABEL = re.compile(
    r"\b(?:[ÚU]TLEV[ÉE]LSZ[ÁA]M|PASSPORT\s*(?:NO|NUMBER))\b",
    re.IGNORECASE,
)

SURNAME_LABEL = re.compile(
    r"\b(?:CSAL[AÁ]DI\s+N[EÉ]V|SURNAME)\b",
    re.IGNORECASE,
)

GIVEN_NAMES_LABEL = re.compile(
    r"\b(?:UT[OÓ]N[EÉ]V(?:-?EK)?|GIVEN\s+NAMES?)\b",
    re.IGNORECASE,
)

BIRTH_NAME_LABEL = re.compile(
    r"\b(?:SZ[ÜU]LET[ÉE]SI\s+N[EÉ]V|BIRTH\s+NAME)\b",
    re.IGNORECASE,
)

SEX_LABEL = re.compile(
    r"\b(?:NEM|SEX)\b",
    re.IGNORECASE,
)

BIRTH_DATE_LABEL = re.compile(
    r"\b(?:SZ[ÜU]LET[ÉE]SI\s+ID[ŐO]|DATE\s+OF\s+BIRTH)\b",
    re.IGNORECASE,
)

BIRTH_PLACE_LABEL = re.compile(
    r"\b(?:SZ[ÜU]LET[ÉE]SI\s+HELY|PLACE\s+OF\s+BIRTH)\b",
    re.IGNORECASE,
)

NATIONALITY_LABEL = re.compile(
    r"\b(?:[ÁA]LLAMPOLG[ÁA]RS[ÁA]G|NATIONALITY)\b",
    re.IGNORECASE,
)

ISSUE_DATE_LABEL = re.compile(
    r"\b(?:KI[AÁ]LL[IÍ]T[ÁA]SI\s+D[ÁA]TUM|DATE\s+OF\s+ISSUE)\b",
    re.IGNORECASE,
)

EXPIRY_DATE_LABEL = re.compile(
    r"\b(?:[ÉE]RV[ÉE]NYESS[ÉE]GI\s+ID[ŐO]|DATE\s+OF\s+EXPIRY)\b",
    re.IGNORECASE,
)

ISSUING_AUTHORITY_LABEL = re.compile(
    r"\b(?:KI[AÁ]LL[IÍ]T[OÓ]\s+HAT[OÓ]S[AÁ]G|AUTHORITY)\b",
    re.IGNORECASE,
)

# Values
COUNTRY_CODE_VALUE = re.compile(r"\b(?P<value>[A-Z]{3})\b")

DOCUMENT_NUMBER_VALUE = re.compile(
    r"\b(?P<value>(?=[A-Z0-9]{5,12}\b)(?=.*\d)[A-Z0-9]+)\b",
    re.IGNORECASE,
)

SEX_RAW_VALUE = re.compile(
    r"\b(?P<value>(?:N/F|F/M|[MF]|N[ÓŐO]|NŐ|F[ÉE]RFI|FERFI))\b",
    re.IGNORECASE,
)

STOP_LABELS = (
    COUNTRY_CODE_LABEL,
    DOCUMENT_NUMBER_LABEL,
    SURNAME_LABEL,
    GIVEN_NAMES_LABEL,
    BIRTH_NAME_LABEL,
    SEX_LABEL,
    BIRTH_DATE_LABEL,
    BIRTH_PLACE_LABEL,
    NATIONALITY_LABEL,
    ISSUE_DATE_LABEL,
    EXPIRY_DATE_LABEL,
    ISSUING_AUTHORITY_LABEL,
)
