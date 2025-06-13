from playwright.sync_api import Playwright, expect


def test_crear_embarque(playwright: Playwright) -> None:
    archivo_prueba = __file__.replace("test_crear_embarque.py", "archivo_prueba.pdf")

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
    page.get_by_role("link", name="Nuevo Embarque").click()
    page.get_by_label("Ruta:").select_option("1")
    page.get_by_role("textbox", name="Fecha salida:").fill("2025-06-26")
    page.get_by_label("Buque:").click()
    page.get_by_label("Buque:").select_option("BR0001")
    page.get_by_role("textbox", name="Nombre transportista:").click()
    page.get_by_role("textbox", name="Nombre transportista:").fill("Transportista 1")
    page.get_by_role("textbox", name="Nombre mc:").click()
    page.get_by_role("textbox", name="Nombre mc:").fill("f")
    page.get_by_role("group", name="Manifiesto de Carga (PDF)").click()
    page.get_by_role("button", name="Doc mc:").set_input_files(archivo_prueba)
    page.get_by_role("button", name="Crear").click()

    expect(page.get_by_role("cell", name="Santos Carrier")).to_be_visible()

    page.get_by_role("link", name="Borrar").click()
    page.get_by_role("button", name="Sí, eliminar").click()

    context.close()
    browser.close()

def test_error_crear_embarque(playwright: Playwright) -> None:
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
    page.get_by_role("link", name="Nuevo Embarque").click()
    page.get_by_label("Ruta:").select_option("1")
    page.get_by_role("textbox", name="Fecha salida:").fill("2025-06-04")
    page.get_by_label("Buque:").select_option("US0001")
    page.get_by_role("button", name="Crear").click()
    page.get_by_role("textbox", name="Nombre transportista:").click()
    page.get_by_role("textbox", name="Nombre transportista:").fill("asdfasdf")
    page.get_by_role("group", name="Manifiesto de Carga (PDF)").click()
    page.get_by_role("button", name="Crear").click()
    expect(page.get_by_text("La fecha de salida no puede")).to_be_visible()
    expect(page.locator("#id_manifiesto_carga-0-nombre_mc_error").get_by_text("This field is required.")).to_be_visible()
    expect(page.locator("#id_manifiesto_carga-0-doc_mc_error").get_by_text("This field is required.")).to_be_visible()

    # ---------------------
    context.close()
    browser.close()

