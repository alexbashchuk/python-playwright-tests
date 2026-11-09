from __future__ import annotations

import re

from playwright.sync_api import Locator, Page

from tests.ui.ui_support import PortfolioActions


class CertificateDialog:
    def __init__(self, page: Page, actions: PortfolioActions) -> None:
        self.page = page
        self.actions = actions

    @property
    def dialog(self) -> Locator:
        return self.page.get_by_role("dialog")

    def open(self, certificate: str) -> None:
        self.actions.click(
            self.page.get_by_role("region", name="Certifications").get_by_role(
                "button", name=certificate, exact=True
            )
        )

    def close_button(self) -> Locator:
        return self.dialog.get_by_role("button", name=re.compile("CLOSE"))

    def close(self) -> None:
        self.actions.click(self.close_button())
