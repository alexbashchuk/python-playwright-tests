from __future__ import annotations

import base64
import html
from pathlib import Path
from typing import Any

import pytest
from pytest_html import extras
from playwright.sync_api import Page

from tests.ui.ui_support import PortfolioActions, StepRecorder


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("portfolio demo")
    group.addoption(
        "--demo",
        action="store_true",
        default=False,
        help="enable visible portfolio demo pacing",
    )
    group.addoption(
        "--demo-click-delay-ms",
        type=int,
        default=500,
        help="milliseconds to pause after successful clicks in demo mode",
    )


def pytest_configure(config: pytest.Config) -> None:
    delay_ms = config.getoption("--demo-click-delay-ms")
    if delay_ms < 0:
        raise pytest.UsageError("--demo-click-delay-ms must be a non-negative integer")

    if config.getoption("--demo"):
        if not config.getoption("headed", default=False):
            raise pytest.UsageError("--demo requires --headed")
        workers = config.getoption("numprocesses", default=None)
        if workers not in (None, 0, 1, "0", "1"):
            raise pytest.UsageError("--demo requires a single sequential worker")

    config.addinivalue_line(
        "markers",
        "portfolio_review: observation-only scenario awaiting product clarification",
    )


@pytest.fixture
def ui_steps(
    request: pytest.FixtureRequest,
    page: Page,
    output_path: str,
) -> StepRecorder:
    recorder = StepRecorder(
        node=request.node,
        page=page,
        output_path=Path(output_path),
        demo=request.config.getoption("--demo"),
        demo_click_delay_ms=request.config.getoption("--demo-click-delay-ms"),
    )
    setattr(request.node, "_portfolio_step_recorder", recorder)
    return recorder


@pytest.fixture
def portfolio_actions(page: Page, ui_steps: StepRecorder) -> PortfolioActions:
    return PortfolioActions(
        page=page,
        demo=ui_steps.demo,
        demo_click_delay_ms=ui_steps.demo_click_delay_ms,
    )


def _failure_artifacts(report: pytest.TestReport, recorder: StepRecorder) -> None:
    page = recorder.page
    try:
        if not page.is_closed():
            screenshot_path = recorder.output_path / "failure-screenshot.png"
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(screenshot_path), full_page=False)
            image_data = base64.b64encode(screenshot_path.read_bytes()).decode("ascii")
            report.extras.append(
                extras.html(
                    "<details><summary>Failure screenshot</summary>"
                    f'<img alt="Failure screenshot" style="max-width:100%" '
                    f'src="data:image/png;base64,{image_data}"></details>'
                )
            )
    except Exception as exc:
        recorder.artifact_errors.append(f"Screenshot capture failed: {exc}")

    trace_path = recorder.output_path / "trace.zip"
    if trace_path.exists() or recorder.trace_expected:
        report.extras.append(extras.url(trace_path.resolve().as_uri(), name="Playwright trace"))


def _report_details(recorder: StepRecorder) -> str:
    recorder.finish()
    rows = []
    for step in recorder.steps:
        rows.append(
            "<tr>"
            f"<td>{html.escape(step['status'])}</td>"
            f"<td>{html.escape(step['name'])}</td>"
            f"<td>{html.escape(step['expected'])}</td>"
            f"<td>{html.escape(step['actual'])}</td>"
            f"<td>{html.escape(step['started_at'])}</td>"
            f"<td>{html.escape(step['completed_at'])}</td>"
            f"<td>{html.escape(step['duration_ms'])}</td>"
            "</tr>"
        )

    metadata = dict(recorder.metadata)
    metadata.update(
        {
            "scenario_id": recorder.scenario_id or "Unassigned",
            "page_url": recorder.page.url if not recorder.page.is_closed() else "closed",
            "demo_mode": recorder.demo,
            "demo_click_delay_ms": recorder.demo_click_delay_ms,
        }
    )
    metadata_html = "".join(
        f"<li><strong>{html.escape(str(key))}:</strong> "
        f"{html.escape(str(value))}</li>"
        for key, value in metadata.items()
    )
    errors_html = "".join(
        f"<li>{html.escape(message)}</li>" for message in recorder.artifact_errors
    )
    review_html = ""
    if recorder.review_note:
        review_html = (
            '<p><strong>REVIEW REQUIRED (observation only):</strong> '
            f"{html.escape(recorder.review_note)}</p>"
        )
    artifact_html = (
        f"<ul>{errors_html}</ul>" if recorder.artifact_errors else ""
    )
    return (
        f"<h3>{html.escape(recorder.scenario_id or 'UI scenario')} — ordered steps</h3>"
        f"{review_html}<ul>{metadata_html}</ul>"
        "<table><thead><tr><th>Status</th><th>Step</th><th>Expected</th>"
        "<th>Actual</th><th>Started</th><th>Completed</th><th>Duration (ms)</th>"
        f"</tr></thead><tbody>{''.join(rows)}</tbody></table>"
        f"{artifact_html}"
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[Any]
):
    outcome = yield
    report = outcome.get_result()
    recorder = getattr(item, "_portfolio_step_recorder", None)

    if recorder is None:
        if report.failed and report.when in {"setup", "teardown"}:
            report.extras = getattr(report, "extras", [])
            report.extras.append(
                extras.html(
                    "<p>UI step reporting was unavailable because test "
                    f"{html.escape(report.when)} failed before the recorder was ready.</p>"
                )
            )
        return

    if report.failed and report.when in {"setup", "teardown"}:
        recorder.add_hook_failure(report.when, str(report.longrepr))
    if report.when == "call":
        recorder.capture_trace_on_failure = report.failed
    if report.failed:
        recorder.capture_trace_on_failure = True
        report.extras = getattr(report, "extras", [])
        _failure_artifacts(report, recorder)

    if report.when == "call" or (
        report.failed and report.when in {"setup", "teardown"}
    ):
        report.extras = getattr(report, "extras", [])
        report.extras.append(extras.html(_report_details(recorder)))
