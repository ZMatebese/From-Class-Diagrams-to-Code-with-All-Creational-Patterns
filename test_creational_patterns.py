"""
Unit Tests — RPL System: Creational Patterns & Core Classes
============================================================
Run with: pytest tests/test_creational_patterns.py -v
Coverage: pytest tests/test_creational_patterns.py --cov=src --cov=creational_patterns --cov-report=term-missing
"""
import sys, os, threading
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import datetime

# Core classes
from src.student import Student, StudentProfile
from src.module_request import ModuleRequest, EvidenceDocument
from src.rpl_application import RPLApplication, Notification
from src.assessor import (Assessor, Admin, AcademicModule,
                           AssessmentReport, AssessmentPanel)

# Creational patterns
from creational_patterns.simple_factory import RPLObjectFactory
from creational_patterns.factory_method import (
    AcademicVerifier, EmployerVerifier, CertificateVerifier, get_verifier
)
from creational_patterns.abstract_factory import (
    WebPortalFactory, MobilePortalFactory, RPLPortalClient
)
from creational_patterns.builder import RPLApplicationBuilder, RPLApplicationDirector
from creational_patterns.prototype import ModuleRequestPrototype, ModuleRequestCache
from creational_patterns.singleton import DatabaseConnection


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 1: Core Class Tests
# ════════════════════════════════════════════════════════════════════════════════

class TestStudentProfile:
    def setup_method(self):
        self.profile = StudentProfile("PROF-001", "STU-001")

    def test_initial_state(self):
        assert self.profile.profile_id == "PROF-001"
        assert self.profile.student_id == "STU-001"
        assert self.profile.qualifications == []
        assert self.profile.work_experience == []

    def test_add_qualification(self):
        self.profile.add_qualification("BSc Computer Science (Wits, 2018)")
        assert len(self.profile.qualifications) == 1
        assert "BSc Computer Science (Wits, 2018)" in self.profile.qualifications

    def test_duplicate_qualification_not_added(self):
        self.profile.add_qualification("BSc")
        self.profile.add_qualification("BSc")
        assert len(self.profile.qualifications) == 1

    def test_add_work_experience(self):
        self.profile.add_work_experience("Software Developer at ABC Corp, 5 years")
        assert len(self.profile.work_experience) == 1

    def test_get_profile_summary(self):
        self.profile.add_qualification("BSc")
        summary = self.profile.get_profile_summary()
        assert "PROF-001" in summary
        assert "Qualifications: 1" in summary


class TestStudent:
    def setup_method(self):
        self.student = Student("STU-001", "Thabo Nkosi", "thabo@test.com", "082-111-2222")

    def test_attributes(self):
        assert self.student.student_id == "STU-001"
        assert self.student.full_name == "Thabo Nkosi"
        assert self.student.email == "thabo@test.com"
        assert self.student.status == "Active"

    def test_profile_created_automatically(self):
        assert self.student.profile is not None
        assert isinstance(self.student.profile, StudentProfile)

    def test_submit_application(self):
        app = RPLApplication("APP-001", "STU-001")
        app.add_module_request(ModuleRequest("MR-001", "CS101", "Intro to Programming", 12))
        result = self.student.submit_application(app)
        assert result is True

    def test_br001_max_three_active_applications(self):
        """BR-001: Student cannot have more than 3 active applications."""
        for i in range(3):
            app = RPLApplication(f"APP-{i}", "STU-001")
            mr = ModuleRequest(f"MR-{i}", "CS101", "Intro", 12)
            app.add_module_request(mr)
            app.submit()
            self.student.submit_application(app)

        fourth_app = RPLApplication("APP-99", "STU-001")
        mr = ModuleRequest("MR-99", "CS201", "OOP", 12)
        fourth_app.add_module_request(mr)
        fourth_app.submit()

        with pytest.raises(ValueError, match="BR-001"):
            self.student.submit_application(fourth_app)

    def test_track_application_status(self):
        app = RPLApplication("APP-TRK", "STU-001")
        mr = ModuleRequest("MR-TRK", "CS101", "Intro", 12)
        app.add_module_request(mr)
        app.submit()
        self.student.submit_application(app)
        status = self.student.track_application_status("APP-TRK")
        assert status == "Pending"

    def test_track_nonexistent_application(self):
        result = self.student.track_application_status("INVALID")
        assert result == "Application not found."

    def test_update_profile(self):
        result = self.student.update_profile({
            "qualification": "BSc CS",
            "institution": "Wits University"
        })
        assert result is True
        assert "BSc CS" in self.student.profile.qualifications


