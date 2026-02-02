from __future__ import annotations
from typing import Optional

def normalize_id_number(raw: str) -> Optional[str]:
    """
    Target format: 6 digits + 2 uppercase letters.

    Correct common OCR confusions:
      digits part: O->0, I/l/|->1
      letters part: 0->O, 1/l/|->I
    """
    if not raw:
        return None
    
    s = raw.strip().upper().replace(" ", "")

    # NOTE if 2 letter became 1 due to OCR error, cannot fix reliably
    if len(s) != 8:
        return None

    first6 = list(s[:6])
    last2 = list(s[6:])

    # digits part
    for i, ch in enumerate(first6):
        if ch == "O":
            first6[i] = "0"
        elif ch in ("I", "L", "|"):
            first6[i] = "1"
        # lowercase l would already become 'L' by upper()

    digits = "".join(first6)
    if not digits.isdigit():
        return None

    # letters part
    for i, ch in enumerate(last2):
        if ch == "0":
            last2[i] = "O"
        elif ch in ("1", "L", "|"):
            last2[i] = "I"

    letters = "".join(last2)
    if len(letters) != 2 or not letters.isalpha():
        return None

    return digits + letters