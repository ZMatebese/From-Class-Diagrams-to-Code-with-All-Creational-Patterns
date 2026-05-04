"""
Creational Pattern 2: Factory Method
=========================================
Pattern: Factory Method
Use Case: Delegate the creation of evidence verifiers to subclasses.
           Each verifier type knows how to create the right verification
           strategy for different document types.

RPL Context:
  Different document types (academic transcripts, employer letters, certificates)
  require different verification workflows. The factory method lets each
  verifier subclass create the correct EvidenceDocument processor.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from abc import ABC, abstractmethod
from src.module_request import EvidenceDocument


class EvidenceProcessor(ABC):
    """Abstract product — defines the interface for processing evidence."""

    def __init__(self, document: EvidenceDocument):
        self._document = document

    @abstractmethod
    def process(self) -> str:
        """Process and verify the document."""
        pass

    @abstractmethod
    def get_verification_notes(self) -> str:
        pass


class AcademicTranscriptProcessor(EvidenceProcessor):
    """Processes academic transcripts from universities or TVET colleges."""

    def process(self) -> str:
        self._document.upload()
        self._document.verify()
        return f"Academic transcript '{self._document.file_name}' verified against NQF registry."

    def get_verification_notes(self) -> str:
        return "Checked institution accreditation, subject equivalence, and NQF level."


class EmployerLetterProcessor(EvidenceProcessor):
    """Processes employer reference letters for work experience RPL."""

    def process(self) -> str:
        self._document.upload()
        self._document.verify()
        return f"Employer letter '{self._document.file_name}' verified via company registration check."

    def get_verification_notes(self) -> str:
        return "Verified company registration number and signatory authority."


class CertificateProcessor(EvidenceProcessor):
    """Processes professional certificates (e.g., CompTIA, AWS, SAICA)."""

    def process(self) -> str:
        self._document.upload()
        self._document.verify()
        return f"Certificate '{self._document.file_name}' verified against issuing body database."

    def get_verification_notes(self) -> str:
        return "Cross-referenced certificate number with issuing body's online portal."


# ── Creator (Factory Method) ──────────────────────────────────────────────────

class EvidenceVerifier(ABC):
    """
    Abstract Creator: declares the factory method that subclasses override
    to create the right EvidenceProcessor.
    """

    @abstractmethod
    def create_processor(self, document: EvidenceDocument) -> EvidenceProcessor:
        """Factory method — subclasses decide which processor to create."""
        pass

    def verify_document(self, document: EvidenceDocument) -> str:
        """
        Template method: uses the factory method to create a processor,
        then runs the verification workflow.
        """
        processor = self.create_processor(document)
        result = processor.process()
        notes = processor.get_verification_notes()
        return f"{result}\nNotes: {notes}"


class AcademicVerifier(EvidenceVerifier):
    """Concrete creator for academic transcripts."""

    def create_processor(self, document: EvidenceDocument) -> EvidenceProcessor:
        return AcademicTranscriptProcessor(document)


class EmployerVerifier(EvidenceVerifier):
    """Concrete creator for employer letters."""

    def create_processor(self, document: EvidenceDocument) -> EvidenceProcessor:
        return EmployerLetterProcessor(document)


class CertificateVerifier(EvidenceVerifier):
    """Concrete creator for professional certificates."""

    def create_processor(self, document: EvidenceDocument) -> EvidenceProcessor:
        return CertificateProcessor(document)


def get_verifier(doc_category: str) -> EvidenceVerifier:
    """Helper to retrieve the correct verifier by category name."""
    verifiers = {
        "transcript": AcademicVerifier(),
        "employer_letter": EmployerVerifier(),
        "certificate": CertificateVerifier(),
    }
    if doc_category not in verifiers:
        raise ValueError(f"Unknown document category: '{doc_category}'")
    return verifiers[doc_category]


# ── Demo ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Factory Method Demo ===\n")

    docs = [
        ("transcript",      EvidenceDocument("D001", "UKZN_Transcript.pdf", "pdf")),
        ("employer_letter",  EvidenceDocument("D002", "EmployerLetter.pdf", "pdf")),
        ("certificate",     EvidenceDocument("D003", "AWS_Cert.pdf", "pdf")),
    ]

    for category, doc in docs:
        verifier = get_verifier(category)
        result = verifier.verify_document(doc)
        print(f"Category: {category}")
        print(result)
        print()