class TestEvidenceDocument:
    def setup_method(self):
        self.doc = EvidenceDocument("D001", "transcript.pdf", "pdf", "http://files/D001")

    def test_initial_state(self):
        assert self.doc.document_id == "D001"
        assert self.doc.verification_status == "Pending"
        assert self.doc.upload_date is None

    def test_upload(self):
        result = self.doc.upload()
        assert result is True
        assert self.doc.verification_status == "Uploaded"
        assert self.doc.upload_date is not None

    def test_verify_after_upload(self):
        self.doc.upload()
        self.doc.verify()
        assert self.doc.verification_status == "Verified"

    def test_verify_without_upload_raises(self):
        with pytest.raises(ValueError, match="uploaded"):
            self.doc.verify()

    def test_reject(self):
        self.doc.upload()
        self.doc.reject("Document is illegible.")
        assert self.doc.verification_status == "Rejected"
        assert self.doc.rejection_reason == "Document is illegible."

    def test_invalid_file_type_raises(self):
        with pytest.raises(ValueError, match="not allowed"):
            EvidenceDocument("D002", "virus.exe", "exe")

    def test_get_file_metadata(self):
        metadata = self.doc.get_file_metadata()
        assert metadata["document_id"] == "D001"
        assert metadata["file_type"] == "pdf"


class TestModuleRequest:
    def setup_method(self):
        self.mr = ModuleRequest("MR-001", "CS301", "Data Structures", 16, "Equiv course")

    def test_attributes(self):
        assert self.mr.module_code == "CS301"
        assert self.mr.credits == 16
        assert self.mr.request_status == "Pending"

    def test_invalid_credits_raises(self):
        with pytest.raises(ValueError):
            ModuleRequest("MR-X", "CS999", "Bad Credits", 0)

    def test_attach_evidence(self):
        doc = EvidenceDocument("D001", "file.pdf", "pdf")
        doc.upload()
        self.mr.attach_evidence(doc)
        assert len(self.mr.evidence_documents) == 1

    def test_attach_invalid_evidence_type_raises(self):
        with pytest.raises(TypeError):
            self.mr.attach_evidence("not a document")

    def test_update_status(self):
        self.mr.update_request_status("UnderReview")
        assert self.mr.request_status == "UnderReview"

    def test_invalid_status_raises(self):
        with pytest.raises(ValueError):
            self.mr.update_request_status("Flying")

    def test_has_verified_evidence_false_with_no_docs(self):
        assert self.mr.has_verified_evidence() is False

    def test_has_verified_evidence_true(self):
        doc = EvidenceDocument("D001", "file.pdf", "pdf")
        doc.upload()
        doc.verify()
        self.mr.attach_evidence(doc)
        assert self.mr.has_verified_evidence() is True


