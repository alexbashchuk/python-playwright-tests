Use Python with pytest-playwright and playwright.sync_api.

Explore the application using Playwright MCP before choosing locators.
Save plans in specs/ and executable tests in tests/.
Name test files test_*.py and test functions test_*.

Use pytest's page fixture and Playwright expect assertions.
Keep tests independent.
Prefer accessible roles, labels, and stable test IDs.
Do not use fixed sleeps.
Run tests through .venv/Scripts/python.exe -m pytest.
Do not create TypeScript tests or invoke npx playwright test.

Separate application defects from automation defects.
Do not weaken assertions or skip failing tests to obtain a pass.
Do not trigger portfolio CI workflows or send contact messages.

Defer certificate image validation until the UI suite is complete.