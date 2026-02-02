from __future__ import annotations

from typing import Dict, Optional, Type

from ocr_service.core.types import DocType
from ocr_service.documents.base import DocumentProcessor

from ocr_service.documents.id_front.processor import IDFrontProcessor
from ocr_service.documents.id_back.processor import IDBackProcessor
from ocr_service.documents.id_old_front.processor import IDOldFrontProcessor
from ocr_service.documents.id_old_back.processor import IDOldBackProcessor
from ocr_service.documents.driving_license.processor import DrivingLicenseProcessor
from ocr_service.documents.address_card.processor import AddressCardProcessor
from ocr_service.documents.passport.processor import PassportProcessor
from ocr_service.documents.registration.processor import RegistrationProcessor
# from ocr_service.documents.coc.processor import CocProcessor


PROCESSOR_CLASSES: Dict[DocType, Type[DocumentProcessor]] = {
    DocType.ID_FRONT: IDFrontProcessor,
    DocType.ID_BACK: IDBackProcessor,
    DocType.ID_OLD_FRONT: IDOldFrontProcessor,
    DocType.ID_OLD_BACK: IDOldBackProcessor,
    DocType.DRIVING_LICENSE: DrivingLicenseProcessor,
    DocType.ADDRESS_CARD: AddressCardProcessor,
    DocType.PASSPORT: PassportProcessor,
    DocType.REGISTRATION: RegistrationProcessor,
    # DocType.COC: CocProcessor,
}


def get_processor(doc_type: DocType) -> Optional[DocumentProcessor]:
    cls = PROCESSOR_CLASSES.get(doc_type)
    return cls() if cls else None
