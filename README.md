# RPL System — Recognition of Prior Learning
## Assignment 10: Class Implementation & Creational Design Patterns

---

## Language Choice

**Python 3.12** was chosen for the following reasons:
- Clean, readable syntax that maps closely to UML class diagrams.
- Strong support for OOP (inheritance, abstract base classes via `abc`).
- `threading` module enables thread-safe Singleton testing.
- `copy` module provides shallow and deep clone support for the Prototype pattern.
- `pytest` ecosystem offers excellent unit testing and coverage tooling.

---

## Project Structure

```
rpl_system/
├── src/                          # Core domain class implementations
│   ├── __init__.py
│   ├── student.py                # Student, StudentProfile
│   ├── module_request.py         # ModuleRequest, EvidenceDocument
│   ├── rpl_application.py        # RPLApplication, Notification
│   └── assessor.py               # Assessor, Admin, AcademicModule,
│                                 # AssessmentReport, AssessmentPanel
│
├── creational_patterns/          # All six creational design patterns
│   ├── __init__.py
│   ├── simple_factory.py         # Pattern 1: Simple Factory
│   ├── factory_method.py         # Pattern 2: Factory Method
│   ├── abstract_factory.py       # Pattern 3: Abstract Factory
│   ├── builder.py                # Pattern 4: Builder
│   ├── prototype.py              # Pattern 5: Prototype
│   └── singleton.py              # Pattern 6: Singleton
│
├── tests/
│   ├── __init__.py
│   └── test_creational_patterns.py  # 89 unit tests
│
├── README.md
└── CHANGELOG.md
```

---

## Running the Code

### Run all tests
```bash
pytest tests/test_creational_patterns.py -v
```

### Run with coverage report
```bash
pytest tests/test_creational_patterns.py --cov=src --cov=creational_patterns --cov-report=term-missing
```

### Run individual pattern demos
```bash
python creational_patterns/simple_factory.py
python creational_patterns/factory_method.py
python creational_patterns/abstract_factory.py
python creational_patterns/builder.py
python creational_patterns/prototype.py
python creational_patterns/singleton.py
```

---

## Creational Patterns — Rationale

| Pattern | RPL Use Case | Justification |
|---|---|---|
| **Simple Factory** | `RPLObjectFactory` creates `Notification` and `RPLApplication` objects by type string | Centralises object creation; callers don't need to know which concrete class to instantiate |
| **Factory Method** | `EvidenceVerifier` subclasses create the right `EvidenceProcessor` per document type (transcript, employer letter, certificate) | Delegates instantiation to subclasses; easy to add new document types without modifying existing code |
| **Abstract Factory** | `WebPortalFactory` and `MobilePortalFactory` each produce a consistent family of UI components (form, button, renderer) | Ensures UI components are always matched to the correct platform; client code is decoupled from concrete component classes |
| **Builder** | `RPLApplicationBuilder` constructs complex `RPLApplication` objects step-by-step via a fluent API | RPL applications have many optional parts (multiple modules, multiple evidence files); Builder prevents telescoping constructors and enforces BR-002 at `build()` time |
| **Prototype** | `ModuleRequestCache` stores template `ModuleRequest` prototypes and clones them per applicant | Avoids rebuilding frequently-used module configurations from scratch; clone then customise is faster than full construction |
| **Singleton** | `DatabaseConnection` ensures only one connection pool instance exists globally | Prevents connection pool exhaustion; all system components share one managed connection; thread-safe via double-checked locking |

---

## Key Design Decisions

### 1. Private Attributes with Properties (Encapsulation)
All class attributes are private (name-mangled with `__`). Access is controlled via Python `@property` decorators, mirroring the `-` (private) and `+` (public) UML visibility modifiers from the class diagram.

### 2. Business Rules Enforced in Methods
Business rules from Assignment 9 are enforced directly in method logic:
- **BR-001** → `Student.submit_application()` — max 3 active applications
- **BR-002** → `RPLApplicationBuilder.build()` and `RPLApplication.submit()` — minimum 1 module request
- **BR-003** → `ModuleRequest.has_verified_evidence()` — verified evidence required before approval
- **BR-004** → `RPLApplication.withdraw()` — only Pending/UnderReview status allowed
- **BR-005** → `AssessmentPanel.convene_panel()` — minimum quorum of 3
- **BR-007** → `AcademicModule.check_eligibility()` — NQF level check
- **BR-010** → `Admin.confirm_credit_grant()` — credits only after Admin confirmation

### 3. Inheritance: Admin extends Assessor
Implemented using Python class inheritance (`class Admin(Assessor)`). `Admin` inherits all assessor capabilities and adds management-level methods. Protected (`_`) attributes in `Assessor` are accessible to `Admin` without breaking encapsulation.

### 4. Composition for Application → ModuleRequest → EvidenceDocument
`RPLApplication.add_module_request()` stores `ModuleRequest` objects internally. `ModuleRequest.attach_evidence()` stores `EvidenceDocument` objects. Python's object lifecycle management handles cascading deletion naturally.

### 5. Thread-Safe Singleton
The `DatabaseConnection` Singleton uses **double-checked locking** with `threading.Lock()` to prevent race conditions during simultaneous first-instantiation by multiple threads. This is verified by the `test_thread_safety` unit test.

---

## Test Coverage Summary

| Module | Statements | Coverage |
|---|---|---|
| `src/module_request.py` | 87 | 94% |
| `src/rpl_application.py` | 103 | 91% |
| `src/student.py` | 105 | 84% |
| `src/assessor.py` | 179 | 77% |
| `creational_patterns/factory_method.py` | 66 | 83% |
| `creational_patterns/abstract_factory.py` | 81 | 80% |
| `creational_patterns/prototype.py` | 59 | 71% |
| `creational_patterns/singleton.py` | 82 | 70% |
| `creational_patterns/builder.py` | 60 | 65% |
| **TOTAL** | **859** | **80%** |

**89 tests — 89 passed — 0 failed**
