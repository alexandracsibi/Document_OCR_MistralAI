from __future__ import annotations
import argparse
import json
from ocr_service.config.mistral_client import get_mistral_client
from ocr_service.core.types import DocType
from ocr_service.pipeline.service import process_document, unify_payload


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc-type", required=True, choices=[d.value for d in DocType])
    ap.add_argument("--image", required=True)
    args = ap.parse_args()

    client = get_mistral_client()
    res = process_document(client=client, doc_type=DocType(args.doc_type), image_path=args.image)

    doc_type = res.doc_type.value
    fields = dict(res.fields or {})
    docno = res.document_number

    data_key, data = unify_payload(doc_type, fields)

    output = {
        "doc_type": doc_type,
        "document_number": docno,
        "is_correct_document": res.is_correct_document,
        "confidence": round(res.confidence, 4),
        data_key: data,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))

    
if __name__ == "__main__":
    main()