from __future__ import annotations

import math
import re
from urllib.parse import urlparse

import pytest
from playwright.sync_api import Page, expect

from tests.ui.data.portfolio_data import (
    COMPANIES,
    DEMO_LINKS,
    PROJECTS,
    SECTION_HEADINGS,
    YOUTUBE_VIDEOS,
    destination_slug,
    heading_slug,
    inventory_for_route,
    project_heading_for_route,
    youtube_url,
)
from tests.ui.pages.portfolio_page import PortfolioPage
from tests.ui.pages.project_detail_page import ProjectDetailPage
from tests.ui.ui_support import PortfolioActions, StepRecorder


def test_portfolio_primary_content(page: Page, ui_steps: StepRecorder, portfolio_actions: PortfolioActions) -> None:
    portfolio = PortfolioPage(page, portfolio_actions)
    ui_steps.configure("PORT-001")
    ui_steps.plan(
        [
            ("Open portfolio home", "Root page responds successfully"),
            ("Verify profile and summary", "Name, role, contact, citizenship, summary, and title are present"),
        ]
    )
    with ui_steps.step("Open portfolio home", "Root page responds successfully") as step:
        response = portfolio.open()
        assert response is not None
        assert response.ok
        step["actual"] = f"HTTP {response.status}; URL {page.url}"

    with ui_steps.step(
        "Verify profile and summary",
        "Name, role, contact, citizenship, summary, and title are present",
    ) as step:
        expect(portfolio.heading("Alex Boschuk", level=1, target=page)).to_be_visible()
        expect(portfolio.profile).to_contain_text("Senior SDET / QA Automation Engineer")
        expect(portfolio.profile).to_contain_text("Boca Raton, FL")
        expect(portfolio.profile).to_contain_text("347-495-4965")
        expect(portfolio.profile).to_contain_text("bostchuk@gmail.com")
        expect(portfolio.profile).to_contain_text("US Citizen")
        expect(portfolio.paragraphs(portfolio.professional_summary)).to_be_visible()
        expect(portfolio.paragraphs(portfolio.professional_summary)).to_have_text(
            re.compile(r"\S+")
        )
        expect(page).to_have_title("myportfolio")
        step["actual"] = (
            "Profile and summary content visible; "
            f"title={portfolio.page_title()!r}; page_url={page.url}"
        )


def test_portfolio_sections_and_content(
    page: Page, ui_steps: StepRecorder, portfolio_actions: PortfolioActions
) -> None:
    portfolio = PortfolioPage(page, portfolio_actions)
    ui_steps.configure("PORT-002")
    ui_steps.plan(
        [
            ("Open landing page", "The landing page renders"),
            ("Read sections in order", "All six non-profile section headings are reachable in order"),
            ("Verify experience, education, certifications, projects, and footer", "All observed content is present"),
        ]
    )
    with ui_steps.step("Open landing page", "The landing page renders") as step:
        response = portfolio.open()
        assert response is not None and response.ok
        step["actual"] = f"HTTP {response.status}; URL {page.url}"

    with ui_steps.step(
        "Read sections in order",
        "All six non-profile section headings are reachable in order",
    ) as step:
        actual_headings = portfolio.all_headings(level=2)
        assert tuple(actual_headings) == SECTION_HEADINGS
        for heading_text in SECTION_HEADINGS:
            heading = portfolio.heading(heading_text, level=2)
            portfolio.scroll_into_view(heading)
            expect(heading).to_be_visible()
        step["actual"] = f"Ordered headings: {actual_headings!r}"

    with ui_steps.step(
        "Verify experience, education, certifications, projects, and footer",
        "All observed content is present",
    ) as step:
        for company in COMPANIES:
            expect(portfolio.heading(company, level=3, target=page)).to_be_visible()
        expect(portfolio.list_items(portfolio.education)).to_have_count(2)
        for certificate in ("AS1", "AS2", "TDS1", "TDS2", "qTest", "CTFL"):
            expect(portfolio.button(certificate, target=page)).to_be_visible()
        expect(portfolio.list_items(portfolio.projects)).to_have_count(6)
        expect(portfolio.text("© 2026 Alex Boschuk", exact=True)).to_be_visible()
        step["actual"] = (
            f"{len(COMPANIES)} employers, 2 education items, 6 certificate buttons, "
            "6 projects, and footer confirmed"
        )


