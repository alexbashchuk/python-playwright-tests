from __future__ import annotations

from typing import Any

from playwright.sync_api import Locator, Page, Response

from tests.ui.components.certificate_dialog import CertificateDialog
from tests.ui.components.experience_card import ExperienceCard
from tests.ui.ui_support import PortfolioActions


class PortfolioPage:
    def __init__(self, page: Page, actions: PortfolioActions) -> None:
        self.page = page
        self.actions = actions

    def open(self, path: str = "/") -> Response | None:
        return self.page.goto(path)

    def heading(
        self, name: str, level: int | None = None, *, target: Page | None = None
    ) -> Locator:
        page = target or self.page
        options: dict[str, Any] = {"name": name}
        if level is not None:
            options["level"] = level
        return page.get_by_role("heading", **options)

    def region(self, name: str, *, exact: bool = False) -> Locator:
        return self.page.get_by_role("region", name=name, exact=exact)

    def button(
        self, name: str, *, exact: bool = False, target: Page | None = None
    ) -> Locator:
        return (target or self.page).get_by_role("button", name=name, exact=exact)

    def link(
        self, name: str, *, exact: bool = False, target: Page | None = None
    ) -> Locator:
        return (target or self.page).get_by_role("link", name=name, exact=exact)

    def link_within(
        self, within: Locator, name: str, *, exact: bool = False
    ) -> Locator:
        return within.get_by_role("link", name=name, exact=exact)

    def text(self, value: str, *, exact: bool = False) -> Locator:
        return self.page.get_by_text(value, exact=exact)

    def paragraphs(self, within: Locator) -> Locator:
        return within.locator("p")

    def list_items(self, within: Locator) -> Locator:
        return within.get_by_role("listitem")

    def links_within(self, within: Locator) -> Locator:
        return within.get_by_role("link")

    def scroll_into_view(self, locator: Locator) -> None:
        locator.scroll_into_view_if_needed()

    @property
    def profile(self) -> Locator:
        return self.region("Profile")

    @property
    def professional_summary(self) -> Locator:
        return self.region("Professional Summary")

    @property
    def experience(self) -> Locator:
        return self.region("Professional Experience")

    @property
    def education(self) -> Locator:
        return self.region("Education")

    @property
    def certifications(self) -> Locator:
        return self.region("Certifications")

    @property
    def projects(self) -> Locator:
        return self.region("Automation Projects Examples")

    @property
    def demo_links(self) -> Locator:
        return self.region("Demo Links")

    def experience_card(self, company: str) -> ExperienceCard:
        return ExperienceCard(self.page, company, self.actions)

    def certificate_dialog(self) -> CertificateDialog:
        return CertificateDialog(self.page, self.actions)

    def all_headings(self, level: int) -> list[str]:
        return self.page.get_by_role("heading", level=level).all_text_contents()

    def open_project_link(self, label: str) -> None:
        self.actions.click(self.link(label, exact=True))

    def return_home(self) -> None:
        self.actions.click(self.button("⌂ Home"))

    def set_viewport(self, width: int, height: int) -> None:
        self.page.set_viewport_size({"width": width, "height": height})

    def viewport_metrics(self) -> dict[str, float]:
        return self.page.evaluate(
            "() => ({"
            "scrollY: window.scrollY, scrollHeight: document.documentElement.scrollHeight, "
            "innerHeight: window.innerHeight, clientWidth: document.documentElement.clientWidth, "
            "scrollWidth: document.documentElement.scrollWidth"
            "})"
        )

    def is_in_viewport(self, locator: Locator) -> bool:
        return locator.evaluate(
            "(element) => {"
            "const rect = element.getBoundingClientRect();"
            "return rect.bottom > 0 && rect.top < window.innerHeight && "
            "rect.right > 0 && rect.left < window.innerWidth;"
            "}"
        )

    def main_region_labels(self) -> set[str]:
        return set(
            self.page.locator("main [aria-label]").evaluate_all(
                "(elements) => elements.map((element) => "
                "element.getAttribute('aria-label'))"
            )
        )

    def visible_main_region_labels(self) -> set[str]:
        return set(
            self.page.locator("main [aria-label]").evaluate_all(
                "(elements) => elements.filter((element) => {"
                "const rect = element.getBoundingClientRect();"
                "return rect.bottom > 0 && rect.top < window.innerHeight;"
                "}).map((element) => element.getAttribute('aria-label'))"
            )
        )

    def visible_main_region_labels_after_scroll(self) -> list[str]:
        return self.page.locator("main [aria-label]").evaluate_all(
            "(elements) => elements.filter((element) => {"
            "const rect = element.getBoundingClientRect();"
            "return rect.bottom > 0 && rect.top < window.innerHeight;"
            "}).map((element) => element.getAttribute('aria-label'))"
        )

    def scroll_to(self, y: float) -> None:
        self.page.evaluate(
            "(y) => window.scrollTo({top: y, behavior: 'instant'})", y
        )

    def scroll_to_top(self) -> None:
        self.page.evaluate("() => window.scrollTo({top: 0, behavior: 'instant'})")
        self.page.wait_for_function("() => window.scrollY === 0")

    def scroll_to_bottom(self) -> None:
        self.page.evaluate(
            "() => window.scrollTo({top: document.documentElement.scrollHeight, "
            "behavior: 'instant'})"
        )
        self.page.wait_for_function(
            "() => Math.abs(window.scrollY - "
            "(document.documentElement.scrollHeight - window.innerHeight)) <= 2"
        )

    def wait_for_scroll_advance(self, previous: float, target: float) -> None:
        self.page.wait_for_function(
            "(state) => window.scrollY > state.previous || "
            "window.scrollY >= state.target - 2",
            arg={"previous": previous, "target": target},
        )

    def keyboard_press(self, key: str) -> None:
        self.page.keyboard.press(key)

    def viewport_width(self) -> int:
        return self.page.evaluate("window.innerWidth")

    def scroll_y(self) -> float:
        return self.page.evaluate("window.scrollY")

    def page_title(self, target: Page | None = None) -> str:
        return (target or self.page).title()

    def observe_projects_button(self) -> tuple[str, float, str, float, bool]:
        button = self.button("My QA Automation Demo Projects", exact=True)
        before_url = self.page.url
        before_scroll_y = self.scroll_y()
        self.actions.click(button)
        after_url = self.page.url
        after_scroll_y = self.scroll_y()
        projects_visible = self.projects.is_visible()
        return before_url, before_scroll_y, after_url, after_scroll_y, projects_visible
