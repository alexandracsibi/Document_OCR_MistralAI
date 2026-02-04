from __future__ import annotations
import re

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

ID_NUMBER_CANDIDATE = re.compile(r"\b([0-9OIL\|]{6}[A-Z01IL\|]{2})\b", re.IGNORECASE)

STOP_LABELS = [
    BIRTH_PLACE_LABEL,
    BIRTH_NAME_LABEL,
    MOTHERS_NAME_LABEL,
    ORIGIN_PLACE_LABEL,
]