@pytest.mark.parametrize(
    ("route", "link_label", "heading_text"),
    [
        pytest.param(route, label, heading, id=f"PORT-003-{route}")
        for route, label, heading in PROJECTS
    ],
)
def test_project_navigation_and_home_return(
    page: Page,
    ui_steps: StepRecorder,
    portfolio_actions: PortfolioActions,
    route: str,
    link_label: str,
    heading_text: str,
) -> None:
    portfolio = PortfolioPage(page, portfolio_actions)
    ui_steps.configure(
        "PORT-003",
        {"project": route, "project_link": link_label, "expected_heading": heading_text},
    )
    ui_steps.plan(
        [
            ("Open portfolio home", "The landing page is available"),
            ("Open project detail", f"Route #/{route} and heading {heading_text!r} render"),
            ("Return home", "Home returns to /#/ and restores portfolio content"),
        ]
    )
    with ui_steps.step("Open portfolio home", "The landing page is available") as step:
        response = portfolio.open()
        assert response is not None and response.ok
        step["actual"] = f"HTTP {response.status}; URL {page.url}"

    with ui_steps.step(
        "Open project detail", f"Route #/{route} and heading {heading_text!r} render"
    ) as step:
        portfolio.open_project_link(link_label)
        heading = portfolio.heading(heading_text, level=1)
        expect(heading).to_be_visible()
        assert page.url.endswith(f"#/{route}")
        step["actual"] = (
            f"heading={heading.inner_text()!r}; URL={page.url}; "
            f"demo_pause_ms={portfolio_actions.last_click_delay_ms}"
        )

    with ui_steps.step(
        "Return home", "Home returns to /#/ and restores portfolio content"
    ) as step:
        portfolio.return_home()
        expect(portfolio.heading("Alex Boschuk", level=1)).to_be_visible()
        expect(portfolio.projects).to_be_visible()
        assert page.url.endswith("#/")
        step["actual"] = (
            f"URL={page.url}; profile and projects visible; "
            f"demo_pause_ms={portfolio_actions.last_click_delay_ms}"
        )


def test_portfolio_project_demo_link_destinations(
    page: Page, ui_steps: StepRecorder, portfolio_actions: PortfolioActions
) -> None:
    detail = ProjectDetailPage(page, portfolio_actions)
    ui_steps.configure("PORT-004", {"project": "portfolio-github"})
    ui_steps.plan(
        [
            ("Open portfolio project detail", "The portfolio GitHub project page renders"),
            ("Check repository destination", "GitHub repository has the exact expected URL"),
            ("Check live-site destination", "GitHub Pages site has the exact expected URL"),
        ]
    )
    with ui_steps.step(
        "Open portfolio project detail", "The portfolio GitHub project page renders"
    ) as step:
        response = detail.open_project("portfolio-github")
        assert response is not None and response.ok
        expect(detail.heading("GitHub Portfolio Website", level=1)).to_be_visible()
        step["actual"] = f"HTTP {response.status}; URL {page.url}"

    expected_links = (
        ("GitHub repository", "https://github.com/alexbashchuk/alexbashchuk.github.io"),
        ("GitHub Pages site", "https://alexbashchuk.github.io"),
    )
    for label, expected_url in expected_links:
        with ui_steps.step(
            f"Check {label} destination", f"Exact href is {expected_url}"
        ) as step:
            link = detail.link_within(detail.demo_links, label, exact=True)
            expect(link).to_be_visible()
            actual_url = link.get_attribute("href")
            assert actual_url == expected_url
            step["actual"] = f"label={label!r}; href={actual_url!r}"


