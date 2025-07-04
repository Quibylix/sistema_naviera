from playwright.sync_api import Playwright, expect

def test_crear_contenedor_primer_paso(playwright: Playwright) -> None:
    archivo_prueba = __file__.replace("test_crear_contenedor.py", "archivo_prueba.pdf")

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://127.0.0.1:8000/")
    page.get_by_role("link", name="Portal Agente Origen").click()
    page.get_by_role("textbox", name="Nombre de usuario:").click()
    page.get_by_role("textbox", name="Nombre de usuario:").fill("u1")
    page.get_by_role("textbox", name="Contraseña:").click()
    page.get_by_role("textbox", name="Contraseña:").fill("Contra1234")
    page.get_by_role("button", name="Ingresar").click()
    page.get_by_role("link", name="Nuevo Embarque").click()
    page.get_by_label("Ruta:").select_option("1")
    page.get_by_role("textbox", name="Fecha salida:").fill("2025-06-30")
    page.get_by_label("Buque:").select_option("BR0001")
    page.get_by_role("textbox", name="Nombre transportista:").click()
    page.get_by_role("textbox", name="Nombre transportista:").fill("Transportista")
    page.get_by_role("button", name="Siguiente").click()
    page.get_by_role("textbox", name="Nombre mc:").click()
    page.get_by_role("textbox", name="Nombre mc:").fill("manifiesto")
    page.get_by_role("button", name="Doc mc:").set_input_files(archivo_prueba)
    page.get_by_role("button", name="Crear").click()
    page.get_by_title("Crear Contenedor").click()
    expect(page.get_by_role("heading", name="Crear contenedor para")).to_be_visible()

    page.goto("http://127.0.1:8000/embarque")
    page.get_by_title("Borrar").click()
    page.get_by_role("button", name="Sí, eliminar").click()

    context.close()
    browser.close()

def test_crear_contenedor_segundo_paso(playwright: Playwright) -> None:
    archivo_prueba = __file__.replace("test_crear_contenedor.py", "archivo_prueba.pdf")

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://127.0.0.1:8000/")
    page.get_by_role("link", name="Portal Agente Origen").click()
    page.get_by_role("textbox", name="Nombre de usuario:").click()
    page.get_by_role("textbox", name="Nombre de usuario:").fill("u1")
    page.get_by_role("textbox", name="Contraseña:").click()
    page.get_by_role("textbox", name="Contraseña:").fill("Contra1234")
    page.get_by_role("button", name="Ingresar").click()
    page.get_by_role("link", name="Nuevo Embarque").click()
    page.get_by_label("Ruta:").select_option("1")
    page.get_by_role("textbox", name="Fecha salida:").fill("2025-06-30")
    page.get_by_label("Buque:").select_option("BR0001")
    page.get_by_role("textbox", name="Nombre transportista:").click()
    page.get_by_role("textbox", name="Nombre transportista:").fill("Transportista")
    page.get_by_role("button", name="Siguiente").click()
    page.get_by_role("textbox", name="Nombre mc:").click()
    page.get_by_role("textbox", name="Nombre mc:").fill("manifiesto")
    page.get_by_role("button", name="Doc mc:").set_input_files(archivo_prueba)
    page.get_by_role("button", name="Crear").click()
    page.get_by_title("Crear Contenedor").click()
    page.get_by_label("Tipo contenedor:").select_option("40GP")
    page.get_by_label("Tipo carga:").select_option("1")
    page.get_by_label("Tipo equipamiento:").select_option("6")
    page.get_by_label("Puerto descarga:").select_option("NL001")
    page.get_by_role("checkbox", name="Es consolidado:").check()
    page.get_by_role("button", name="Guardar").click()
    page.locator("#id_descripcion_mercancia").click()
    page.locator("#id_descripcion_mercancia").fill("Descripcion")
    page.locator("#id_cantidad_bultos").click()
    page.locator("#id_cantidad_bultos").fill("2")
    page.locator("#id_bulto").select_option("1")
    page.locator("#id_pais").select_option("CN")
    page.get_by_role("button", name="Agregar Mercancía").click()
    page.get_by_role("link", name="Consultar").click()
    page.get_by_title("Borrar").click()
    page.get_by_role("button", name="Sí, eliminar").click()

    context.close()
    browser.close()

