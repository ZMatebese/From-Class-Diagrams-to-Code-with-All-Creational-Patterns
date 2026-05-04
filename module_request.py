"""
RPL System - EvidenceDocument and ModuleRequest Classes
"""
from datetime import datetime
from typing import List, Optional


class EvidenceDocument:
    """Represents a document uploaded as evidence for a module request."""

    ALLOWED_FILE_TYPES = {"pdf", "docx", "jpg", "png", "jpeg"}

    def __init__(self, document_id: str, file_name: str, file_type: str, file_url: str = ""):
        if file_type.lower() not in self.ALLOWED_FILE_TYPES:
            raise ValueError(f"File type '{file_type}' is not allowed.")
        self.__document_id = document_id
        self.__file_name = file_name
        self.__file_type = file_type.lower()
        self.__upload_date: Optional[datetime] = None
        self.__verification_status: str = "Pending"
        self.__file_url: str = file_url
        self.__rejection_reason: str = ""

    # Getters
    @property
    def document_id(self): return self.__document_id
    @property
    def file_name(self): return self.__file_name
    @property
    def file_type(self): return self.__file_type
    @property
    def upload_date(self): return self.__upload_date
    @property
    def verification_status(self): return self.__verification_status
    @property
    def file_url(self): return self.__file_url
    @property
    def rejection_reason(self): return self.__rejection_reason

    def upload(self) -> bool:
        """Simulate uploading the document."""
        if not self.__file_name:
            return False
        self.__upload_date = datetime.now()
        self.__verification_status = "Uploaded"
        return True

    def verify(self) -> None:
        """Mark document as verified by an assessor."""
        if self.__verification_status == "Uploaded":
            self.__verification_status = "Verified"
        else:
            raise ValueError("Document must be uploaded before verification.")

    def reject(self, reason: str) -> None:
        """Mark document as rejected with a reason."""
        self.__verification_status = "Rejected"
        self.__rejection_reason = reason

    def get_file_metadata(self) -> dict:
        return {
            "document_id": self.__document_id,
            "file_name": self.__file_name,
            "file_type": self.__file_type,
            "upload_date": str(self.__upload_date),
            "verification_status": self.__verification_status,
            "file_url": self.__file_url,
        }

    def __repr__(self):
        return (f"EvidenceDocument(id={self.__document_id}, "
                f"file={self.__file_name}, status={self.__verification_status})")


class ModuleRequest:
    """Represents a request to earn credit for one academic module via RPL."""

    VALID_STATUSES = {"Pending", "UnderReview", "Approved", "Rejected", "MoreInfoRequired"}

    def __init__(self, module_request_id: str, module_code: str,
                 module_name: str, credits: int, justification: str = ""):
        if credits <= 0:
            raise ValueError("Credits must be a positive integer.")
        self.__module_request_id = module_request_id
        self.__module_code = module_code
        self.__module_name = module_name
        self.__credits = credits
        self.__request_status = "Pending"
        self.__justification = justification
        self.__evidence_documents: List[EvidenceDocument] = []

    # Getters
    @property
    def module_request_id(self): return self.__module_request_id
    @property
    def module_code(self): return self.__module_code
    @property
    def module_name(self): return self.__module_name
    @property
    def credits(self): return self.__credits
    @property
    def request_status(self): return self.__request_status
    @property
    def justification(self): return self.__justification
    @property
    def evidence_documents(self): return list(self.__evidence_documents)

    def attach_evidence(self, doc: EvidenceDocument) -> None:
        """Attach an evidence document to this module request."""
        if not isinstance(doc, EvidenceDocument):
            raise TypeError("Expected an EvidenceDocument instance.")
        self.__evidence_documents.append(doc)

    def update_request_status(self, status: str) -> None:
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}")
        self.__request_status = status

    def get_credits(self) -> int:
        return self.__credits

    def get_justification(self) -> str:
        return self.__justification

    def has_verified_evidence(self) -> bool:
        """BR-003: Check if at least one evidence document is verified."""
        return any(
            doc.verification_status == "Verified"
            for doc in self.__evidence_documents
        )

    def __repr__(self):
        return (f"ModuleRequest(id={self.__module_request_id}, "
                f"module={self.__module_code}, credits={self.__credits}, "
                f"status={self.__request_status})")