@pytest.mark.parametrize(
    ("company", "option", "expected_heading", "expected_button"),
    [
        pytest.param(
            company,
            option,
            heading,
            f"Work description: {option}",
            id=f"PORT-005-{heading_slug(company)}-{heading_slug(option)}",
        )
        for company in COMPANIES
        for option, heading in (
            ("Short Details", "Work description"),
            ("Long Story", "Work story"),
        )
    ],
)
def test_company_work_description(
    page: Page,
    ui_steps: StepRecorder,
    portfolio_actions: PortfolioActions,
    company: str,
    option: str,
    expected_heading: str,
    expected_button: str,
) -> None:
    portfolio = PortfolioPage(page, portfolio_actions)
    card = portfolio.experience_card(company)
    ui_steps.configure(
        "PORT-005",
        {
            "company": company,
            "description_option": option,
            "expected_heading": expected_heading,
        },
    )
    ui_steps.plan(
        [
            ("Open landing page", "Company work descriptions are available"),
            ("Find exact company region", f"One region is labeled Experience at {company!r}"),
            ("Open description menu", "Short Details and Long Story are available"),
            (f"Select {option}", f"Heading is {expected_heading!r} and selected label is {expected_button!r}"),
            ("Close description", "Content is hidden and the collapsed button is restored"),
        ]
    )
    with ui_steps.step("Open landing page", "Company work descriptions are available") as step:
        response = portfolio.open()
        assert response is not None and response.ok
        step["actual"] = f"HTTP {response.status}; URL {page.url}"

    with ui_steps.step(
        "Find exact company region", f"One region is labeled Experience at {company!r}"
    ) as step:
        expect(card.region).to_have_count(1)
        portfolio.scroll_into_view(card.region)
        expect(card.heading(company, level=3)).to_be_visible()
        step["actual"] = f"One matching employer region found: Experience at {company}"

    with ui_steps.step(
        "Open description menu", "Short Details and Long Story are available"
    ) as step:
        card.open_description_menu()
        expect(card.menu_option("Short Details")).to_be_visible()
        expect(card.menu_option("Long Story")).to_be_visible()
        step["actual"] = (
            "Both menu options are visible; "
            f"demo_pause_ms={portfolio_actions.last_click_delay_ms}"
        )

    with ui_steps.step(
        f"Select {option}",
        f"Heading is {expected_heading!r} and selected label is {expected_button!r}",
    ) as step:
        card.select_description(option)
        expect(card.heading(expected_heading, level=4)).to_be_visible()
        selected_button = card.selected_description_button(expected_button)
        expect(selected_button).to_be_visible()
        step["actual"] = (
            f"heading={expected_heading!r}; button={selected_button.inner_text()!r}; "
            f"demo_pause_ms={portfolio_actions.last_click_delay_ms}"
        )

    with ui_steps.step(
        "Close description", "Content is hidden and the collapsed button is restored"
    ) as step:
        card.close_description()
        expect(card.heading(expected_heading, level=4)).to_have_count(0)
        expect(card.choose_description_button()).to_be_visible()
        step["actual"] = (
            "Selected heading hidden; collapsed button restored; "
            f"demo_pause_ms={portfolio_actions.last_click_delay_ms}"
        )


def test_certificate_dialog_opens_and_closes(
    page: Page,
    ui_steps: StepRecorder,
    portfolio_actions: PortfolioActions,
) -> None:
    portfolio = PortfolioPage(page, portfolio_actions)
    certificate_dialog = portfolio.certificate_dialog()
    ui_steps.configure("PORT-006")
    ui_steps.plan(
        [
            ("Open landing page", "Certification controls are available"),
            ("Open AS1 dialog", "A dialog and its close button are visible"),
            ("Close dialog", "The certificate dialog is dismissed"),
        ]
    )
    with ui_steps.step("Open landing page", "Certification controls are available") as step:
        response = portfolio.open()
        assert response is not None and response.ok
        step["actual"] = f"HTTP {response.status}; URL {page.url}"

    with ui_steps.step(
        "Open AS1 dialog", "A dialog and its close button are visible"
    ) as step:
        certificate_dialog.open("AS1")
        expect(certificate_dialog.dialog).to_be_visible()
        expect(certificate_dialog.close_button()).to_be_visible()
        step["actual"] = (
            "Dialog visible; explicit close button available; "
            f"demo_pause_ms={portfolio_actions.last_click_delay_ms}"
        )

    with ui_steps.step("Close dialog", "The certificate dialog is dismissed") as step:
        certificate_dialog.close()
        expect(certificate_dialog.dialog).to_have_count(0)
        step["actual"] = (
            "Dialog removed after explicit CLOSE activation; "
            f"demo_pause_ms={portfolio_actions.last_click_delay_ms}"
        )


