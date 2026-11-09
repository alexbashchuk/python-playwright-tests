# Portfolio UI Test Scenarios

## Scope and browser observations

- Target: `https://alexbashchuk.github.io/`
- The landing page is a vertically scrolling portfolio with Profile, Professional Summary, Technical Skills, Professional Experience, Education, Certifications, and Automation Projects Examples sections.
- The project examples are a list of linked items, not visually presented cards.
- The landing page has no navigation landmark or section menu. Scenarios cover section access by scrolling and navigation through the observed project routes; they do not assume an unobserved section menu.
- Project routes use hash URLs and render project-specific detail pages with a `Home` button.
- Certificate scenarios cover only opening and closing the dialog. Certificate image contents, appearance, and comparison against reference images are explicitly out of scope.
- Do not submit contact details or trigger any GitHub Actions/workflow.

## Priorities

- **P1** — primary content and core navigation.
- **P2** — secondary controls, outbound-link destinations, keyboard, and responsive checks.

## Scenarios

### PORT-001 — Load the portfolio's primary content

| Field | Details |
|---|---|
| Priority | P1 |
| Preconditions | Open a fresh page at the portfolio root URL. |
| Steps | 1. Navigate to `/`. 2. Inspect the Profile and Professional Summary sections. |
| Expected results | The page loads successfully and shows the `Alex Boschuk` heading, the `Senior SDET / QA Automation Engineer` role, contact details, citizenship text, and a non-empty Professional Summary. The browser title is `myportfolio`. |

### PORT-002 — Read the landing-page sections in order

| Field | Details |
|---|---|
| Priority | P1 |
| Preconditions | The landing page is loaded at `/`. |
| Steps | 1. Scroll down through the page. 2. Verify each section heading as it comes into view. 3. Continue to the end of the page. |
| Expected results | Sections are reachable in this order: Professional Summary, Technical Skills, Professional Experience, Education, Certifications, and My QA Automation Demo Projects. Professional Experience includes the seven observed employer entries; Education and Certifications each show their listed items; the project list and `© 2026 Alex Boschuk` footer are reachable. No section-navigation control is required by this scenario because none was observed. |

### PORT-003 — Follow each project entry to its detail page

| Field | Details |
|---|---|
| Priority | P1 |
| Preconditions | The landing page is loaded at `/`. Treat each project entry as an independent navigation check. |
| Steps | 1. Locate a project link by its visible technology label. 2. Activate it. 3. Verify the resulting hash route and page heading. 4. Activate `Home` and verify the landing page is rendered again. 5. Repeat independently for each row below. |
| Expected results | Each link opens its matching detail page and heading. The `Home` button returns to the landing page at `/#/`; the profile and project list are present again. |

| Visible project link | Expected route | Expected detail-page heading |
|---|---|---|
| JavaScript + React + Vite | `#/portfolio-github` | GitHub Portfolio Website |
| Java + Playwright + OpenCV + JUnit | `#/java-playwright` | Java + Playwright Automation Project |
| C# + Selenium + Appium + NUnit | `#/csharp-mobile` | C# + Selenium + Appium + NUnit Automation Project |
| Java + Selenium + Appium + Charles Proxy + TestNG | `#/java-mobile` | Java + Selenium + Appium + Charles Proxy + TestNG Automation Project |
| JMeter + Jenkins CI/CD | `#/jmeter-jenkins` | JMeter + Jenkins API Automation Project |
| Cypress + TypeScript + Allure + GitHub Actions | `#/cypress-typescript-cicd` | Cypress + TypeScript + Allure + GitHub Actions CI/CD Project |

### PORT-004 — Verify portfolio detail-page demo links

| Field | Details |
|---|---|
| Priority | P2 |
| Preconditions | Open `/#/portfolio-github`. |
| Steps | 1. Locate the Demo Links section. 2. Check the visible link labels and destinations without submitting a form or initiating a workflow. |
| Expected results | `GitHub repository` links to `https://github.com/alexbashchuk/alexbashchuk.github.io`, and `GitHub Pages site` links to `https://alexbashchuk.github.io`. |

### PORT-005 — Parameterize work-description checks for every company

