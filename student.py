"""
RPL System - Student and StudentProfile Classes
"""
from datetime import datetime
from typing import List, Optional


class StudentProfile:
    """Stores a student's prior learning history separately from account data."""

    def __init__(self, profile_id: str, student_id: str):
        self.__profile_id = profile_id
        self.__student_id = student_id
        self.__qualifications: List[str] = []
        self.__work_experience: List[str] = []
        self.__institutions: List[str] = []
        self.__updated_at: datetime = datetime.now()

    # Getters
    @property
    def profile_id(self): return self.__profile_id
    @property
    def student_id(self): return self.__student_id
    @property
    def qualifications(self): return list(self.__qualifications)
    @property
    def work_experience(self): return list(self.__work_experience)
    @property
    def institutions(self): return list(self.__institutions)
    @property
    def updated_at(self): return self.__updated_at

    def add_qualification(self, qual: str) -> None:
        if qual and qual not in self.__qualifications:
            self.__qualifications.append(qual)
            self.__updated_at = datetime.now()

    def add_work_experience(self, exp: str) -> None:
        if exp and exp not in self.__work_experience:
            self.__work_experience.append(exp)
            self.__updated_at = datetime.now()

    def add_institution(self, institution: str) -> None:
        if institution and institution not in self.__institutions:
            self.__institutions.append(institution)
            self.__updated_at = datetime.now()

    def get_profile_summary(self) -> str:
        return (
            f"Profile [{self.__profile_id}] | "
            f"Qualifications: {len(self.__qualifications)} | "
            f"Work Experience: {len(self.__work_experience)} entries | "
            f"Institutions: {', '.join(self.__institutions) if self.__institutions else 'None'}"
        )

    def __repr__(self):
        return f"StudentProfile(id={self.__profile_id}, student_id={self.__student_id})"


class Student:
    """Represents a student who can submit RPL applications."""

    def __init__(self, student_id: str, full_name: str, email: str, phone: str = ""):
        self.__student_id = student_id
        self.__full_name = full_name
        self.__email = email
        self.__phone = phone
        self.__registration_date: datetime = datetime.now()
        self.__status: str = "Active"
        self.__profile: Optional[StudentProfile] = StudentProfile(
            f"PROF-{student_id}", student_id
        )
        self.__applications: List = []

    # Getters
    @property
    def student_id(self): return self.__student_id
    @property
    def full_name(self): return self.__full_name
    @property
    def email(self): return self.__email
    @property
    def phone(self): return self.__phone
    @property
    def status(self): return self.__status
    @property
    def registration_date(self): return self.__registration_date
    @property
    def profile(self): return self.__profile

    # Setters
    @full_name.setter
    def full_name(self, value: str):
        if value:
            self.__full_name = value

    @email.setter
    def email(self, value: str):
        if "@" in value:
            self.__email = value

    @status.setter
    def status(self, value: str):
        valid_statuses = {"Active", "Suspended", "Graduated", "Withdrawn"}
        if value in valid_statuses:
            self.__status = value

    def submit_application(self, application) -> bool:
        """Submit an RPL application. Max 3 active applications allowed (BR-001)."""
        active_count = sum(
            1 for app in self.__applications
            if app.status in ("Pending", "UnderReview")
        )
        if active_count >= 3:
            raise ValueError("BR-001: Cannot have more than 3 active applications.")
        self.__applications.append(application)
        return True

    def track_application_status(self, application_id: str) -> str:
        for app in self.__applications:
            if app.application_id == application_id:
                return app.status
        return "Application not found."

    def view_outcome(self, application_id: str) -> str:
        for app in self.__applications:
            if app.application_id == application_id:
                if app.status in ("Approved", "Rejected", "PartiallyApproved"):
                    return f"Outcome: {app.status}"
                return f"Application still in progress: {app.status}"
        return "Application not found."

    def update_profile(self, details: dict) -> bool:
        if "qualification" in details:
            self.__profile.add_qualification(details["qualification"])
        if "work_experience" in details:
            self.__profile.add_work_experience(details["work_experience"])
        if "institution" in details:
            self.__profile.add_institution(details["institution"])
        return True

    def get_applications(self) -> list:
        return list(self.__applications)

    def __repr__(self):
        return f"Student(id={self.__student_id}, name={self.__full_name}, status={self.__status})"
