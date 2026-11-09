from __future__ import annotations

from urllib.parse import urljoin

from playwright.sync_api import Locator, Page, Response

from tests.ui.pages.portfolio_page import PortfolioPage


class ProjectDetailPage(PortfolioPage):
    def open_project(self, route: str) -> Response | None:
        return self.open(f"/#/{route}")

    def demo_link_inventory(self) -> list[tuple[str, str]]:
        raw_inventory = self.demo_links.locator("a").evaluate_all(
            "(links) => links.map((link) => [link.innerText.trim(), "
            "link.getAttribute('href')])"
        )
        return [
            (label, urljoin(self.page.url, href))
            for label, href in raw_inventory
            if label != "YouTube video"
        ]

    def video_link(self, destination: str) -> Locator:
        return self.demo_links.locator(f'a[href="{destination}"]')

    def fetch_destination(self, destination: str) -> tuple[int, str]:
        response = self.page.request.get(
            destination,
            timeout=20000,
            max_redirects=5,
        )
        try:
            return response.status, response.url
        finally:
            response.dispose()

    def open_video_link(self, link: Locator) -> tuple[Page, list[Response]]:
        responses: list[Response] = []

        def collect_navigation_response(response: Response) -> None:
            if response.request.is_navigation_request():
                responses.append(response)

        self.page.context.on("response", collect_navigation_response)
        try:
            popup = self.actions.click_popup(link)
            popup.wait_for_load_state("domcontentloaded")
            return popup, responses
        finally:
            self.page.context.remove_listener("response", collect_navigation_response)