class TestRPLApplication:
    def setup_method(self):
        self.app = RPLApplication("APP-001", "STU-001")
        self.mr = ModuleRequest("MR-001", "CS101", "Intro", 12, "Prior learning")

    def test_initial_status_is_draft(self):
        assert self.app.status == "Draft"

    def test_submit_requires_module_request(self):
        """BR-002: Must have at least one module request."""
        with pytest.raises(ValueError, match="BR-002"):
            self.app.submit()

    def test_submit_success(self):
        self.app.add_module_request(self.mr)
        result = self.app.submit()
        assert result is True
        assert self.app.status == "Pending"
        assert self.app.submission_date is not None

    def test_calculate_fee(self):
        self.app.add_module_request(self.mr)
        self.app.submit()
        expected = 500.00 + 1 * 150.00
        assert self.app.application_fee == expected

    def test_withdraw_from_pending(self):
        self.app.add_module_request(self.mr)
        self.app.submit()
        result = self.app.withdraw()
        assert result is True
        assert self.app.status == "Withdrawn"

    def test_br004_cannot_withdraw_approved(self):
        """BR-004: Cannot withdraw an approved application."""
        self.app.add_module_request(self.mr)
        self.app.submit()
        self.app.update_status("Approved")
        with pytest.raises(ValueError, match="BR-004"):
            self.app.withdraw()

    def test_notifications_sent_on_status_change(self):
        self.app.add_module_request(self.mr)
        self.app.submit()
        notifications = self.app.get_notifications()
        assert len(notifications) >= 1

    def test_get_application_summary(self):
        self.app.add_module_request(self.mr)
        summary = self.app.get_application_summary()
        assert "APP-001" in summary
        assert "STU-001" in summary


class TestAssessmentPanel:
    def setup_method(self):
        self.panel = AssessmentPanel("PNL-001", "Science Panel", datetime.now())
        self.assessors = [
            Assessor(f"ASSR-{i}", f"Assessor {i}", f"a{i}@test.com", "CS", "PhD")
            for i in range(4)
        ]

    def test_br005_quorum_required(self):
        """BR-005: Panel needs at least 3 members."""
        self.panel.add_member(self.assessors[0])
        self.panel.add_member(self.assessors[1])
        with pytest.raises(ValueError, match="BR-005"):
            self.panel.convene_panel()

    def test_convene_with_quorum(self):
        for a in self.assessors[:3]:
            self.panel.add_member(a)
        result = self.panel.convene_panel()
        assert result is True

    def test_make_final_decision(self):
        for a in self.assessors[:3]:
            self.panel.add_member(a)
        report = AssessmentReport("RPT-001", "APP-001", "ASSR-0")
        report.generate_report("Approve", "Strong evidence provided.")
        self.panel.make_final_decision(report, "Approved")
        assert report.final_decision == "Approved"


class TestAdmin:
    def setup_method(self):
        self.admin = Admin("ADM-001", "Fatima Moosa", "fatima@rpl.ac.za",
                           "Registry", "MEd")

    def test_admin_inherits_assessor(self):
        assert isinstance(self.admin, Assessor)

    def test_admin_has_permissions(self):
        assert "manage_users" in self.admin.permissions
        assert "confirm_credits" in self.admin.permissions

    def test_confirm_credit_grant_requires_approved_status(self):
        mr = ModuleRequest("MR-001", "CS101", "Intro", 12)
        with pytest.raises(ValueError, match="BR-010"):
            self.admin.confirm_credit_grant(mr)

    def test_confirm_credit_grant_success(self):
        mr = ModuleRequest("MR-001", "CS101", "Intro", 12)
        mr.update_request_status("Approved")
        result = self.admin.confirm_credit_grant(mr)
        assert result is True

    def test_audit_system(self):
        result = self.admin.audit_system()
        assert "Fatima Moosa" in result


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 2: Simple Factory Tests
# ════════════════════════════════════════════════════════════════════════════════

