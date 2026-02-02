from __future__ import annotations

import re

LABEL_TOKEN = r"(?:[A-Z](?:\.\d+)?|\d+(?:\.\d+)*|\(\d+\))"

# single-letter, line-leading labels (allow optional trailing dot)
A_LABEL = re.compile(r"(?im)(?<![A-Z0-9])A\.?(?=\s|$)")
B_LABEL = re.compile(r"(?im)(?<![A-Z0-9])B\.?(?=\s|$)")
E_LABEL = re.compile(r"(?im)(?<![A-Z0-9])E\.?(?=\s|$)")
G_LABEL = re.compile(r"(?im)(?<![A-Z0-9])G\.?(?=\s|$)")
H_LABEL = re.compile(r"(?im)(?<![A-Z0-9])H\.?(?=\s|$)")
I_LABEL = re.compile(r"(?im)(?<![A-Z0-9])I\.?(?=\s|$)")
J_LABEL = re.compile(r"(?im)(?<![A-Z0-9])J\.?(?=\s|$)")
K_LABEL = re.compile(r"(?im)(?<![A-Z0-9])K\.?(?=\s|$)")
O_LABEL = re.compile(r"(?im)(?<![A-Z0-9])O\.?(?=\s|$)")
Q_LABEL = re.compile(r"(?im)(?<![A-Z0-9])Q\.?(?=\s|$)")
R_LABEL = re.compile(r"(?im)(?<![A-Z0-9])R\.?(?=\s|$)")

# O-block sublabels (OCR often reads O as 0)
O1_LABEL = re.compile(r"(?im)(?<![A-Z0-9])[O0]\s*\.?\s*1(?=\s|$)")
O2_LABEL = re.compile(r"(?im)(?<![A-Z0-9])[O0]\s*\.?\s*2(?=\s|$)")

PAREN_0_LABEL = re.compile(r"(?im)(?<![A-Z0-9])\(\s*0\s*\)(?=\s|$)")
PAREN_1_LABEL = re.compile(r"(?im)(?<![A-Z0-9])\(\s*1\s*\)(?=\s|$)")
PAREN_2_LABEL = re.compile(r"(?im)(?<![A-Z0-9])\(\s*2\s*\)(?=\s|$)")
PAREN_3_LABEL = re.compile(r"(?im)(?<![A-Z0-9])\(\s*3\s*\)(?=\s|$)")

# "1" misread for I: standalone 1 token, NOT preceded by ". " (so it won't match P.1), followed by digit
I_ALIAS_1_LABEL = re.compile(
    r"(?im)(?:(?<=^)|(?<=\s))1(?!\d)\.?(?=\s*\d)"
)

# "1" misread for J: standalone 1 token, NOT preceded by ". ", followed by category like M1/N1 (letter+digit)
J_ALIAS_1_LABEL = re.compile(
    r"(?im)(?:(?<=^)|(?<=\s))(?<!\.)(?<!\.\s)1\.?(?=\s*[A-Z]\s*\d)"
)


# dotted-number labels: accept "F.1", "F1", "F . 1" (dot optional, spaces flexible), inline-capable
D1_LABEL = re.compile(r"(?im)(?<![A-Z0-9])D\s*\.?\s*1(?=\s|$)")
D2_LABEL = re.compile(r"(?im)(?<![A-Z0-9])D\s*\.?\s*2(?=\s|$)")
D3_LABEL = re.compile(r"(?im)(?<![A-Z0-9])D\s*\.?\s*3(?=\s|$)")

F1_LABEL = re.compile(r"(?im)(?<![A-Z0-9])F\s*\.?\s*1(?=\s|$)")

P1_LABEL = re.compile(r"(?im)(?<![A-Z0-9])P\s*\.?\s*1(?=\s|$)")
P2_LABEL = re.compile(r"(?im)(?<![A-Z0-9])P\s*\.?\s*2(?=\s|$)")
P3_LABEL = re.compile(r"(?im)(?<![A-Z0-9])P\s*\.?\s*3(?=\s|$)")
P5_LABEL = re.compile(r"(?im)(?<![A-Z0-9])P\s*\.?\s*5(?=\s|$)")

