from playwright.sync_api import Playwright, sync_playwright, expect

def test_login_agente_origen(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://127.0.0.1:8000/")
    page.get_by_role("link", name="Portal Agente Origen").click()
    page.get_by_role("textbox", name="Username:").click()
    page.get_by_role("textbox", name="Username:").fill("u1")
    page.get_by_role("textbox", name="Password:").click()
    page.get_by_role("textbox", name="Password:").fill("Contra1234")
    page.get_by_role("button", name="Ingresar").click()
    expect(page.get_by_text("Hola, u1 - Puerto de Shanghái")).to_be_visible()

    context.close()
    browser.close()

def test_login_agente_destino(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://127.0.1:8000/")
    page.get_by_role("link", name="Portal Agente Destino").click()
    page.get_by_role("textbox", name="Username:").click()
    page.get_by_role("textbox", name="Username:").fill("u2")
    page.get_by_role("textbox", name="Password:").click()
    page.get_by_role("textbox", name="Password:").fill("Contra1234")
    page.get_by_role("button", name="Ingresar").click()
    expect(page.get_by_text("Hola, u2 - Puerto de Nueva York")).to_be_visible()

    context.close()
    browser.close()

def test_no_login_agente(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://127.0.1:8000/")
    page.get_by_role("link", name="Portal Agente Origen").click()
    page.get_by_role("textbox", name="Username:").click()
    page.get_by_role("textbox", name="Username:").fill("u2")
    page.get_by_role("textbox", name="Password:").click()
    page.get_by_role("textbox", name="Password:").fill("Contra1234")
    page.get_by_role("button", name="Ingresar").click()
    expect(page.get_by_text("Acceso denegado. No eres un agente aduanal de origen")).to_be_visible()

    context.close()
    browser.close()


