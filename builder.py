"""
Creational Pattern 4: Builder
===================================
Pattern: Builder
Use Case: Construct complex RPLApplication objects step by step,
           allowing different configurations without a telescoping constructor.

RPL Context:
  An RPL application is complex — it can have multiple module requests,
  each with their own evidence documents and justifications. The builder
  provides a fluent API to assemble an application step by step,
  validating at the final build() stage.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rpl_application import RPLApplication
from src.module_request import ModuleRequest, EvidenceDocument


class RPLApplicationBuilder:
    """
    Builder: constructs an RPLApplication with any combination of
    module requests and evidence, step by step.
    """

    def __init__(self, application_id: str, student_id: str):
        self._application_id = application_id
        self._student_id = student_id
        self._module_requests: list = []
        self._evidence_map: dict = {}   # module_request_id -> [EvidenceDocument]

    def add_module_request(self, module_request_id: str, module_code: str,
                           module_name: str, credits: int,
                           justification: str = "") -> "RPLApplicationBuilder":
        """Add a module request to the application being built."""
        mr = ModuleRequest(module_request_id, module_code, module_name,
                           credits, justification)
        self._module_requests.append(mr)
        self._evidence_map[module_request_id] = []
        return self  # fluent interface

    def add_evidence(self, module_request_id: str, document_id: str,
                     file_name: str, file_type: str,
                     file_url: str = "") -> "RPLApplicationBuilder":
        """Attach an evidence document to a previously added module request."""
        if module_request_id not in self._evidence_map:
            raise ValueError(
                f"No module request '{module_request_id}' found. "
                "Add the module request before attaching evidence."
            )
        doc = EvidenceDocument(document_id, file_name, file_type, file_url)
        doc.upload()
        self._evidence_map[module_request_id].append(doc)
        return self

    def build(self) -> RPLApplication:
        """
        Validate and assemble the final RPLApplication.
        Enforces BR-002: at least one module request required.
        """
        if not self._module_requests:
            raise ValueError(
                "BR-002: Cannot build an application with no module requests."
            )

        application = RPLApplication(self._application_id, self._student_id)

        for mr in self._module_requests:
            # Attach evidence to each module request
            for doc in self._evidence_map.get(mr.module_request_id, []):
                mr.attach_evidence(doc)
            application.add_module_request(mr)

        return application

    def reset(self) -> "RPLApplicationBuilder":
        """Reset the builder to start fresh."""
        self._module_requests = []
        self._evidence_map = {}
        return self


# ── Director ──────────────────────────────────────────────────────────────────

class RPLApplicationDirector:
    """
    Director: knows how to build common application configurations
    using the builder. Clients can use the director or the builder directly.
    """

    def __init__(self, builder: RPLApplicationBuilder):
        self._builder = builder

    def build_single_module_application(self, module_code: str,
                                        module_name: str, credits: int) -> RPLApplication:
        """Build a minimal application with one module and no evidence."""
        return (
            self._builder
            .add_module_request("MR-001", module_code, module_name, credits,
                                "Standard RPL application.")
            .build()
        )

    def build_full_application(self) -> RPLApplication:
        """Build a complete application with multiple modules and evidence."""
        return (
            self._builder
            .add_module_request(
                "MR-001", "CS301", "Data Structures", 16,
                "Completed equivalent course at UKZN in 2019."
            )
            .add_evidence("MR-001", "D001", "UKZN_Transcript.pdf", "pdf")
            .add_evidence("MR-001", "D002", "Module_Outline.pdf", "pdf")
            .add_module_request(
                "MR-002", "CS401", "Software Engineering", 16,
                "5 years as a software developer at ABC Corp."
            )
            .add_evidence("MR-002", "D003", "EmployerLetter.pdf", "pdf")
            .add_evidence("MR-002", "D004", "Portfolio.pdf", "pdf")
            .build()
        )


# ── Demo ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Builder Pattern Demo ===\n")

    # Direct builder usage — fluent API
    print("-- Direct builder (fluent) --")
    builder = RPLApplicationBuilder("APP-201", "STU-005")
    app = (
        builder
        .add_module_request("MR-A", "NET101", "Computer Networks", 12,
                            "Cisco CCNA certified.")
        .add_evidence("MR-A", "E001", "CCNA_Certificate.pdf", "pdf")
        .add_module_request("MR-B", "DB201", "Database Design", 16,
                            "3 years as DBA at XYZ Ltd.")
        .add_evidence("MR-B", "E002", "Employer_Ref.pdf", "pdf")
        .build()
    )
    print(app.get_application_summary())

    # Director usage
    print("\n-- Director (full application) --")
    director_builder = RPLApplicationBuilder("APP-202", "STU-006")
    director = RPLApplicationDirector(director_builder)
    full_app = director.build_full_application()
    print(full_app.get_application_summary())
    print(f"Module requests: {len(full_app.module_requests)}")

    # Edge case: empty application should raise
    print("\n-- Edge case: no module requests --")
    try:
        empty_builder = RPLApplicationBuilder("APP-203", "STU-007")
        empty_builder.build()
    except ValueError as e:
        print(f"Expected error: {e}")
