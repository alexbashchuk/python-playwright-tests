# UI tests

The portfolio UI suite uses Python, pytest, and synchronous Playwright. The
`--base-url` and browser artifact settings come from the repository's
`pytest.ini`. Tests create self-contained step details in pytest-html reports;
failed browser tests include a screenshot and a link to the retained Playwright
trace.

UI tests are organized by responsibility: `tests/ui/pages/` contains portfolio
page objects, `tests/ui/components/` contains reusable experience-card and
certificate-dialog interactions, and `tests/ui/data/` contains portfolio
content and expected link inventories. `test_portfolio_ui.py` contains scenario
setup and validations.

Non-video Demo Links are checked with read-only HTTP requests. YouTube links
are excluded from those API checks and tested by clicking each link in the
browser, then recording the final watch URL, main navigation response status,
and whether the expected video title renders.

Run the complete suite and generate reports:

```powershell
New-Item -ItemType Directory -Force reports | Out-Null
.\.venv\Scripts\python.exe -m pytest --html=reports/portfolio-ui.html --self-contained-html --junitxml=reports/portfolio-ui.xml
```

Run a visible, sequential demo with a 500 ms pause after each successful UI
click:

```powershell
New-Item -ItemType Directory -Force reports | Out-Null
.\.venv\Scripts\python.exe -m pytest --headed --demo --demo-click-delay-ms=500 --html=reports/portfolio-ui-demo.html --self-contained-html
```

Demo mode requires `--headed`; `--demo-click-delay-ms` must be a non-negative
integer. The delay is presentation pacing only and does not replace Playwright
auto-waiting or explicit readiness assertions. PORT-007 is marked as an
observation pending product review and does not assert intended behavior.

Certificate tests validate only dialog open/close behavior. Image contents and
pixel comparison remain out of scope.
