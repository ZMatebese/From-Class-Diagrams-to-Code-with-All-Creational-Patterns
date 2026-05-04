"""
Creational Pattern 5: Prototype
=====================================
Pattern: Prototype
Use Case: Clone pre-configured template objects to avoid expensive re-initialisation.

RPL Context:
  Certain ModuleRequest templates are used repeatedly across applicants
  (e.g., CS301 Data Structures always has the same module code, credits, NQF level).
  Instead of constructing and configuring each from scratch, we store prototype
  templates in a cache and clone them, then customise the clone per applicant.
"""
import sys, os, copy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from abc import ABC, abstractmethod
from src.module_request import ModuleRequest


# ── Prototype Interface ───────────────────────────────────────────────────────

class Prototype(ABC):
    """Interface that all cloneable prototypes must implement."""

    @abstractmethod
    def clone(self) -> "Prototype":
        pass


# ── Concrete Prototype ────────────────────────────────────────────────────────

class ModuleRequestPrototype(Prototype):
    """
    A ModuleRequest that can be cloned. Wraps ModuleRequest and adds
    clone capability to avoid costly repeated configuration.
    """

    def __init__(self, module_request_id: str, module_code: str,
                 module_name: str, credits: int, justification: str = ""):
        self._module_request_id = module_request_id
        self._module_code = module_code
        self._module_name = module_name
        self._credits = credits
        self._justification = justification

    def clone(self) -> "ModuleRequestPrototype":
        """Shallow clone — suitable since all fields are primitives."""
        return copy.copy(self)

    def deep_clone(self) -> "ModuleRequestPrototype":
        """Deep clone — for future use if nested mutable objects are added."""
        return copy.deepcopy(self)

    def customise(self, new_id: str, justification: str) -> "ModuleRequestPrototype":
        """Customise the clone for a specific applicant."""
        self._module_request_id = new_id
        self._justification = justification
        return self

    def to_module_request(self) -> ModuleRequest:
        """Convert this prototype to a concrete ModuleRequest."""
        return ModuleRequest(
            self._module_request_id,
            self._module_code,
            self._module_name,
            self._credits,
            self._justification
        )

    def __repr__(self):
        return (f"ModuleRequestPrototype(id={self._module_request_id}, "
                f"code={self._module_code}, credits={self._credits})")


# ── Prototype Cache ───────────────────────────────────────────────────────────

class ModuleRequestCache:
    """
    Stores pre-configured ModuleRequest prototypes and serves clones on demand.
    Avoids rebuilding common module configurations from scratch each time.
    """

    _cache: dict = {}

    @classmethod
    def load_cache(cls) -> None:
        """Pre-load commonly used module request templates."""
        templates = [
            ModuleRequestPrototype("TMPL-CS101", "CS101", "Introduction to Programming",
                                   12, ""),
            ModuleRequestPrototype("TMPL-CS301", "CS301", "Data Structures", 16, ""),
            ModuleRequestPrototype("TMPL-CS401", "CS401", "Software Engineering", 16, ""),
            ModuleRequestPrototype("TMPL-NET101", "NET101", "Computer Networks", 12, ""),
            ModuleRequestPrototype("TMPL-DB201", "DB201", "Database Design", 16, ""),
            ModuleRequestPrototype("TMPL-PM301", "PM301", "Project Management", 12, ""),
        ]
        for t in templates:
            cls._cache[t._module_code] = t

    @classmethod
    def get_clone(cls, module_code: str, new_id: str,
                  justification: str) -> ModuleRequestPrototype:
        """
        Return a cloned and customised ModuleRequest prototype.

        Args:
            module_code: The module code to retrieve the template for.
            new_id: The new unique ID for this applicant's request.
            justification: The applicant's personal justification.

        Returns:
            A customised clone of the stored prototype.
        """
        if module_code not in cls._cache:
            raise KeyError(
                f"No prototype found for module code '{module_code}'. "
                f"Available: {list(cls._cache.keys())}"
            )
        prototype = cls._cache[module_code].clone()
        return prototype.customise(new_id, justification)

    @classmethod
    def list_available(cls) -> list:
        return list(cls._cache.keys())


# ── Demo ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Prototype Pattern Demo ===\n")

    # Load templates into cache
    ModuleRequestCache.load_cache()
    print(f"Available templates: {ModuleRequestCache.list_available()}\n")

    # Clone CS301 for student 1
    mr1 = ModuleRequestCache.get_clone(
        "CS301", "MR-STU001-CS301",
        "Completed equivalent at Wits University in 2020."
    )
    print(f"Student 1 clone: {mr1}")

    # Clone CS301 for student 2 — completely independent object
    mr2 = ModuleRequestCache.get_clone(
        "CS301", "MR-STU002-CS301",
        "10 years industry experience in algorithm design."
    )
    print(f"Student 2 clone: {mr2}")

    # Verify they are different objects (not the same reference)
    print(f"\nSame object? {mr1 is mr2}")  # Expected: False
    print(f"Same module code? {mr1._module_code == mr2._module_code}")  # Expected: True

    # Convert to real ModuleRequest for use
    real_mr = mr1.to_module_request()
    print(f"\nConverted to ModuleRequest: {real_mr}")

    # Edge case: non-existent module code
    try:
        ModuleRequestCache.get_clone("INVALID", "MR-X", "test")
    except KeyError as e:
        print(f"\nExpected error: {e}")