class TestSimpleFactory:
    def test_create_email_notification(self):
        notif = RPLObjectFactory.create_notification("email", "N001", "Hello", "STU-001")
        assert isinstance(notif, Notification)
        assert notif.channel == "email"

    def test_create_sms_notification(self):
        notif = RPLObjectFactory.create_notification("sms", "N002", "Update", "STU-002")
        assert notif.channel == "sms"

    def test_create_inapp_notification(self):
        notif = RPLObjectFactory.create_notification("in-app", "N003", "Alert", "STU-003")
        assert notif.channel == "in-app"

    def test_invalid_notification_type_raises(self):
        with pytest.raises(ValueError, match="Unknown notification type"):
            RPLObjectFactory.create_notification("fax", "N004", "msg", "STU-004")

    def test_create_standard_application(self):
        app = RPLObjectFactory.create_application("standard", "APP-SF-001", "STU-001")
        assert isinstance(app, RPLApplication)
        assert app.application_id == "APP-SF-001"

    def test_create_expedited_application(self):
        app = RPLObjectFactory.create_application("expedited", "APP-SF-002", "STU-002")
        assert isinstance(app, RPLApplication)

    def test_invalid_application_type_raises(self):
        with pytest.raises(ValueError, match="Unknown application type"):
            RPLObjectFactory.create_application("unknown", "APP-SF-X", "STU-X")


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 3: Factory Method Tests
# ════════════════════════════════════════════════════════════════════════════════

class TestFactoryMethod:
    def test_academic_verifier_creates_correct_processor(self):
        doc = EvidenceDocument("D001", "transcript.pdf", "pdf")
        verifier = AcademicVerifier()
        result = verifier.verify_document(doc)
        assert "transcript" in result.lower()
        assert doc.verification_status == "Verified"

    def test_employer_verifier(self):
        doc = EvidenceDocument("D002", "letter.pdf", "pdf")
        verifier = EmployerVerifier()
        result = verifier.verify_document(doc)
        assert "employer" in result.lower() or "company" in result.lower()
        assert doc.verification_status == "Verified"

    def test_certificate_verifier(self):
        doc = EvidenceDocument("D003", "cert.pdf", "pdf")
        verifier = CertificateVerifier()
        result = verifier.verify_document(doc)
        assert doc.verification_status == "Verified"

    def test_get_verifier_returns_correct_type(self):
        assert isinstance(get_verifier("transcript"), AcademicVerifier)
        assert isinstance(get_verifier("employer_letter"), EmployerVerifier)
        assert isinstance(get_verifier("certificate"), CertificateVerifier)

    def test_get_verifier_invalid_category_raises(self):
        with pytest.raises(ValueError, match="Unknown document category"):
            get_verifier("x_ray")

    def test_verifiers_are_independent(self):
        """Each verifier handles its document independently."""
        doc1 = EvidenceDocument("DA", "a.pdf", "pdf")
        doc2 = EvidenceDocument("DB", "b.pdf", "pdf")
        AcademicVerifier().verify_document(doc1)
        EmployerVerifier().verify_document(doc2)
        assert doc1.verification_status == "Verified"
        assert doc2.verification_status == "Verified"


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 4: Abstract Factory Tests
# ════════════════════════════════════════════════════════════════════════════════

class TestAbstractFactory:
    def test_web_factory_creates_web_components(self):
        factory = WebPortalFactory()
        form = factory.create_application_form()
        btn = factory.create_submit_button()
        renderer = factory.create_report_renderer()
        assert "form" in form.render().lower() or "input" in form.render().lower()
        assert "button" in btn.render().lower()

    def test_mobile_factory_creates_mobile_components(self):
        factory = MobilePortalFactory()
        form = factory.create_application_form()
        btn = factory.create_submit_button()
        assert "mobile" in form.render().lower() or "tap" in btn.render().lower()

    def test_web_form_validation_requires_both_fields(self):
        factory = WebPortalFactory()
        form = factory.create_application_form()
        assert form.validate({"module_code": "CS101", "justification": "5 years exp"}) is True
        assert form.validate({"module_code": "CS101"}) is False

    def test_mobile_form_validation_requires_only_module_code(self):
        factory = MobilePortalFactory()
        form = factory.create_application_form()
        assert form.validate({"module_code": "CS101"}) is True
        assert form.validate({}) is False

    def test_web_report_renderer_includes_decision(self):
        factory = WebPortalFactory()
        renderer = factory.create_report_renderer()
        result = renderer.render_report({"report_id": "R1", "final_decision": "Approved", "comments": "Good."})
        assert "Approved" in result

    def test_mobile_report_renderer_truncates_comments(self):
        factory = MobilePortalFactory()
        renderer = factory.create_report_renderer()
        long_comment = "A" * 200
        result = renderer.render_report({"report_id": "R1", "final_decision": "Rejected", "comments": long_comment})
        assert "..." in result

    def test_client_works_with_either_factory(self):
        for factory in [WebPortalFactory(), MobilePortalFactory()]:
            client = RPLPortalClient(factory)
            assert client is not None


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 5: Builder Tests
# ════════════════════════════════════════════════════════════════════════════════

