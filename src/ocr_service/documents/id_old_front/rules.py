from __future__ import annotations
import re

NAME_LABEL = re.compile(
    r"\b(CSAL[AÁ]DI\s+ÉS\s+UT[OÓ]N[EÉ]V|SURNAME\s+AND\s+GIVEN\s+NAME)\b",
    re.IGNORECASE,
)

DOCNO_INLINE = re.compile(
    r"""
    ^\s*
    (?: .*? )?
    \b(
        [OÖ]KM[AÁ]NYAZONOS[IÍ]T[OÓ]
    )\b
    (?:\s*[:.]\s*|\s+)
    (?P<value>[^\r\n]+?)
    \s*$
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)

# 6 digit-ish + 2 letter-ish (pre-normalization)
ID_NUMBER_CANDIDATE = re.compile(r"\b([0-9OIL\|]{6}[A-Z01IL\|]{2})\b", re.IGNORECASE)