@pytest.mark.portfolio_review
def test_demo_projects_button_observation_only(
    page: Page,
    ui_steps: StepRecorder,
    portfolio_actions: PortfolioActions,
) -> None:
    portfolio = PortfolioPage(page, portfolio_actions)
    ui_steps.configure(
        "PORT-007",
        review_note=(
            "Intended action is unconfirmed. This test records the current observed "
            "click result only and does not assert navigation or scrolling behavior."
        ),
    )
    ui_steps.plan(
        [
            ("Open landing page", "The technical-skills button is available"),
            ("Record button behavior for review", "Observation only; no acceptance behavior is asserted"),
        ]
    )
    with ui_steps.step("Open landing page", "The technical-skills button is available") as step:
        response = portfolio.open()
        assert response is not None and response.ok
        step["actual"] = f"HTTP {response.status}; URL {page.url}"

    button = portfolio.button("My QA Automation Demo Projects", exact=True)
    with ui_steps.step(
        "Record button behavior for review",
        "Observation only; no acceptance behavior is asserted",
    ) as step:
        expect(button).to_be_visible()
        before_url, before_scroll_y, after_url, after_scroll_y, projects_visible = (
            portfolio.observe_projects_button()
        )
        step["actual"] = (
            f"before_url={before_url}; after_url={after_url}; "
            f"scrollY_before={before_scroll_y}; scrollY_after={after_scroll_y}; "
            f"projects_region_visible={projects_visible}; behavior unconfirmed; "
            f"demo_pause_ms={portfolio_actions.last_click_delay_ms}"
        )


def test_landing_page_narrow_viewport(
    page: Page, ui_steps: StepRecorder, portfolio_actions: PortfolioActions
) -> None:
    portfolio = PortfolioPage(page, portfolio_actions)
    ui_steps.configure("PORT-008", {"viewport": "390x844"})
    ui_steps.plan(
        [
            ("Set narrow viewport and open landing page", "Viewport is 390x844 and page loads"),
            ("Verify content sections at narrow width", "Profile and all landing sections remain reachable"),
            ("Check horizontal overflow", "Document width does not exceed the viewport beyond 2px"),
        ]
    )
    with ui_steps.step(
        "Set narrow viewport and open landing page", "Viewport is 390x844 and page loads"
    ) as step:
        portfolio.set_viewport(390, 844)
        response = portfolio.open()
        assert response is not None and response.ok
        metrics = portfolio.viewport_metrics()
        assert metrics["innerHeight"] == 844
        step["actual"] = f"HTTP {response.status}; metrics={metrics}"

    with ui_steps.step(
        "Verify content sections at narrow width",
        "Profile and all landing sections remain reachable",
    ) as step:
        expect(portfolio.heading("Alex Boschuk", level=1)).to_be_visible()
        expect(portfolio.profile).to_contain_text("bostchuk@gmail.com")
        for section_name in SECTION_HEADINGS:
            heading = portfolio.heading(section_name, level=2)
            portfolio.scroll_into_view(heading)
            expect(heading).to_be_visible()
        step["actual"] = (
            f"All section headings reachable at viewport width "
            f"{portfolio.viewport_width()}"
        )

    with ui_steps.step(
        "Check horizontal overflow", "Document width does not exceed the viewport beyond 2px"
    ) as step:
        metrics = portfolio.viewport_metrics()
        assert metrics["scrollWidth"] <= metrics["clientWidth"] + 2
        step["actual"] = (
            f"scrollWidth={metrics['scrollWidth']}; clientWidth={metrics['clientWidth']}"
        )