| Field | Details |
|---|---|
| Priority | P2 |
| Preconditions | Open a fresh landing page at `/` for each parameter combination. Build the company-name data set from every employer entry in Professional Experience (seven entries in the supplied observations); use the exact displayed company names. |
| Parameters | `company_name`, `description_option`, `expected_heading`. Run every company with both rows in the table below using `pytest.mark.parametrize`. Use readable test IDs containing the company name and description option. |
| Steps | 1. Find the unique company block by its company name within Professional Experience. 2. Scroll that block into view. 3. Within that block, activate `Choose work description`. 4. Verify both menu choices are visible. 5. Select the parameterized description option. 6. Assert the heading text equals the expected heading exactly. 7. Verify the selected button label. 8. Activate `Close work description` within that company block. 9. Verify the selected content is hidden and the collapsed button is restored. |
| Expected results | Every company supports both options. The heading and selected button label match the table exactly. Closing the description restores `Choose work description`. Each parameter combination is an independent pytest result. |

| `description_option` | `expected_heading` | Expected selected button label |
|---|---|---|
| Short Details | Work description | Work description: Short Details |
| Long Story | Work story | Work description: Long Story |

- Identify the company block using `company_name`, never its list index or a globally matched repeated button. Require exactly one matching block; fail clearly on missing or ambiguous company names.
- Scope description controls, selected content, and heading assertions to that block. Do not allow a heading from another company to satisfy the assertion.
- Resolve and freeze the full company-name parameter list before test execution; do not silently omit an employer because its controls are missing. With seven companies, this produces fourteen test instances.

### PORT-006 — Open and close a certificate dialog

| Field | Details |
|---|---|
| Priority | P2 |
| Preconditions | The landing page is loaded at `/`. |
| Steps | 1. Activate the `AS1` button in Certifications. 2. Verify a dialog is present. 3. Activate the dialog's `CLOSE` button. |
| Expected results | Activating AS1 opens a dialog with a visible close control. Activating CLOSE dismisses the dialog. Do not assert certificate image pixels, image source, or image content. |

### PORT-007 — Review the “My QA Automation Demo Projects” button behavior

| Field | Details |
|---|---|
| Priority | Review required |
| Preconditions | The landing page is loaded at `/`. |
| Steps | 1. Activate the `My QA Automation Demo Projects` button in Technical Skills. 2. Observe the URL and visible page position/content. |
| Observed result | The URL changes from `/` to `/#/`, while the landing-page content remains rendered. No clear jump to the project list was observed. |
| Expected result | **Unconfirmed.** Product review is needed to clarify whether this control should navigate home, scroll to the project list, or do something else before making it an acceptance assertion. |

### PORT-008 — Keep the landing page usable at a narrow viewport

| Field | Details |
|---|---|
| Priority | P2 |
| Preconditions | The landing page is loaded at `/` in a 390 × 844 CSS-pixel viewport. |
| Steps | 1. Inspect the profile and contact details. 2. Scroll through the skills, experience, education, certifications, and project list. 3. Check the document's horizontal scroll width against its viewport width. |
| Expected results | Content reflows into a readable vertical layout, including wrapped contact text and project entries. All sections remain reachable, and the document does not require horizontal scrolling. |

### PORT-009 — Keep a project detail page usable at a narrow viewport

| Field | Details |
|---|---|
| Priority | P2 |
| Preconditions | Open `/#/portfolio-github` in a 390 × 844 CSS-pixel viewport. |
| Steps | 1. Inspect the page heading, description, demo links, and tech-stack chips. 2. Scroll to the bottom. 3. Compare document and viewport widths. |
| Expected results | Text and chips wrap within the viewport, all detail-page sections and the `Home` button remain reachable, and no horizontal scrolling is required. |

### PORT-010 — Navigate interactive controls with the keyboard

| Field | Details |
|---|---|
| Priority | P2 |
| Preconditions | Open a fresh landing page at `/`; do not click a control before beginning. |
| Steps | 1. Press Tab once. 2. Press Tab again. 3. Press Enter to open the focused work-description control. 4. Press Tab to focus `Short Details`, then press Enter. |
| Expected results | The first Tab focuses `My QA Automation Demo Projects`; the second focuses the Williams Companies `Choose work description` button. Enter opens its menu, Tab can focus `Short Details`, and Enter selects it. The selected description is displayed and the control's accessible name reflects `Short Details`. |

### PORT-011 — Validate scrolling on every project detail page

