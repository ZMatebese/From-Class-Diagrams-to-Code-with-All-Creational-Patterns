# CHANGELOG
## RPL System — Recognition of Prior Learning

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — Assignment 10 Release

### Added — Core Class Implementations (`/src`)
- `student.py` — `Student` and `StudentProfile` classes with full encapsulation
  - Implemented BR-001: max 3 active applications per student
  - `StudentProfile` separated to honour Single Responsibility Principle
- `module_request.py` — `EvidenceDocument` and `ModuleRequest` classes
  - `EvidenceDocument` validates file types on construction
  - `EvidenceDocument` enforces upload-before-verify workflow
  - `ModuleRequest` enforces positive credits (validates on init)
  - `has_verified_evidence()` enforces BR-003
- `rpl_application.py` — `RPLApplication` and `Notification` classes
  - `submit()` enforces BR-002 (min 1 module request)
  - `withdraw()` enforces BR-004 (only Pending/UnderReview)
  - `calculate_fee()` — base R500 + R150 per module request
  - Automatic notifications triggered on every status change
- `assessor.py` — `Assessor`, `Admin`, `AcademicModule`, `AssessmentReport`, `AssessmentPanel`
  - `Admin` inherits from `Assessor` (matches UML class diagram)
  - `AssessmentPanel.convene_panel()` enforces BR-005 (quorum ≥ 3)
  - `Admin.confirm_credit_grant()` enforces BR-010
  - `AcademicModule.check_eligibility()` enforces BR-007

### Added — Creational Patterns (`/creational_patterns`)
- `simple_factory.py` — `RPLObjectFactory`
  - Creates `Notification` objects by channel type (email/sms/in-app)
  - Creates `RPLApplication` by type (standard/expedited/appeal)
  - Raises `ValueError` for unknown types
- `factory_method.py` — `EvidenceVerifier` hierarchy
  - Abstract `EvidenceVerifier` with `create_processor()` factory method
  - `AcademicVerifier`, `EmployerVerifier`, `CertificateVerifier` concrete creators
  - Each creates the correct `EvidenceProcessor` for their document type
  - `get_verifier()` helper function for convenient access
- `abstract_factory.py` — Portal UI component families
  - `AbstractPortalFactory` interface
  - `WebPortalFactory` produces web-optimised form, button, renderer
  - `MobilePortalFactory` produces mobile-optimised equivalents
  - `RPLPortalClient` works against the abstract factory — fully decoupled
- `builder.py` — `RPLApplicationBuilder` with fluent API
  - `add_module_request()`, `add_evidence()`, `build()` chainable methods
  - `RPLApplicationDirector` for common pre-configured builds
  - `build()` validates BR-002 before returning the application
  - `add_evidence()` validates module request exists before attaching
- `prototype.py` — `ModuleRequestCache` with template cloning
  - 6 pre-loaded module templates (CS101, CS301, CS401, NET101, DB201, PM301)
  - `get_clone()` returns a customised copy, leaving original template intact
  - `clone()` (shallow) and `deep_clone()` (deep copy) both implemented
  - `to_module_request()` converts prototype to domain object
- `singleton.py` — `DatabaseConnection` thread-safe Singleton
  - Double-checked locking with `threading.Lock()`
  - `connect()`, `disconnect()`, `execute_query()` lifecycle methods
  - `query_count` tracks usage across all references
  - `reset_instance()` provided for test isolation only

### Added — Unit Tests (`/tests`)
- `test_creational_patterns.py` — 89 tests across 9 test classes
  - `TestStudentProfile` — 5 tests
  - `TestStudent` — 7 tests (includes BR-001 edge case)
  - `TestEvidenceDocument` — 7 tests (includes invalid file type, verify-before-upload)
  - `TestModuleRequest` — 7 tests (includes BR-003)
  - `TestRPLApplication` — 8 tests (includes BR-002, BR-004)
  - `TestAssessmentPanel` — 3 tests (includes BR-005 quorum)
  - `TestAdmin` — 5 tests (includes inheritance check, BR-010)
  - `TestSimpleFactory` — 7 tests (valid types + invalid edge cases)
  - `TestFactoryMethod` — 6 tests (each verifier type + invalid category)
  - `TestAbstractFactory` — 7 tests (both factory families + client)
  - `TestBuilder` — 8 tests (fluent API, director, edge cases)
  - `TestPrototype` — 9 tests (clone independence, cache, conversion)
  - `TestSingleton` — 9 tests (identity, thread safety, lifecycle)
- **Result: 89/89 PASSED | 80% overall coverage**

### Added — Documentation
- `README.md` — Language rationale, project structure, run instructions,
  pattern justification table, design decisions, coverage summary
- `CHANGELOG.md` — This file

---

## GitHub Issues Resolved

| Issue | Title | Status |
|---|---|---|
| #01 | Implement Student and StudentProfile classes | ✅ Done |
| #02 | Implement EvidenceDocument with file type validation | ✅ Done |
| #03 | Implement ModuleRequest with BR-003 enforcement | ✅ Done |
| #04 | Implement RPLApplication with BR-002 and BR-004 | ✅ Done |
| #05 | Implement Assessor, Admin, Panel with BR-005, BR-010 | ✅ Done |
| #06 | Simple Factory — RPLObjectFactory | ✅ Done |
| #07 | Factory Method — EvidenceVerifier hierarchy | ✅ Done |
| #08 | Abstract Factory — Portal UI families | ✅ Done |
| #09 | Builder — RPLApplicationBuilder with fluent API | ✅ Done |
| #10 | Prototype — ModuleRequestCache with template cloning | ✅ Done |
| #11 | Singleton — Thread-safe DatabaseConnection | ✅ Done |
| #12 | Unit tests for all patterns (89 tests) | ✅ Done |
| #13 | Coverage report — 80% total coverage | ✅ Done |
