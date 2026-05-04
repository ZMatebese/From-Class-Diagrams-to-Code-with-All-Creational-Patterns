"""
RPL System - Assessor, AssessmentReport, AssessmentPanel, AcademicModule, Admin Classes
"""
from datetime import datetime
from typing import List, Optional


class AcademicModule:
    """Represents a formal academic module within the institution."""

    def __init__(self, module_code: str, module_name: str,
                 credits: int, faculty: str, nqf_level: int):
        self.__module_code = module_code
        self.__module_name = module_name
        self.__credits = credits
        self.__faculty = faculty
        self.__nqf_level = nqf_level
        self.__is_active = True

    # Getters
    @property
    def module_code(self): return self.__module_code
    @property
    def module_name(self): return self.__module_name
    @property
    def credits(self): return self.__credits
    @property
    def faculty(self): return self.__faculty
    @property
    def nqf_level(self): return self.__nqf_level
    @property
    def is_active(self): return self.__is_active

    def get_module_details(self) -> dict:
        return {
            "module_code": self.__module_code,
            "module_name": self.__module_name,
            "credits": self.__credits,
            "faculty": self.__faculty,
            "nqf_level": self.__nqf_level,
            "is_active": self.__is_active,
        }

    def check_eligibility(self, student_nqf_level: int) -> bool:
        """BR-007: Student's NQF level must meet or exceed the module's level."""
        return student_nqf_level >= self.__nqf_level

    def update_module_info(self, details: dict) -> None:
        if "module_name" in details:
            self.__module_name = details["module_name"]
        if "credits" in details:
            self.__credits = details["credits"]
        if "faculty" in details:
            self.__faculty = details["faculty"]

    def deactivate_module(self) -> None:
        self.__is_active = False

    def __repr__(self):
        return (f"AcademicModule(code={self.__module_code}, "
                f"name={self.__module_name}, NQF={self.__nqf_level})")


class AssessmentReport:
    """Created by an assessor to document their review of an RPL application."""

    def __init__(self, report_id: str, application_id: str, assessor_id: str):
        self.__report_id = report_id
        self.__application_id = application_id
        self.__assessor_id = assessor_id
        self.__creation_date: Optional[datetime] = None
        self.__recommendation: str = ""
        self.__comments: str = ""
        self.__final_decision: str = "Pending"

    # Getters
    @property
    def report_id(self): return self.__report_id
    @property
    def application_id(self): return self.__application_id
    @property
    def assessor_id(self): return self.__assessor_id
    @property
    def recommendation(self): return self.__recommendation
    @property
    def comments(self): return self.__comments
    @property
    def final_decision(self): return self.__final_decision
    @property
    def creation_date(self): return self.__creation_date

    def generate_report(self, recommendation: str, comments: str) -> None:
        self.__recommendation = recommendation
        self.__comments = comments
        self.__creation_date = datetime.now()

    def submit_to_panel(self) -> None:
        if not self.__recommendation:
            raise ValueError("Report must have a recommendation before panel submission.")

    def record_decision(self, decision: str) -> None:
        valid_decisions = {"Approved", "Rejected", "PartiallyApproved", "Deferred"}
        if decision not in valid_decisions:
            raise ValueError(f"Invalid decision: {decision}")
        self.__final_decision = decision

    def get_report_details(self) -> dict:
        return {
            "report_id": self.__report_id,
            "application_id": self.__application_id,
            "assessor_id": self.__assessor_id,
            "recommendation": self.__recommendation,
            "comments": self.__comments,
            "final_decision": self.__final_decision,
            "creation_date": str(self.__creation_date),
        }

    def __repr__(self):
        return (f"AssessmentReport(id={self.__report_id}, "
                f"application={self.__application_id}, decision={self.__final_decision})")


