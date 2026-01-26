from __future__ import annotations

from typing import Any, Dict, Optional

from ocr_service.core.types import OCRResult
from ocr_service.core.utils.text import (
    split_lines,
    extract_inline_value,
    extract_nextline_value,
)
from ocr_service.core.utils.normalization import (
    ddmmyy_from_iso,
    extract_dates,
    normalize_sex,
    normalize_id_number,
)
from ocr_service.core.utils import patterns
from ocr_service.documents.base import DocumentProcessor
from ocr_service.documents.schemas import id_front


class IDFrontProcessor(DocumentProcessor):
    @property
    def doc_type(self) -> str:
        return "ID_FRONT"

    def extract_fields(self, ocr: OCRResult) -> Dict[str, Any]:
        text = ocr.text or ""
        lines = split_lines(text)

        fields = id_front.empty()

        # 1) full_name (label -> next non-empty line)
        fields["full_name"] = extract_nextline_value(lines, patterns.NAME_LABEL)

        # 2) sex: KV first, fallback to global token search
        sex_rhs = extract_inline_value(text, patterns.SEX_INLINE)
        if not sex_rhs:
            m_sex = patterns.SEX_TOKEN.search(text)
            sex_rhs = m_sex.group(0) if m_sex else None
        fields["sex"] = normalize_sex(sex_rhs or "")

        # 3) nationality: KV first, fallback token scan
        nat_rhs = extract_inline_value(text, patterns.NATIONALITY_INLINE)
        if nat_rhs:
            token = nat_rhs.split()[0].strip(".,;:")
            fields["nationality"] = token.upper()
        else:
            m_nat = patterns.NATIONALITY_TOKEN.search(text)
            fields["nationality"] = m_nat.group(1).upper() if m_nat else None

        # 4) dates (DD MM YYYY only; earliest=birth, latest=expiry)
        dates = extract_dates(text)
        if dates:
            fields["birth_date"] = dates[0]
        if len(dates) >= 2:
            fields["expiry_date"] = dates[-1]

        dob_ddmmyy = ddmmyy_from_iso(fields["birth_date"])
        doe_ddmmyy = ddmmyy_from_iso(fields["expiry_date"])

        def _reject_date_derived(norm: str) -> bool:
            first6 = norm[:6]
            return (dob_ddmmyy is not None and first6 == dob_ddmmyy) or (doe_ddmmyy is not None and first6 == doe_ddmmyy)


        # 5) document_number (prefer inline label; fallback to global)
        docno_rhs = extract_inline_value(text, patterns.DOCNO_INLINE)
        docno: Optional[str] = None
        if docno_rhs:
            token = docno_rhs.split()[0].strip(".,;:")
            docno = normalize_id_number(token)
            #print(f"Found inline this is it: {docno}")

        if not docno:
            #print("Falling back to global scan for ID number")
            compact = text.replace(" ", "")
            for m in patterns.ID_NUMBER_CANDIDATE.finditer(compact):
                #print("  Candidate:", m.group(1))
                norm = normalize_id_number(m.group(1))
                #print("    Normalized to:", norm)
                if not norm:
                    continue
                    
                if _reject_date_derived(norm):
                    #print("    Rejected: matches DOB/DOE")
                    continue
                    
                docno = norm
                break

        fields["document_number"] = docno

        return {k: fields.get(k) for k in id_front.FIELDS}