def test_project_detail_narrow_viewport(
    page: Page, ui_steps: StepRecorder, portfolio_actions: PortfolioActions
) -> None:
    detail = ProjectDetailPage(page, portfolio_actions)
    ui_steps.configure("PORT-009", {"project": "portfolio-github", "viewport": "390x844"})
    ui_steps.plan(
        [
            ("Set narrow viewport and open project", "Portfolio detail page loads at 390x844"),
            ("Verify detail-page sections", "Heading, description, demo links, and tech stack are reachable"),
            ("Check horizontal overflow", "Document width does not exceed the viewport beyond 2px"),
        ]
    )
    with ui_steps.step(
        "Set narrow viewport and open project", "Portfolio detail page loads at 390x844"
    ) as step:
        detail.set_viewport(390, 844)
        response = detail.open_project("portfolio-github")
        assert response is not None and response.ok
        heading = detail.heading("GitHub Portfolio Website", level=1)
        expect(heading).to_be_visible()
        step["actual"] = f"HTTP {response.status}; heading={heading.inner_text()!r}; URL={page.url}"

    with ui_steps.step(
        "Verify detail-page sections",
        "Heading, description, demo links, and tech stack are reachable",
    ) as step:
        for section_name in ("Project Description", "Demo Links", "Tech Stack"):
            section = detail.region(section_name)
            detail.scroll_into_view(section)
            expect(section).to_be_visible()
        expect(detail.link("GitHub repository")).to_be_visible()
        expect(detail.link("GitHub Pages site")).to_be_visible()
        expect(detail.button("⌂ Home")).to_be_visible()
        step["actual"] = "Project content, links, tech stack, and Home are reachable"

    with ui_steps.step(
        "Check horizontal overflow", "Document width does not exceed the viewport beyond 2px"
    ) as step:
        metrics = detail.viewport_metrics()
        assert metrics["scrollWidth"] <= metrics["clientWidth"] + 2
        step["actual"] = (
            f"scrollWidth={metrics['scrollWidth']}; clientWidth={metrics['clientWidth']}"
        )


def test_keyboard_navigation_and_work_menu(
    page: Page, ui_steps: StepRecorder, portfolio_actions: PortfolioActions
) -> None:
    portfolio = PortfolioPage(page, portfolio_actions)
    card = portfolio.experience_card("Williams Companies")
    ui_steps.configure("PORT-010")
    ui_steps.plan(
        [
            ("Open fresh landing page", "No control was clicked before keyboard navigation"),
            ("Tab to projects button", "First Tab focuses My QA Automation Demo Projects"),
            ("Tab to Williams control", "Second Tab focuses Choose work description"),
            ("Open work menu with Enter", "Menu options appear after keyboard activation"),
            ("Focus and select Short Details", "Tab focuses Short Details and Enter selects it"),
        ]
    )
    with ui_steps.step(
        "Open fresh landing page", "No control was clicked before keyboard navigation"
    ) as step:
        response = portfolio.open()
        assert response is not None and response.ok
        step["actual"] = f"HTTP {response.status}; URL={page.url}"

    projects_button = portfolio.button("My QA Automation Demo Projects", exact=True)
    with ui_steps.step(
        "Tab to projects button", "First Tab focuses My QA Automation Demo Projects"
    ) as step:
        portfolio.keyboard_press("Tab")
        expect(projects_button).to_be_focused()
        step["actual"] = "Focused My QA Automation Demo Projects"

    choose_button = card.choose_description_button()
    with ui_steps.step(
        "Tab to Williams control", "Second Tab focuses Choose work description"
    ) as step:
        portfolio.keyboard_press("Tab")
        expect(choose_button).to_be_focused()
        step["actual"] = "Focused Williams Companies work-description control"

    with ui_steps.step(
        "Open work menu with Enter", "Menu options appear after keyboard activation"
    ) as step:
        portfolio.keyboard_press("Enter")
        expect(card.menu_option("Short Details")).to_be_visible()
        expect(card.menu_option("Long Story")).to_be_visible()
        step["actual"] = "Both work-description menu options are visible"

    short_details = card.menu_option("Short Details")
    with ui_steps.step(
        "Focus and select Short Details", "Tab focuses Short Details and Enter selects it"
    ) as step:
        portfolio.keyboard_press("Tab")
        expect(short_details).to_be_focused()
        portfolio.keyboard_press("Enter")
        expect(portfolio.heading("Work description", level=4)).to_be_visible()
        expect(
            card.selected_description_button("Work description: Short Details")
        ).to_be_visible()
        step["actual"] = "Short Details focused and selected; Work description content visible"