class TestBuilder:
    def test_build_with_one_module(self):
        builder = RPLApplicationBuilder("APP-B01", "STU-001")
        app = (builder
               .add_module_request("MR-1", "CS101", "Intro", 12, "Self-taught")
               .build())
        assert isinstance(app, RPLApplication)
        assert len(app.module_requests) == 1

    def test_build_with_multiple_modules(self):
        builder = RPLApplicationBuilder("APP-B02", "STU-002")
        app = (builder
               .add_module_request("MR-1", "CS101", "Intro", 12)
               .add_module_request("MR-2", "CS301", "Data Structures", 16)
               .add_module_request("MR-3", "CS401", "Software Eng", 16)
               .build())
        assert len(app.module_requests) == 3

    def test_build_with_evidence(self):
        builder = RPLApplicationBuilder("APP-B03", "STU-003")
        app = (builder
               .add_module_request("MR-1", "CS101", "Intro", 12)
               .add_evidence("MR-1", "D001", "transcript.pdf", "pdf")
               .build())
        mr = app.module_requests[0]
        assert len(mr.evidence_documents) == 1

    def test_build_empty_raises(self):
        """BR-002: Builder should reject empty applications."""
        builder = RPLApplicationBuilder("APP-B99", "STU-099")
        with pytest.raises(ValueError, match="BR-002"):
            builder.build()

    def test_evidence_for_nonexistent_module_raises(self):
        builder = RPLApplicationBuilder("APP-B04", "STU-004")
        with pytest.raises(ValueError, match="No module request"):
            builder.add_evidence("MR-GHOST", "D001", "file.pdf", "pdf")

    def test_fluent_interface_returns_builder(self):
        builder = RPLApplicationBuilder("APP-B05", "STU-005")
        result = builder.add_module_request("MR-1", "CS101", "Intro", 12)
        assert result is builder

    def test_director_builds_full_application(self):
        builder = RPLApplicationBuilder("APP-DIR-01", "STU-010")
        director = RPLApplicationDirector(builder)
        app = director.build_full_application()
        assert len(app.module_requests) == 2

    def test_fee_calculated_correctly_by_builder(self):
        builder = RPLApplicationBuilder("APP-B06", "STU-006")
        app = (builder
               .add_module_request("MR-1", "CS101", "Intro", 12)
               .add_module_request("MR-2", "CS201", "OOP", 12)
               .build())
        app.submit()
        expected_fee = 500.00 + 2 * 150.00
        assert app.application_fee == expected_fee


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 6: Prototype Tests
# ════════════════════════════════════════════════════════════════════════════════

