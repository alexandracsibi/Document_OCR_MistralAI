from __future__ import annotations
import re

FULL_NAME_LABEL = re.compile(
    r"\bCSAL[AÁ]DI\s+ÉS\s+UT[OÓ]N[EÉ]V\b",
    re.IGNORECASE,
)

BIRTH_PLACE_DATE_LABEL = re.compile(
    r"\bSZ[UÜ]LET[EÉ]SI\s+HELY[, ]*ID[ŐO]\b",
    re.IGNORECASE,
)

MOTHERS_NAME_LABEL = re.compile(
    r"\bANYJA\s+NEVE\b",
    re.IGNORECASE,
)

PERMANENT_ADDRESS_LABEL = re.compile(
    r"\bLAK[OÓ]HELY\b",
    re.IGNORECASE,
)

TEMPORARY_ADDRESS_LABEL = re.compile(
    r"\bTART[OÓ]ZKOD[AÁ]SI\s+HELY\b",
    re.IGNORECASE,
)

REPORTING_TIME_LABEL = re.compile(
    r"\bBEJELENT[ÉE]SI\s+ID[ŐO]\b",
    re.IGNORECASE,
)

VALIDITY_LABEL = re.compile(
    r"\b[ÉE]RV[ÉE]NYESS[ÉE]GI\s+IDEJE\b",
    re.IGNORECASE,
)

ISSUING_AUTHORITY_LABEL = re.compile(
    r"\bKI[AÁ]LL[IÍ]T[OÓ]\s+HAT[OÓ]S[AÁ]G\b",
    re.IGNORECASE,
)

TITLE_LABEL = re.compile(r"(?i)\bLAKC[IÍ]MET\s+IGAZOL[OÓ]\b")

# Address card "document number": 6 digits + optional space + 2 letters
# OCR: digits may contain O/I/J/L as 0/1; letters may contain 0/1.
DOCNO_VALUE = re.compile(
    r"(?i)\b([0-9OIJLl]{6})\s?([A-Z01]{2})\b"
)

DOCNO_CANON = re.compile(r"^\d{6}\s[A-Z]{2}$")

FOREIGN_ADDRESS_VALUE = re.compile(r"(?i)^\s*K[ÜU]LF[ÖO]LDI\s+C[ÍI]M\s*$")

HUNGARY_WORD = re.compile(r"(?i)\bMAGYARORSZ[AÁ]G\b")

# ================================
# Stop-label set
# Used to reject "value" lines that are actually labels
# ================================

STOP_LABELS = (
    FULL_NAME_LABEL,
    BIRTH_PLACE_DATE_LABEL,
    MOTHERS_NAME_LABEL,
    PERMANENT_ADDRESS_LABEL,
    TEMPORARY_ADDRESS_LABEL,
    REPORTING_TIME_LABEL,
    VALIDITY_LABEL,
    ISSUING_AUTHORITY_LABEL,
)