@pytest.mark.parametrize(
    ("route", "link_label", "heading_text"),
    [
        pytest.param(route, label, heading, id=f"PORT-011-{route}")
        for route, label, heading in PROJECTS
    ],
)
def test_project_detail_scrolling(
    page: Page,
    ui_steps: StepRecorder,
    portfolio_actions: PortfolioActions,
    route: str,
    link_label: str,
    heading_text: str,
) -> None:
    detail = ProjectDetailPage(page, portfolio_actions)
    ui_steps.configure(
        "PORT-011",
        {
            "project": route,
            "project_link": link_label,
            "expected_heading": heading_text,
            "viewport": "390x844",
        },
    )
    ui_steps.plan(
        [
            ("Set viewport and open project", "Project route loads at 390x844"),
            ("Verify expected project heading", f"Heading is {heading_text!r}"),
            ("Reset to document top", "scrollY is zero and scroll dimensions are recorded"),
        ]
    )
    with ui_steps.step(
        "Set viewport and open project", "Project route loads at 390x844"
    ) as step:
        detail.set_viewport(390, 844)
        response = detail.open_project(route)
        assert response is not None and response.ok
        step["actual"] = f"HTTP {response.status}; URL={page.url}"

    with ui_steps.step(
        "Verify expected project heading", f"Heading is {heading_text!r}"
    ) as step:
        heading = detail.heading(heading_text, level=1)
        expect(heading).to_be_visible()
        step["actual"] = f"heading={heading.inner_text()!r}; URL={page.url}"

    with ui_steps.step(
        "Reset to document top", "scrollY is zero and scroll dimensions are recorded"
    ) as step:
        detail.scroll_to_top()
        initial = detail.viewport_metrics()
        assert initial["scrollY"] == 0
        step["actual"] = f"initial_metrics={initial}"

    all_region_labels = detail.main_region_labels()
    seen_region_labels = detail.visible_main_region_labels()
    remaining = max(0, initial["scrollHeight"] - initial["innerHeight"])
    increment = initial["innerHeight"] * 0.8
    scroll_steps = math.ceil(remaining / increment) if remaining else 0
    assert scroll_steps <= 50, f"Unexpectedly many scroll iterations: {scroll_steps}"
    if scroll_steps == 0:
        with ui_steps.step(
            "Page fits viewport",
            "All rendered project content fits without requiring positive scrolling",
        ) as step:
            assert initial["scrollHeight"] <= initial["innerHeight"] + 2
            assert all_region_labels.issubset(seen_region_labels)
            step["actual"] = f"content fits; initial_metrics={initial}"

    scroll_plan = [
        (f"Scroll increment {index}", "Viewport position advances by a bounded increment")
        for index in range(1, scroll_steps + 1)
    ]
    scroll_plan.extend(
        [
            ("Reach Demo Links", "Demo Links section intersects the viewport"),
            ("Verify all project sections", "Every labeled section intersects a viewport during the bounded scroll"),
            ("Reach document bottom", "scrollY reaches maximum scroll within 2px"),
            ("Reach last content", "Footer is reachable and intersects the viewport"),
            ("Reach Home control", "Home is reachable and intersects the viewport"),
            ("Return to top", "scrollY returns to zero and project heading is visible"),
            ("Check horizontal overflow", "Document width is within 2px of viewport width"),
        ]
    )
    ui_steps.plan(scroll_plan)

    if scroll_steps:
        before = 0.0
        for index in range(1, scroll_steps + 1):
            target_y = min(remaining, index * increment)
            with ui_steps.step(
                f"Scroll increment {index}", "Viewport position advances by a bounded increment"
            ) as step:
                detail.scroll_to(target_y)
                detail.wait_for_scroll_advance(before, target_y)
                metrics = detail.viewport_metrics()
                assert metrics["scrollY"] > before
                assert metrics["scrollY"] <= target_y + 2
                regions_in_view = detail.visible_main_region_labels_after_scroll()
                seen_region_labels.update(regions_in_view)
                step["actual"] = (
                    f"metrics={metrics}; regions_intersecting_viewport={regions_in_view}"
                )
                before = metrics["scrollY"]

    with ui_steps.step(
        "Verify all project sections",
        "Every labeled section intersects a viewport during the bounded scroll",
    ) as step:
        assert all_region_labels.issubset(seen_region_labels), (
            f"Sections not reached during scrolling: "
            f"{sorted(all_region_labels - seen_region_labels)!r}"
        )
        step["actual"] = (
            f"All {len(all_region_labels)} labeled sections entered the viewport: "
            f"{sorted(seen_region_labels)!r}"
        )

    with ui_steps.step(
        "Reach Demo Links", "Demo Links section intersects the viewport"
    ) as step:
        detail.scroll_into_view(detail.demo_links)
        expect(detail.demo_links).to_be_visible()
        assert detail.is_in_viewport(detail.demo_links)
        links = detail.links_within(detail.demo_links).count()
        assert links > 0
        step["actual"] = f"Demo Links intersects viewport; visible links={links}"

    with ui_steps.step(
        "Reach document bottom", "scrollY reaches maximum scroll within 2px"
    ) as step:
        detail.scroll_to_bottom()
        bottom = detail.viewport_metrics()
        maximum_scroll = bottom["scrollHeight"] - bottom["innerHeight"]
        assert abs(bottom["scrollY"] - maximum_scroll) <= 2
        step["actual"] = f"bottom_metrics={bottom}; maximum_scroll={maximum_scroll}"

    footer = detail.text("© 2026 Alex Bachuk", exact=True)
    with ui_steps.step(
        "Reach last content", "Footer is reachable and intersects the viewport"
    ) as step:
        detail.scroll_into_view(footer)
        expect(footer).to_be_visible()
        assert detail.is_in_viewport(footer)
        step["actual"] = "Footer intersects the viewport at the end of the document"

    home_button = detail.button("⌂ Home")
    with ui_steps.step(
        "Reach Home control", "Home is reachable and intersects the viewport"
    ) as step:
        detail.scroll_into_view(home_button)
        expect(home_button).to_be_visible()
        assert detail.is_in_viewport(home_button)
        step["actual"] = "Home control brought into viewport and visible"

    with ui_steps.step(
        "Return to top", "scrollY returns to zero and project heading is visible"
    ) as step:
        detail.scroll_to_top()
        expect(detail.heading(heading_text, level=1)).to_be_visible()
        assert detail.is_in_viewport(detail.heading(heading_text, level=1))
        step["actual"] = f"scrollY={detail.viewport_metrics()['scrollY']}; heading visible"

    with ui_steps.step(
        "Check horizontal overflow", "Document width is within 2px of viewport width"
    ) as step:
        metrics = detail.viewport_metrics()
        assert metrics["scrollWidth"] <= metrics["clientWidth"] + 2
        step["actual"] = (
            f"scrollWidth={metrics['scrollWidth']}; clientWidth={metrics['clientWidth']}"
        )