| Field | Details |
|---|---|
| Priority | P2 |
| Preconditions | Parameterize over all six project routes and expected headings in PORT-003. Run each independently in a fixed 390 × 844 CSS-pixel viewport. |
| Steps | 1. Open the project detail route and verify its heading. 2. Reset the page to the top and record scroll position, viewport height, and document scroll height. 3. Scroll down in bounded viewport-sized increments, recording the resulting position and checking sections as they enter the viewport. 4. Bring Demo Links and its links into view. 5. Continue to the document bottom and verify the last content and `Home` control are reachable, scrolling to Home separately if needed. 6. Scroll back to the top and verify the project heading is in the viewport again. 7. Check for horizontal overflow. |
| Expected results | On a page taller than the viewport, scrolling changes the document scroll position and reaches the bottom within a small rounding tolerance (for example, 2 CSS pixels). Demo Links, all other rendered sections, and Home are reachable and visible in the viewport when scrolled to. Returning to the top restores the initial position. Document width does not exceed viewport width beyond the same rounding tolerance. If the full page fits in the viewport, record that fact and verify all content is reachable without requiring a positive scroll delta. |

- Visibility alone is insufficient for scrolling assertions: check viewport intersection as well as document scroll metrics.
- Use bounded scrolling and condition-based waits for layout or smooth-scroll completion; avoid arbitrary sleeps and infinite loops.

### PORT-012 — Check non-video Demo Links through HTTP requests

| Field | Details |
|---|---|
| Priority | P2 |
| Preconditions | Cover all six project routes in PORT-003. Enumerate every rendered non-YouTube anchor inside each project's Demo Links section and resolve its destination against the page URL. |
| Parameters | Project route, link label, and resolved destination URL. Give every non-video project/link combination an independent report result. Freeze the discovered inventory before assertions so failures cannot silently remove links from coverage. |
| Steps | 1. Open the project and scroll Demo Links into the viewport. 2. Verify the section exists and contains links. 3. Record each non-YouTube link label and href; assert an HTTP or HTTPS destination. 4. Send a read-only GET using Playwright's API request context, with a finite timeout and bounded redirect following. 5. Record the response status and final URL. 6. Assert the final status is in the 200–299 range. 7. Dispose of responses. |
| Expected results | Every non-video Demo Links destination returns a successful final HTTP response after any allowed redirects. Timeouts, DNS/TLS errors, redirect loops, missing destinations, and final non-2xx responses are reported as failures with project/link context. YouTube video destinations are excluded from this API scenario and covered by PORT-013. |

- These are HTTP availability checks for non-video linked resources; retain PORT-004's exact destination assertions for the portfolio project.
- For hash URLs, check the resource's HTTP availability and separately validate the client-side route with browser assertions where applicable; an HTTP 200 alone cannot validate a hash route.
- Do not submit forms, authenticate, trigger builds, invoke workflow-dispatch APIs, or execute other state-changing operations. A link to a workflow page may be checked with a GET only.
- Report 401, 403, 429, and other access/rate-limit responses with their actual status; do not treat them as successful link checks or silently skip them.

### PORT-013 — Open every YouTube Demo Link in the browser

| Field | Details |
|---|---|
| Priority | P2 |
| Preconditions | Parameterize over every observed YouTube link in the six project Demo Links sections; each test starts from its project route. |
| Parameters | Project route, video ID, and expected video title. Give each video its own pytest result. |
| Steps | 1. Open the project and locate the matching YouTube video link by its destination. 2. Click the link and capture the newly opened browser page. 3. Wait for the destination document to load. 4. Record the final browser URL and main-frame navigation response status. 5. Verify the final watch URL identifies the expected video and the expected title is visible in the page title and a heading. |
| Expected results | Each link opens a YouTube watch page in a new browser page. The final URL contains the expected video ID, the final main-frame response status is 2xx, and the expected destination title is rendered. Record the final URL, response status, and content-loaded result in the test report. |

## GitHub Copilot implementation and pytest reporting instructions

