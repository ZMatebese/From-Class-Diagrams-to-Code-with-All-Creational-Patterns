"""
Creational Pattern 3: Abstract Factory
===========================================
Pattern: Abstract Factory
Use Case: Create families of related objects without specifying concrete classes.

RPL Context:
  The RPL portal supports two deployment environments: a full web portal
  (WebPortal) and a lightweight mobile portal (MobilePortal). Each environment
  needs its own family of UI components — forms, buttons, and report renderers —
  that look and behave consistently within that family.

  AbstractPortalFactory defines the interface; WebPortalFactory and
  MobilePortalFactory each produce their own consistent family of components.
"""
from abc import ABC, abstractmethod


# ── Abstract Products ─────────────────────────────────────────────────────────

class ApplicationForm(ABC):
    """Abstract product: the RPL application submission form."""
    @abstractmethod
    def render(self) -> str: pass
    @abstractmethod
    def validate(self, data: dict) -> bool: pass


class SubmitButton(ABC):
    """Abstract product: submit button widget."""
    @abstractmethod
    def render(self) -> str: pass
    @abstractmethod
    def on_click(self) -> str: pass


class ReportRenderer(ABC):
    """Abstract product: renders assessment reports."""
    @abstractmethod
    def render_report(self, report_data: dict) -> str: pass


# ── Concrete Products: Web Portal Family ──────────────────────────────────────

class WebApplicationForm(ApplicationForm):
    def render(self) -> str:
        return ("<form class='rpl-web-form'>"
                "<input type='text' name='module_code'/>"
                "<textarea name='justification'></textarea>"
                "</form>")

    def validate(self, data: dict) -> bool:
        return bool(data.get("module_code") and data.get("justification"))


class WebSubmitButton(SubmitButton):
    def render(self) -> str:
        return "<button class='btn-primary btn-lg'>Submit RPL Application</button>"

    def on_click(self) -> str:
        return "Web: POST /api/rpl/applications — full form payload submitted."


class WebReportRenderer(ReportRenderer):
    def render_report(self, report_data: dict) -> str:
        return (f"<div class='report-card'>"
                f"<h2>Assessment Report: {report_data.get('report_id')}</h2>"
                f"<p>Decision: <strong>{report_data.get('final_decision')}</strong></p>"
                f"<p>{report_data.get('comments')}</p>"
                f"</div>")


# ── Concrete Products: Mobile Portal Family ───────────────────────────────────

class MobileApplicationForm(ApplicationForm):
    def render(self) -> str:
        return ("[Mobile Form] Module Code: [____] | Justification: [____] "
                "| Attach Evidence: [📎]")

    def validate(self, data: dict) -> bool:
        # Mobile validation is lighter — only module code required
        return bool(data.get("module_code"))


class MobileSubmitButton(SubmitButton):
    def render(self) -> str:
        return "[TAP TO SUBMIT — RPL Application]"

    def on_click(self) -> str:
        return "Mobile: compressed payload sent via REST API with JWT auth."


class MobileReportRenderer(ReportRenderer):
    def render_report(self, report_data: dict) -> str:
        return (f"📋 Report {report_data.get('report_id')} | "
                f"Decision: {report_data.get('final_decision')} | "
                f"{report_data.get('comments', '')[:60]}...")


# ── Abstract Factory ──────────────────────────────────────────────────────────

class AbstractPortalFactory(ABC):
    """
    Abstract Factory: defines the interface for creating a family of
    RPL portal UI components.
    """

    @abstractmethod
    def create_application_form(self) -> ApplicationForm: pass

    @abstractmethod
    def create_submit_button(self) -> SubmitButton: pass

    @abstractmethod
    def create_report_renderer(self) -> ReportRenderer: pass


# ── Concrete Factories ────────────────────────────────────────────────────────

class WebPortalFactory(AbstractPortalFactory):
    """Creates the full-featured web portal component family."""

    def create_application_form(self) -> ApplicationForm:
        return WebApplicationForm()

    def create_submit_button(self) -> SubmitButton:
        return WebSubmitButton()

    def create_report_renderer(self) -> ReportRenderer:
        return WebReportRenderer()


class MobilePortalFactory(AbstractPortalFactory):
    """Creates the lightweight mobile portal component family."""

    def create_application_form(self) -> ApplicationForm:
        return MobileApplicationForm()

    def create_submit_button(self) -> SubmitButton:
        return MobileSubmitButton()

    def create_report_renderer(self) -> ReportRenderer:
        return MobileReportRenderer()


# ── Client ────────────────────────────────────────────────────────────────────

class RPLPortalClient:
    """
    Client: works with any portal factory without knowing concrete classes.
    Depends only on the AbstractPortalFactory interface.
    """

    def __init__(self, factory: AbstractPortalFactory):
        self._form = factory.create_application_form()
        self._button = factory.create_submit_button()
        self._renderer = factory.create_report_renderer()

    def render_portal(self, form_data: dict, report_data: dict) -> None:
        print("  Form:   ", self._form.render())
        print("  Valid:  ", self._form.validate(form_data))
        print("  Button: ", self._button.render())
        print("  Action: ", self._button.on_click())
        print("  Report: ", self._renderer.render_report(report_data))


# ── Demo ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Abstract Factory Demo ===\n")

    form_data = {"module_code": "CS301", "justification": "10 years industry experience"}
    report_data = {
        "report_id": "RPT-A001",
        "final_decision": "Approved",
        "comments": "Strong work experience portfolio."
    }

    for label, factory in [("Web Portal", WebPortalFactory()),
                            ("Mobile Portal", MobilePortalFactory())]:
        print(f"--- {label} ---")
        client = RPLPortalClient(factory)
        client.render_portal(form_data, report_data)
        print()
