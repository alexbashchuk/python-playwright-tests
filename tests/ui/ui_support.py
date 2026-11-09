from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any, Iterator

import pytest
from playwright.sync_api import Locator, Page


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class StepRecorder:
    def __init__(
        self,
        node: pytest.Item,
        page: Page,
        output_path: Path,
        demo: bool,
        demo_click_delay_ms: int,
    ) -> None:
        self.node = node
        self.page = page
        self.output_path = output_path
        self.demo = demo
        self.demo_click_delay_ms = demo_click_delay_ms
        self.scenario_id = ""
        self.metadata: dict[str, Any] = {}
        self.review_note = ""
        self.artifact_errors: list[str] = []
        self.capture_trace_on_failure = False
        self.steps: list[dict[str, str]] = []

    @property
    def trace_expected(self) -> bool:
        return self.capture_trace_on_failure

    def configure(
        self,
        scenario_id: str,
        metadata: dict[str, Any] | None = None,
        review_note: str = "",
    ) -> None:
        self.scenario_id = scenario_id
        self.metadata = metadata or {}
        self.review_note = review_note

    def plan(self, definitions: list[tuple[str, str]]) -> None:
        existing_names = {step["name"] for step in self.steps}
        for name, expected in definitions:
            if name not in existing_names:
                self.steps.append(
                    {
                        "name": name,
                        "expected": expected,
                        "actual": "Not run",
                        "status": "not run",
                        "started_at": "Not started",
                        "completed_at": "Not completed",
                        "duration_ms": "Not run",
                    }
                )
                existing_names.add(name)

    @contextmanager
    def step(self, name: str, expected: str) -> Iterator[dict[str, str]]:
        record = next(
            (
                step
                for step in self.steps
                if step["name"] == name and step["status"] == "not run"
            ),
            None,
        )
        if record is None:
            self.plan([(name, expected)])
            record = self.steps[-1]

        record["expected"] = expected
        record["status"] = "in progress"
        record["started_at"] = _timestamp()
        started = perf_counter()
        try:
            yield record
        except Exception as exc:
            record["status"] = "failed"
            if record["actual"] == "Not run":
                record["actual"] = f"{type(exc).__name__}: {exc}"
            record["duration_ms"] = f"{(perf_counter() - started) * 1000:.1f}"
            record["completed_at"] = _timestamp()
            raise
        else:
            record["status"] = "passed"
            if record["actual"] == "Not run":
                record["actual"] = "Completed"
            record["duration_ms"] = f"{(perf_counter() - started) * 1000:.1f}"
            record["completed_at"] = _timestamp()

    def add_hook_failure(self, phase: str, detail: str) -> None:
        self.steps.append(
            {
                "name": f"{phase.capitalize()} failure",
                "expected": "Fixture setup or teardown completes successfully",
                "actual": detail,
                "status": "failed",
                "started_at": _timestamp(),
                "completed_at": _timestamp(),
                "duration_ms": "0.0",
            }
        )

    def finish(self) -> None:
        for step in self.steps:
            if step["status"] == "in progress":
                step["status"] = "failed"
                if step["actual"] == "Not run":
                    step["actual"] = "Test stopped before the step completed"


class PortfolioActions:
    def __init__(
        self, page: Page, demo: bool, demo_click_delay_ms: int
    ) -> None:
        self.page = page
        self.demo = demo
        self.demo_click_delay_ms = demo_click_delay_ms
        self.last_click_delay_ms = 0

    def click(self, locator: Locator, **kwargs: Any) -> int:
        locator.click(**kwargs)
        return self._pause_if_demo()

    def double_click(self, locator: Locator, **kwargs: Any) -> int:
        locator.dblclick(**kwargs)
        return self._pause_if_demo()

    def click_popup(self, locator: Locator, **kwargs: Any) -> Page:
        with self.page.expect_popup() as popup_info:
            locator.click(**kwargs)
        popup = popup_info.value
        self._pause_if_demo(popup)
        return popup

    def _pause_if_demo(self, active_page: Page | None = None) -> int:
        page = active_page or self.page
        if self.demo and not page.is_closed():
            page.wait_for_timeout(self.demo_click_delay_ms)
            self.last_click_delay_ms = self.demo_click_delay_ms
        else:
            self.last_click_delay_ms = 0
        return self.last_click_delay_ms
