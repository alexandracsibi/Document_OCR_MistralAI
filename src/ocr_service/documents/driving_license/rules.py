from __future__ import annotations
import re


# Finds EU driving license field anchors anywhere in a line
DL_EU_ANCHOR_ANYWHERE = re.compile(
    r"""
    (?ix)
    (?P<prefix>^|(?<=\s))                       # start or whitespace
    (?P<label>
        4\s*\.?\s*\(?\s*[abcd]\s*\)?            # 4a / 4(a) / 4. a / 4(a)
        |
        [1235]                                 # 1,2,3,5
    )
    (?:
        \s*\.?\s*:                              # require ':' (strong delimiter)
        |
        \s*\.                                  # or require '.' (standard labels)
    )
    """,
    re.VERBOSE | re.IGNORECASE | re.MULTILINE,
)