def test_crear_contenedor_tercer_paso(playwright: Playwright) -> None:
    archivo_prueba = __file__.replace("test_crear_contenedor.py", "archivo_prueba.pdf")

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://127.0.0.1:8000/")
    page.get_by_role("link", name="Portal Agente Origen").click()
    page.get_by_role("textbox", name="Nombre de usuario:").click()
    page.get_by_role("textbox", name="Nombre de usuario:").fill("u1")
    page.get_by_role("textbox", name="Contraseña:").click()
    page.get_by_role("textbox", name="Contraseña:").fill("Contra1234")
    page.get_by_role("button", name="Ingresar").click()
    page.get_by_role("link", name="Nuevo Embarque").click()
    page.get_by_label("Ruta:").select_option("1")
    page.get_by_role("textbox", name="Fecha salida:").fill("2025-06-30")
    page.get_by_label("Buque:").select_option("BR0001")
    page.get_by_role("textbox", name="Nombre transportista:").click()
    page.get_by_role("textbox", name="Nombre transportista:").fill("Transportista")
    page.get_by_role("button", name="Siguiente").click()
    page.get_by_role("textbox", name="Nombre mc:").click()
    page.get_by_role("textbox", name="Nombre mc:").fill("manifiesto")
    page.get_by_role("button", name="Doc mc:").set_input_files(archivo_prueba)
    page.get_by_role("button", name="Crear").click()
    page.get_by_title("Crear Contenedor").click()
    page.get_by_label("Tipo contenedor:").select_option("40GP")
    page.get_by_label("Tipo carga:").select_option("1")
    page.get_by_label("Tipo equipamiento:").select_option("6")
    page.get_by_label("Puerto descarga:").select_option("NL001")
    page.get_by_role("checkbox", name="Es consolidado:").check()
    page.get_by_role("button", name="Guardar").click()
    page.locator("#id_descripcion_mercancia").click()
    page.locator("#id_descripcion_mercancia").fill("Descripcion")
    page.locator("#id_cantidad_bultos").click()
    page.locator("#id_cantidad_bultos").fill("2")
    page.locator("#id_bulto").select_option("1")
    page.locator("#id_pais").select_option("CN")
    page.get_by_role("button", name="Agregar Mercancía").click()
    page.get_by_text("Mercancías del contenedor TRAU-000001-5 Descripción Cantidad de bultos Clase de").click()
    page.get_by_role("link", name="Consultar").click()
    page.get_by_title("Borrar").click()
    page.get_by_role("button", name="Sí, eliminar").click()
    page.get_by_role("link", name="Nuevo Embarque").click()
    page.get_by_label("Ruta:").select_option("1")
    page.get_by_role("textbox", name="Fecha salida:").fill("2025-07-04")
    page.get_by_label("Buque:").select_option("BR0001")
    page.get_by_role("textbox", name="Nombre transportista:").click()
    page.get_by_role("textbox", name="Nombre transportista:").fill("Transportista")
    page.get_by_role("button", name="Siguiente").click()
    page.get_by_role("textbox", name="Nombre mc:").click()
    page.get_by_role("textbox", name="Nombre mc:").fill("Manifiesto")
    page.get_by_role("button", name="Doc mc:").set_input_files(archivo_prueba)
    page.get_by_role("button", name="Crear").click()
    page.get_by_title("Crear Contenedor").click()
    expect(page.get_by_role("heading", name="Crear contenedor para")).to_be_visible()
    page.get_by_label("Tipo contenedor:").select_option("40GP")
    page.get_by_label("Tipo carga:").select_option("1")
    page.get_by_label("Tipo equipamiento:").select_option("6")
    page.get_by_label("Puerto descarga:").select_option("NL001")
    page.get_by_role("checkbox", name="Es consolidado:").check()
    page.get_by_role("button", name="Guardar").click()
    expect(page.get_by_role("heading", name="Mercancías del contenedor")).to_be_visible()
    page.locator("#id_descripcion_mercancia").click()
    page.locator("#id_descripcion_mercancia").fill("Frijoles 1")
    page.locator("#id_cantidad_bultos").click()
    page.locator("#id_cantidad_bultos").fill("2")
    page.locator("#id_bulto").select_option("5")
    page.locator("#id_pais").select_option("CN")
    page.get_by_role("button", name="Agregar Mercancía").click()
    expect(page.get_by_role("cell", name="Frijoles")).to_be_visible()
    page.get_by_role("link", name="Siguiente ➜").click()
    expect(page.get_by_role("heading", name="Documentación del contenedor")).to_be_visible()

    page.goto("http://127.0.1:8000/embarque")
    page.get_by_title("Borrar").click()
    page.get_by_role("button", name="Sí, eliminar").click()

    context.close()
    browser.close()