class TestPrototype:
    def setup_method(self):
        ModuleRequestCache.load_cache()

    def test_clone_creates_independent_object(self):
        proto = ModuleRequestPrototype("TMPL-001", "CS301", "Data Structures", 16)
        clone = proto.clone()
        assert clone is not proto

    def test_clone_has_same_attributes(self):
        proto = ModuleRequestPrototype("TMPL-001", "CS301", "Data Structures", 16)
        clone = proto.clone()
        assert clone._module_code == proto._module_code
        assert clone._credits == proto._credits

    def test_cache_get_clone(self):
        clone = ModuleRequestCache.get_clone("CS301", "MR-STU001-CS301", "5 years exp")
        assert clone._module_code == "CS301"
        assert clone._module_request_id == "MR-STU001-CS301"
        assert clone._justification == "5 years exp"

    def test_two_clones_are_independent(self):
        clone1 = ModuleRequestCache.get_clone("CS301", "MR-A", "Justification A")
        clone2 = ModuleRequestCache.get_clone("CS301", "MR-B", "Justification B")
        assert clone1 is not clone2
        assert clone1._module_request_id != clone2._module_request_id
        assert clone1._justification != clone2._justification

    def test_clone_does_not_affect_cache_template(self):
        before_id = "TMPL-CS301"
        ModuleRequestCache.get_clone("CS301", "MR-STUDENT", "Test")
        # Original template in cache should still have its original ID
        original = ModuleRequestCache._cache["CS301"]
        assert original._module_request_id == before_id

    def test_invalid_module_code_raises(self):
        with pytest.raises(KeyError):
            ModuleRequestCache.get_clone("INVALID999", "MR-X", "Test")

    def test_to_module_request_conversion(self):
        clone = ModuleRequestCache.get_clone("DB201", "MR-DB-001", "DBA experience")
        mr = clone.to_module_request()
        assert isinstance(mr, ModuleRequest)
        assert mr.module_code == "DB201"
        assert mr.credits == 16

    def test_list_available_returns_all_templates(self):
        available = ModuleRequestCache.list_available()
        assert "CS101" in available
        assert "CS301" in available
        assert "DB201" in available

    def test_deep_clone_creates_independent_copy(self):
        proto = ModuleRequestPrototype("T1", "CS101", "Intro", 12)
        deep = proto.deep_clone()
        assert deep is not proto
        assert deep._module_code == proto._module_code


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 7: Singleton Tests
# ════════════════════════════════════════════════════════════════════════════════

class TestSingleton:
    def setup_method(self):
        DatabaseConnection.reset_instance()

    def test_single_instance(self):
        db1 = DatabaseConnection()
        db2 = DatabaseConnection()
        assert db1 is db2

    def test_same_id(self):
        db1 = DatabaseConnection()
        db2 = DatabaseConnection()
        assert id(db1) == id(db2)

    def test_connect_and_disconnect(self):
        db = DatabaseConnection()
        db.connect()
        assert db.is_connected is True
        db.disconnect()
        assert db.is_connected is False

    def test_query_requires_connection(self):
        db = DatabaseConnection()
        with pytest.raises(ConnectionError, match="No active database connection"):
            db.execute_query("SELECT 1")

    def test_query_increments_count(self):
        db = DatabaseConnection()
        db.connect()
        db.execute_query("SELECT * FROM students")
        db.execute_query("SELECT * FROM applications")
        assert db.query_count == 2

    def test_query_count_shared_across_references(self):
        db1 = DatabaseConnection()
        db2 = DatabaseConnection()
        db1.connect()
        db1.execute_query("SELECT 1")
        assert db2.query_count == 1  # same instance

    def test_thread_safety(self):
        """10 threads must all get the same singleton instance."""
        instances = []

        def get_instance():
            conn = DatabaseConnection()
            instances.append(id(conn))

        threads = [threading.Thread(target=get_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(set(instances)) == 1, "Multiple instances created — thread safety failed!"

    def test_connection_info(self):
        db = DatabaseConnection(host="testhost", database="test_db")
        info = db.get_connection_info()
        assert info["host"] == "testhost"
        assert info["database"] == "test_db"

    def test_reset_allows_new_instance(self):
        db1 = DatabaseConnection()
        DatabaseConnection.reset_instance()
        db2 = DatabaseConnection()
        # After reset, a new instance is created — IDs differ
        assert id(db1) != id(db2)