@pytest.mark.parametrize(
    ("route", "link_label", "destination"),
    [
        pytest.param(
            route,
            label,
            destination,
            id=f"PORT-012-{route}-{heading_slug(label)}-{destination_slug(destination)}",
        )
        for route, label, destination in DEMO_LINKS
    ],
)
def test_project_demo_link_http_availability(
    page: Page,
    ui_steps: StepRecorder,
    portfolio_actions: PortfolioActions,
    route: str,
    link_label: str,
    destination: str,
) -> None:
    detail = ProjectDetailPage(page, portfolio_actions)
    project_heading = project_heading_for_route(route)
    ui_steps.configure(
        "PORT-012",
        {"project": route, "link_label": link_label, "original_url": destination},
    )
    ui_steps.plan(
        [
            ("Open project and Demo Links", "Project and Demo Links section are available"),
            ("Validate frozen link inventory", "The target label and exact destination are present"),
            ("GET destination", "Final HTTP response is 2xx with no more than five redirects"),
        ]
    )
    with ui_steps.step(
        "Open project and Demo Links", "Project and Demo Links section are available"
    ) as step:
        response = detail.open_project(route)
        assert response is not None and response.ok
        expect(detail.heading(project_heading, level=1)).to_be_visible()
        detail.scroll_into_view(detail.demo_links)
        expect(detail.demo_links).to_be_visible()
        step["actual"] = f"HTTP {response.status}; URL={page.url}"

    with ui_steps.step(
        "Validate frozen link inventory",
        "The target label and exact destination are present",
    ) as step:
        actual_inventory = detail.demo_link_inventory()
        expected_inventory = inventory_for_route(route)
        assert actual_inventory == expected_inventory
        assert (link_label, destination) in actual_inventory
        step["actual"] = f"route={route}; full inventory={actual_inventory!r}"

    with ui_steps.step(
        "GET destination", "Final HTTP response is 2xx with no more than five redirects"
    ) as step:
        parsed = urlparse(destination)
        assert parsed.scheme in {"http", "https"} and parsed.netloc
        status, final_url = detail.fetch_destination(destination)
        step["actual"] = (
            f"original_url={destination}; final_url={final_url}; status={status}"
        )
        assert 200 <= status <= 299, (
            f"Demo link failed: project={route!r}, label={link_label!r}, "
            f"original_url={destination!r}, final_url={final_url!r}, status={status}"
        )