def test_crear_contenedor_cuarto_paso(playwright: Playwright) -> None:
    archivo_prueba = __file__.replace("test_crear_contenedor.py", "archivo_prueba.pdf")
    
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://127.0.0.1:8000/")
    page.get_by_role("link", name="Portal Agente Origen").click()
    page.get_by_role("textbox", name="Nombre de usuario:").click()
    page.get_by_role("textbox", name="Nombre de usuario:").fill("u1")
    page.get_by_role("textbox", name="Contraseña:").click()
    page.get_by_role("textbox", name="Contraseña:").fill("Contra1234")
    page.get_by_role("button", name="Ingresar").click()
    page.get_by_role("link", name="Nuevo Embarque").click()
    page.get_by_label("Ruta:").select_option("1")
    page.get_by_role("textbox", name="Fecha salida:").fill("2025-06-30")
    page.get_by_label("Buque:").select_option("BR0001")
    page.get_by_role("textbox", name="Nombre transportista:").click()
    page.get_by_role("textbox", name="Nombre transportista:").fill("Transportista")
    page.get_by_role("button", name="Siguiente").click()
    page.get_by_role("textbox", name="Nombre mc:").click()
    page.get_by_role("textbox", name="Nombre mc:").fill("manifiesto")
    page.get_by_role("button", name="Doc mc:").set_input_files(archivo_prueba)
    page.get_by_role("button", name="Crear").click()
    page.get_by_title("Crear Contenedor").click()
    page.get_by_label("Tipo contenedor:").select_option("40GP")
    page.get_by_label("Tipo carga:").select_option("1")
    page.get_by_label("Tipo equipamiento:").select_option("6")
    page.get_by_label("Puerto descarga:").select_option("NL001")
    page.get_by_role("checkbox", name="Es consolidado:").check()
    page.get_by_role("button", name="Guardar").click()
    page.locator("#id_descripcion_mercancia").click()
    page.locator("#id_descripcion_mercancia").fill("Descripcion")
    page.locator("#id_cantidad_bultos").click()
    page.locator("#id_cantidad_bultos").fill("2")
    page.locator("#id_bulto").select_option("1")
    page.locator("#id_pais").select_option("CN")
    page.get_by_role("button", name="Agregar Mercancía").click()
    page.get_by_text("Mercancías del contenedor TRAU-000001-5 Descripción Cantidad de bultos Clase de").click()
    page.get_by_role("link", name="Consultar").click()
    page.get_by_title("Borrar").click()
    page.get_by_role("button", name="Sí, eliminar").click()
    page.get_by_role("link", name="Nuevo Embarque").click()
    page.get_by_label("Ruta:").select_option("1")
    page.get_by_role("textbox", name="Fecha salida:").fill("2025-07-04")
    page.get_by_label("Buque:").select_option("BR0001")
    page.get_by_role("textbox", name="Nombre transportista:").click()
    page.get_by_role("textbox", name="Nombre transportista:").fill("Transportista")
    page.get_by_role("button", name="Siguiente").click()
    page.get_by_role("textbox", name="Nombre mc:").click()
    page.get_by_role("textbox", name="Nombre mc:").fill("Manifiesto")
    page.get_by_role("button", name="Doc mc:").set_input_files(archivo_prueba)
    page.get_by_role("button", name="Crear").click()
    page.get_by_title("Crear Contenedor").click()
    expect(page.get_by_role("heading", name="Crear contenedor para")).to_be_visible()
    page.get_by_label("Tipo contenedor:").select_option("40GP")
    page.get_by_label("Tipo carga:").select_option("1")
    page.get_by_label("Tipo equipamiento:").select_option("6")
    page.get_by_label("Puerto descarga:").select_option("NL001")
    page.get_by_role("checkbox", name="Es consolidado:").check()
    page.get_by_role("button", name="Guardar").click()
    expect(page.get_by_role("heading", name="Mercancías del contenedor")).to_be_visible()
    page.locator("#id_descripcion_mercancia").click()
    page.locator("#id_descripcion_mercancia").fill("Frijoles 1")
    page.locator("#id_cantidad_bultos").click()
    page.locator("#id_cantidad_bultos").fill("2")
    page.locator("#id_bulto").select_option("5")
    page.locator("#id_pais").select_option("CN")
    page.get_by_role("button", name="Agregar Mercancía").click()
    expect(page.get_by_role("cell", name="Frijoles")).to_be_visible()
    page.get_by_role("link", name="Siguiente ➜").click()
    expect(page.get_by_role("heading", name="Documentación del contenedor")).to_be_visible()
    page.locator("#id_bol-nombre_archivo").click()
    page.locator("#id_bol-nombre_archivo").fill("Bill of Lading")
    page.locator("#id_bol-archivo").set_input_files(archivo_prueba)
    page.get_by_role("button", name="Guardar Bill of Lading").click()
    page.locator("#id_fac-nombre_archivo").click()
    page.locator("#id_fac-nombre_archivo").fill("Factura")
    page.locator("#id_fac-archivo").set_input_files(archivo_prueba)
    page.locator("section").filter(has_text="2. Factura de Exportación").locator("button").click()
    page.locator("#id_cert-nombre_archivo").click()
    page.locator("#id_cert-nombre_archivo").fill("Certificado")
    page.locator("#id_cert-archivo").set_input_files(archivo_prueba)
    page.get_by_role("button", name="Guardar Certificado").click()
    expect(page.get_by_role("cell", name="Bill of Lading").nth(1)).to_be_visible()
    expect(page.get_by_role("cell", name="Factura").nth(1)).to_be_visible()
    expect(page.get_by_role("cell", name="Certificado", exact=True)).to_be_visible()
    page.get_by_role("link", name="Siguiente").click()
    expect(page.get_by_role("heading", name="Información del Embarque")).to_be_visible()

    page.goto("http://127.0.1:8000/embarque")
    page.get_by_title("Borrar").click()
    page.get_by_role("button", name="Sí, eliminar").click()

    context.close()
    browser.close()