class Assessor:
    """Reviews RPL applications and produces assessment reports."""

    def __init__(self, assessor_id: str, full_name: str, email: str,
                 department: str, qualification: str):
        self._assessor_id = assessor_id
        self._full_name = full_name
        self._email = email
        self._department = department
        self._qualification = qualification
        self._availability_status = "Available"
        self._reports: List[AssessmentReport] = []

    # Getters
    @property
    def assessor_id(self): return self._assessor_id
    @property
    def full_name(self): return self._full_name
    @property
    def email(self): return self._email
    @property
    def department(self): return self._department
    @property
    def qualification(self): return self._qualification
    @property
    def availability_status(self): return self._availability_status

    @availability_status.setter
    def availability_status(self, value: str):
        if value in ("Available", "Unavailable", "OnLeave"):
            self._availability_status = value

    def review_application(self, application) -> None:
        """BR-008: Assessor cannot review an application from their own department."""
        # Department conflict check would use application.student.department
        application.update_status("UnderReview")

    def approve_evidence(self, document) -> None:
        document.verify()

    def reject_evidence(self, document, reason: str) -> None:
        document.reject(reason)

    def write_assessment_report(self, application_id: str,
                                recommendation: str, comments: str) -> AssessmentReport:
        report_id = f"RPT-{self._assessor_id}-{application_id}"
        report = AssessmentReport(report_id, application_id, self._assessor_id)
        report.generate_report(recommendation, comments)
        self._reports.append(report)
        return report

    def escalate_to_panel(self, application_id: str) -> str:
        return f"Application {application_id} escalated to panel by {self._assessor_id}."

    def get_reports(self) -> List[AssessmentReport]:
        return list(self._reports)

    def __repr__(self):
        return (f"Assessor(id={self._assessor_id}, name={self._full_name}, "
                f"dept={self._department})")


class AssessmentPanel:
    """A panel of assessors that makes the final decision on an RPL application."""

    MIN_QUORUM = 3

    def __init__(self, panel_id: str, panel_name: str, meeting_date: datetime):
        self.__panel_id = panel_id
        self.__panel_name = panel_name
        self.__meeting_date = meeting_date
        self.__members: List[Assessor] = []
        self.__reviewed_reports: List[AssessmentReport] = []

    # Getters
    @property
    def panel_id(self): return self.__panel_id
    @property
    def panel_name(self): return self.__panel_name
    @property
    def meeting_date(self): return self.__meeting_date
    @property
    def members(self): return list(self.__members)

    def add_member(self, assessor: Assessor) -> None:
        if assessor not in self.__members:
            self.__members.append(assessor)

    def convene_panel(self) -> bool:
        """BR-005: Panel requires minimum quorum of 3 assessors."""
        if len(self.__members) < self.MIN_QUORUM:
            raise ValueError(
                f"BR-005: Quorum not met. Need {self.MIN_QUORUM}, have {len(self.__members)}."
            )
        return True

    def review_report(self, report: AssessmentReport) -> None:
        self.__reviewed_reports.append(report)

    def make_final_decision(self, report: AssessmentReport, decision: str) -> None:
        self.convene_panel()
        report.record_decision(decision)

    def notify_outcome(self, application_id: str, decision: str) -> str:
        return f"Panel [{self.__panel_id}] decision '{decision}' for application {application_id} dispatched."

    def __repr__(self):
        return (f"AssessmentPanel(id={self.__panel_id}, "
                f"name={self.__panel_name}, members={len(self.__members)})")


class Admin(Assessor):
    """
    Admin extends Assessor — an Admin is a senior assessor with additional
    system management privileges (inheritance relationship from class diagram).
    """

    def __init__(self, admin_id: str, full_name: str, email: str,
                 department: str, qualification: str, role: str = "SystemAdmin"):
        super().__init__(admin_id, full_name, email, department, qualification)
        self.__admin_id = admin_id
        self.__role = role
        self.__permissions: List[str] = [
            "manage_users", "configure_modules", "generate_reports",
            "assign_assessor", "audit_system", "confirm_credits"
        ]

    @property
    def admin_id(self): return self.__admin_id
    @property
    def role(self): return self.__role
    @property
    def permissions(self): return list(self.__permissions)

    def manage_users(self, action: str, user_id: str) -> str:
        return f"Admin [{self.__admin_id}] performed '{action}' on user {user_id}."

    def configure_modules(self, module: AcademicModule, details: dict) -> None:
        module.update_module_info(details)

    def generate_system_report(self) -> dict:
        return {
            "admin": self._full_name,
            "role": self.__role,
            "generated_at": str(datetime.now()),
            "report": "System audit report generated.",
        }

    def assign_assessor(self, application, assessor: Assessor) -> str:
        return (f"Admin [{self.__admin_id}] assigned assessor "
                f"{assessor.assessor_id} to application {application.application_id}.")

    def audit_system(self) -> str:
        return f"System audit performed by {self._full_name} at {datetime.now()}."

    def confirm_credit_grant(self, module_request) -> bool:
        """BR-010: Credits only granted after Admin confirmation."""
        if module_request.request_status == "Approved":
            return True
        raise ValueError("BR-010: Module request must be Approved before credit confirmation.")

    def __repr__(self):
        return f"Admin(id={self.__admin_id}, name={self._full_name}, role={self.__role})"
