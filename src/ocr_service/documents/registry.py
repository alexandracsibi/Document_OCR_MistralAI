from __future__ import annotations
from ocr_service.core.types import DocType
from ocr_service.documents.processors.id_front import IDFrontProcessor
from ocr_service.documents.processors.id_back import IDBackProcessor
from ocr_service.documents.processors.id_old_front import IDOldFrontProcessor
from ocr_service.documents.processors.id_old_back import IDOldBackProcessor
from ocr_service.documents.processors.driving_license import DrivingLicenseProcessor
from ocr_service.documents.processors.address_card import AddressCardProcessor
from ocr_service.documents.processors.passport import PassportProcessor
from ocr_service.documents.processors.registration import RegistrationProcessor
from ocr_service.documents.processors.coc import CocProcessor

PROCESSORS = {
    DocType.ID_FRONT: IDFrontProcessor(),
    DocType.ID_BACK: IDBackProcessor(),
    DocType.ID_OLD_FRONT: IDOldFrontProcessor(),
    DocType.ID_OLD_BACK: IDOldBackProcessor(),
    DocType.DRIVING_LICENSE: DrivingLicenseProcessor(),
    DocType.ADDRESS_CARD: AddressCardProcessor(),
    DocType.PASSPORT: PassportProcessor(),
    DocType.REGISTRATION: RegistrationProcessor(),
    DocType.COC: CocProcessor(),
}

def get_processor(doc_type: DocType):
    return PROCESSORS.get(doc_type)
