import web
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

# Configuración de Selenium para Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN", "/usr/bin/google-chrome-stable")


def consultar_cedula(nombre, paterno, materno, cedula_buscada=None):
    buscar_por_cedula = cedula_buscada is not None and cedula_buscada.strip() != ""

    try:
        driver_path = os.environ.get("CHROMEDRIVER_PATH", ChromeDriverManager().install())
        driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)

        driver.get("https://www.cedulaprofesional.sep.gob.mx/cedula/presidencia/indexAvanzada.action")

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "nombre")))

        driver.find_element(By.ID, "nombre").send_keys(nombre)
        driver.find_element(By.ID, "paterno").send_keys(paterno)
        driver.find_element(By.ID, "materno").send_keys(materno)

        driver.find_element(By.ID, "dijit_form_Button_0_label").click()

        time.sleep(8)

        resultados = []
        filas = driver.find_elements(By.CSS_SELECTOR, ".dojoxGridRow, .dojoxGridRowOdd")

        for fila in filas:
            celdas = fila.find_elements(By.CSS_SELECTOR, ".dojoxGridCell")
            if len(celdas) >= 5:
                resultados.append({
                    "cedula": celdas[0].text.strip(),
                    "primer_nombre": celdas[1].text.strip(),
                    "apellido_paterno": celdas[2].text.strip(),
                    "apellido_materno": celdas[3].text.strip(),
                    "nivel": celdas[4].text.strip()
                })

        if buscar_por_cedula:
            cedula_encontrada = next((r for r in resultados if r["cedula"] == cedula_buscada), None)
            return {"existe": bool(cedula_encontrada), "datos": cedula_encontrada}

        return {"existe": bool(resultados), "datos": resultados}

    except Exception as e:
        return {"error": str(e), "existe": False, "datos": None}

    finally:
        driver.quit()


class Consulta:
    def GET(self):
        datos = web.input(nombre="", paterno="", materno="", cedula="")
        if not datos.nombre or not datos.paterno:
            return web.jsondumps({"error": "Se requiere al menos nombre y apellido paterno", "existe": False, "datos": None})
        
        resultado = consultar_cedula(datos.nombre, datos.paterno, datos.materno, datos.cedula)
        return web.jsondumps(resultado)