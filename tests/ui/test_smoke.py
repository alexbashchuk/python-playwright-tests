from playwright.sync_api import Page, expect

def test_portfolio_opens(page: Page) -> None:
    response = page.goto("/")

    assert response is not None
    assert response.ok
    expect(page.locator("body")).to_be_visible()