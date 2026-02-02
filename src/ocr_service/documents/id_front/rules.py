from __future__ import annotations
import re

NAME_LABEL = re.compile(
    r"\b(family\s+name\s+and\s+given\s+name|csal[aá]di\s+[ée]s\s+ut[oó]n[eé]v)\b",
    re.IGNORECASE,
)

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

ID_NUMBER_CANDIDATE = re.compile(r"\b([0-9OIL\|]{6}[A-Z01IL\|]{2})\b", re.IGNORECASE)

NATIONALITY_TOKEN = re.compile(r"\b(HUN|HU[NM]|[A-Z]{3})\b", re.IGNORECASE)

SEX_TOKEN = re.compile(r"\b(N/F|F/M|NŐ|NO|N|FÉRFI|FERFI|F|M)\b", re.IGNORECASE)