S1_LABEL = re.compile(r"(?im)(?<![A-Z0-9])S\s*\.?\s*1(?=\s|$)")
S2_LABEL = re.compile(r"(?im)(?<![A-Z0-9])S\s*\.?\s*2(?=\s|$)")

V9_LABEL = re.compile(r"(?im)(?<![A-Z0-9])V\s*\.?\s*9(?=\s|$)")

# ---------------------------
# Special Hungarian textual labels
# ---------------------------

MANUFACTURE_YEAR_LABEL = re.compile(
    r"(?im)^\s*GY[AÁ]RT[AÁ]SI\s+[EÉ]V\s*:\s*"
)
GEARBOX_TYPE_LABEL = re.compile(
    r"(?im)^\s*SEBESS[EÉ]GV[AÁ]LT[OÓŐ]\s+FAJT[AÁ]JA(?:\s*\([^)]*\))?\s*:\s*"
)

# ---------------------------
# Value patterns (keep them simple; extractor does the heavy lifting)
# ---------------------------
# TODO: later in validate.py

# Registration document number: 2 letters + 5 digits (often printed twice)
# Tolerate OCR confusions:
#   - In the 2-char prefix: "1" may appear instead of I/J, and "0" instead of O.
#   - In the 5-char digit block: "O" may appear instead of 0 (and optionally I/J instead of 1).
DOCUMENT_NUMBER_VALUE = re.compile(r"(?i)\b([A-Z10]{2})([0-9OIJ]{5})\b")

# VIN: typically 17 chars, no I,O,Q; OCR may include them
VIN_VALUE = re.compile(r"(?i)(?<![A-Z0-9])([A-Z0-9]{17})(?![A-Z0-9])")

# HU plate for now: 3-4 letters + 3 digits
PLATE_VALUE = re.compile(
    r"(?i)(?<![A-Z0-9])"                # not glued to alnum on the left
    r"([A-Z01]{3,4})"                   # "letters" zone, allow OCR 0/1 too
    r"([0-9OIJLl]{3})"                  # "digits" zone, allow O and I/J/L/l as OCR for 0/1
    r"(?![A-Z0-9])"                     # not glued to alnum on the right
)

# Weights / units
KG_VALUE = re.compile(r"(?i)\b(\d{2,6})\s*KG\b")

# Engine cc and power
CM3_VALUE = re.compile(r"(?i)\b(\d{2,5})\s*CM3\b")
KW_VALUE  = re.compile(r"(?i)\b(\d{1,4})\s*KW\b")

# Fuel type words (Hungarian common)
FUEL_VALUE = re.compile(r"(?i)\b(BENZIN|DÍZEL|DIESEL|ELEKTROMOS|HIBRID|GÁZ|LPG|CNG)\b")

YEAR_VALUE = re.compile(r"\b(19\d{2}|20\d{2})\b")

GEARBOX_CODE_VALUE = re.compile(r"(?i)\b(\d{1,3})\b")

V9_VALUE = re.compile(r"(?i)\b([0-9]{1,3})\b")

STOP_LABELS = [
    A_LABEL, B_LABEL,
    D1_LABEL, D2_LABEL, D3_LABEL,
    E_LABEL,
    F1_LABEL, G_LABEL,
    H_LABEL, I_LABEL, J_LABEL,
    K_LABEL,
    O_LABEL,
    P1_LABEL, P2_LABEL, P3_LABEL, P5_LABEL,
    Q_LABEL, R_LABEL,
    S1_LABEL, S2_LABEL,
    V9_LABEL,
    MANUFACTURE_YEAR_LABEL,
    GEARBOX_TYPE_LABEL,
]

STOP_O_BLOCK_END = [
    Q_LABEL, G_LABEL, R_LABEL,
    S1_LABEL, S2_LABEL,
    V9_LABEL,
    MANUFACTURE_YEAR_LABEL,
    GEARBOX_TYPE_LABEL,
]