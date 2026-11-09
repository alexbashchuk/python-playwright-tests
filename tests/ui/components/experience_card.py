from __future__ import annotations

from playwright.sync_api import Locator, Page

from tests.ui.ui_support import PortfolioActions


class ExperienceCard:
    def __init__(
        self, page: Page, company: str, actions: PortfolioActions
    ) -> None:
        self.page = page
        self.company = company
        self.actions = actions

    @property
    def region(self) -> Locator:
        return self.page.get_by_role(
            "region", name=f"Experience at {self.company}", exact=True
        )

    @property
    def description_menu(self) -> Locator:
        return self.region.get_by_role("menu", name="Work description options")

    def choose_description_button(self) -> Locator:
        return self.region.get_by_role(
            "button", name="Choose work description", exact=True
        )

    def heading(self, name: str, level: int) -> Locator:
        return self.region.get_by_role("heading", name=name, level=level)

    def menu_option(self, option: str) -> Locator:
        return self.description_menu.get_by_role(
            "menuitem", name=option, exact=True
        )

    def open_description_menu(self) -> None:
        self.actions.click(self.choose_description_button())

    def select_description(self, option: str) -> None:
        self.actions.click(self.menu_option(option))

    def selected_description_button(self, label: str) -> Locator:
        return self.region.get_by_role("button", name=label, exact=True)

    def close_description_button(self) -> Locator:
        return self.region.get_by_role(
            "button", name="Close work description", exact=True
        )

    def close_description(self) -> None:
        self.actions.click(self.close_description_button())
