from __future__ import annotations
import re

# --- Inline label:value patterns (preferred when OCR keeps them on one line) ---

BIRTH_NAME_INLINE = re.compile(
    r"""
    \b(SZ[UÜ]LET[EÉ]SI\s+N[ÉE]V|BIRTH\s+NAME)\b
    \s*[:.]\s*
    (?P<value>[^\r\n]+?)
    \s*$
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)

BIRTH_PLACE_INLINE = re.compile(
    r"""
    \b(SZ[UÜ]LET[EÉ]SI\s+HELY|PLACE\s+OF\s+BIRTH)\b
    \s*[:.]\s*
    (?P<value>[^\r\n]+?)
    \s*$
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)

BIRTH_DATE_INLINE = re.compile(
    r"""
    \b(SZ[UÜ]LET[EÉ]SI\s+ID[ŐO]|DATE\s+OF\s+BIRTH)\b
    \s*[:.]\s*
    (?P<value>[^\r\n]+?)
    \s*$
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)

MOTHERS_NAME_INLINE = re.compile(
    r"""
    \b(ANYJA\s+SZ[UÜ]LET[EÉ]SI\s+NEVE|MOTHER'?S\s+NAME)\b
    \s*[:.]\s*
    (?P<value>[^\r\n]+?)
    \s*$
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)

SEX_INLINE = re.compile(
    r"""
    \b(NEME?|SEX)\b
    \s*[:.]\s*
    (?P<value>[^\r\n]+?)
    \s*$
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)

# --- Label-only patterns (fallback for label -> next-line layouts) ---

BIRTH_NAME_LABEL = re.compile(
    r"\b(SZ[UÜ]LET[EÉ]SI\s+N[ÉE]V|BIRTH\s+NAME)\b",
    re.IGNORECASE,
)

BIRTH_PLACE_LABEL = re.compile(
    r"\b(SZ[UÜ]LET[EÉ]SI\s+HELY|PLACE\s+OF\s+BIRTH)\b",
    re.IGNORECASE,
)

BIRTH_DATE_LABEL = re.compile(
    r"\b(SZ[UÜ]LET[EÉ]SI\s+ID[ŐO]|DATE\s+OF\s+BIRTH)\b",
    re.IGNORECASE,
)

MOTHERS_NAME_LABEL = re.compile(
    r"\b(ANYJA\s+SZ[UÜ]LET[EÉ]SI\s+NEVE|MOTHER'?S\s+NAME)\b",
    re.IGNORECASE,
)

SEX_LABEL = re.compile(
    r"\b(NEME?|SEX)\b",
    re.IGNORECASE,
)

# --- Always-inline fields ---

NATIONALITY_INLINE = re.compile(
    r"""
    \b([AÁ]LLAMPOLG[AÁ]RS[AÁ]G|NATIONALITY)\b
    (?:\s*[:.]\s*|\s+)
    (?P<value>[^\r\n]+?)
    \s*$
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)

ISSUING_AUTHORITY_INLINE = re.compile(
    r"""
    \b(KI[ÁA]LL[IÍ]T[ÓO]\s+HAT[ÓO]S[ÁA]G|AUTHORITY)\b
    (?:\s*[:.]\s*|\s+)
    (?P<value>[^\r\n]+?)
    \s*$
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)


STOP_LABELS = [
    BIRTH_NAME_LABEL,
    BIRTH_PLACE_LABEL,
    BIRTH_DATE_LABEL,
    MOTHERS_NAME_LABEL,
    SEX_LABEL,
]