@pytest.mark.parametrize(
    ("route", "video_id", "expected_title"),
    [
        pytest.param(route, video_id, title, id=f"PORT-013-{route}-{video_id}")
        for route, video_id, title in YOUTUBE_VIDEOS
    ],
)
def test_youtube_demo_links_in_browser(
    page: Page,
    ui_steps: StepRecorder,
    portfolio_actions: PortfolioActions,
    route: str,
    video_id: str,
    expected_title: str,
) -> None:
    detail = ProjectDetailPage(page, portfolio_actions)
    project_heading = project_heading_for_route(route)
    destination = youtube_url(video_id)
    ui_steps.configure(
        "PORT-013",
        {
            "project": route,
            "video_id": video_id,
            "expected_title": expected_title,
            "original_url": destination,
        },
    )
    ui_steps.plan(
        [
            ("Open project and locate video link", "The expected YouTube link is present in Demo Links"),
            ("Open video link in browser", "The link opens a new browser page"),
            (
                "Verify destination response and content",
                f"Final URL is the video {video_id}, response is 2xx, and title {expected_title!r} loads",
            ),
        ]
    )
    with ui_steps.step(
        "Open project and locate video link",
        "The expected YouTube link is present in Demo Links",
    ) as step:
        response = detail.open_project(route)
        assert response is not None and response.ok
        expect(detail.heading(project_heading, level=1)).to_be_visible()
        detail.scroll_into_view(detail.demo_links)
        expect(detail.demo_links).to_be_visible()
        video_link = detail.video_link(destination)
        expect(video_link).to_have_count(1)
        expect(video_link).to_have_accessible_name("YouTube video")
        step["actual"] = (
            f"project={project_heading!r}; link={destination}; "
            f"source_status={response.status}; source_url={page.url}"
        )

    with ui_steps.step(
        "Open video link in browser", "The link opens a new browser page"
    ) as step:
        video_page, popup_responses = detail.open_video_link(video_link)
        step["actual"] = (
            f"popup_url={video_page.url}; "
            f"demo_pause_ms={portfolio_actions.last_click_delay_ms}"
        )

    with ui_steps.step(
        "Verify destination response and content",
        f"Final URL is the video {video_id}, response is 2xx, "
        f"and title {expected_title!r} loads",
    ) as step:
        final_url = video_page.url
        parsed_url = urlparse(final_url)
        query = dict(
            part.split("=", 1)
            for part in parsed_url.query.split("&")
            if "=" in part
        )
        matching_response = next(
            (
                browser_response
                for browser_response in reversed(popup_responses)
                if browser_response.url == final_url
            ),
            None,
        )
        assert matching_response is not None, (
            f"No main-frame navigation response was captured for {final_url!r}; "
            f"captured={[item.url for item in popup_responses]!r}"
        )
        response_status = matching_response.status
        expect(video_page).to_have_title(re.compile(re.escape(expected_title)))
        expect(
            detail.heading(expected_title, target=video_page)
        ).to_be_visible()
        content_loaded = True
        step["actual"] = (
            f"final_url={final_url}; status={response_status}; "
            f"expected_title={expected_title!r}; content_loaded={content_loaded}"
        )
        assert parsed_url.hostname in {"www.youtube.com", "youtube.com"}
        assert parsed_url.path == "/watch"
        assert query.get("v") == video_id
        assert 200 <= response_status <= 299, (
            f"Browser navigation failed for {destination!r}: "
            f"final_url={final_url!r}, status={response_status}"
        )
        assert content_loaded