- Implement these scenarios with Python, pytest, and Playwright. Reuse the repository's existing fixtures, Page Objects, and reporting conventions where available.
- Apply step reporting to **all scenarios PORT-001 through PORT-013**, including every parameter instance and setup/cleanup action relevant to a test. Report each action and assertion in execution order, with a clear description, expected result, actual result, and passed/failed status. Mark unexecuted steps as not run when an earlier failure stops a test; never mark them as passed.
- Reuse the configured pytest report if it supports step details. Otherwise, add `pytest-html` and produce a self-contained HTML report with `pytest --html=reports/portfolio-ui.html --self-contained-html --junitxml=reports/portfolio-ui.xml`. Include the necessary dependencies and document the command in the test README.
- Implement a reusable step helper/context manager that records step start, completion, and exceptions. Use pytest reporting hooks to attach ordered step records to each HTML test result for both passed and failed tests; console output alone is insufficient. Include setup/teardown failures in the report. Preserve assertion exceptions and tracebacks so reporting cannot turn a failed check into a pass.
- Include scenario ID, company/project/link parameters, page URL, expected/actual headings, scroll positions and dimensions, and HTTP original/final URLs and statuses as appropriate. For failed UI steps, attach a screenshot and the available Playwright trace using the repository's artifact conventions. Failure-artifact capture must not mask the original error.
- Keep each company's two description choices, each project's scrolling check, and each Demo Links request independently identifiable in the report. If subtests are used for links, ensure the report exposes each subtest's outcome and a failed subtest fails the parent test.
- Retain PORT-007 as an observation/review item until its intended behavior is confirmed; clearly label it in the report rather than asserting an invented expected behavior.
- Verify the generated report contains ordered steps for passing tests and a controlled failing assertion, then remove any intentionally failing verification test from the delivered suite. Report actual execution results; if execution is blocked, state the blocker instead of claiming the scenarios passed.

## Headed demo execution and click pacing

- Create UI tests that support a headed demo run so a person can watch the browser. Reuse the same tests and assertions for normal and demo runs.
- Use the `pytest-playwright` `--headed` option to show the browser. Add custom pytest options `--demo` and `--demo-click-delay-ms` (default: `500`). Apply the delay only when `--demo` is enabled; require `--headed` with demo mode and give a clear configuration error if it is missing.
- In demo mode, wait 500 ms **after every successful UI click**, before the next test action or assertion. Centralize this in a shared Page Object action helper used by every click, including company menus, Short Details, Long Story, Close, project links, certificate controls, and Home. Cover double-click actions if any are introduced. Do not patch Playwright internals or duplicate pauses in individual tests.
- For synchronous Python Playwright tests, the helper should perform `locator.click(...)` followed by `page.wait_for_timeout(demo_click_delay_ms)` only in demo mode. Use the equivalent awaited calls if the repository uses asynchronous Playwright. Validate that the configured delay is a non-negative integer.
- Preserve navigation and popup handling around the click. If a click opens a new page, wait for that page as required and apply the pause on the active, open page before continuing. Do not attempt the delay on a page that the click closed.
- This fixed pause is exclusively for presentation pacing. Keep Playwright auto-waiting and explicit readiness assertions; do not use the pause as evidence that content loaded. The instruction to avoid arbitrary sleeps in PORT-011 still applies to scrolling/readiness checks.
- Do not substitute `slow_mo` for this requirement: the requested pacing is specifically a pause after each click. Avoid adding both mechanisms by default, which would compound delays.
- Run demo tests sequentially in one visible browser session at a time; do not enable parallel workers for the demo command. HTTP-only requests do not need artificial pauses.
- Include demo mode and delay configuration in the pytest report. Record each applied pause within its associated click step so the report matches visible execution.
- Document these commands in the test README (the `--demo` options must be implemented before using the demo command):

```bash
# Visible demo: pause 500 ms after each click
pytest --headed --demo --demo-click-delay-ms=500 --html=reports/portfolio-ui-demo.html --self-contained-html

# Normal run: no presentation delays
pytest --html=reports/portfolio-ui.html --self-contained-html --junitxml=reports/portfolio-ui.xml
```

## Items for review

- No section-navigation menu or navigation landmark was present on the landing page. Confirm whether a dedicated section menu is expected before adding such a requirement.
- The `My QA Automation Demo Projects` button's observed URL change and lack of visible scroll movement leave its intended behavior unclear (PORT-007).
- The certificate dialog did not close when Escape was pressed during exploration; this plan only requires the observed explicit CLOSE button. Confirm whether Escape-to-close is a desired requirement.
- The original exploration exercised only the Williams Companies work-description menu. PORT-005 now requires both description choices for every employer as requested; verify the exact company-name data set during implementation.
