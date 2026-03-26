from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# -------- FUNCIÓN PARA LIMPIAR PRECIO --------
def limpiar_precio(precio):
    try:
        return int(precio.replace(".", "").replace(",", ""))
    except:
        return None

# -------- CONFIGURAR DRIVER --------
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

data = []

# -------- PAGINACIÓN --------
for pagina in range(0, 300, 48):  # puedes ajustar rango

    try:
        url = f"https://inmuebles.mercadolibre.com.mx/terrenos/venta/toluca/_Desde_{pagina}"
        driver.get(url)

        wait = WebDriverWait(driver, 10)
        items = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "ui-search-layout__item"))
        )

        print(f"Página {pagina} -> {len(items)} elementos")

        for item in items:
            try:
                # -------- TITULO --------
                titulo_elem = item.find_elements(By.CLASS_NAME, "ui-search-item__title")
                titulo = titulo_elem[0].text if titulo_elem else "No disponible"

                # -------- PRECIO --------
                precio_elem = item.find_elements(By.CLASS_NAME, "andes-money-amount__fraction")
                precio = precio_elem[0].text if precio_elem else "No disponible"
                precio = limpiar_precio(precio)

                # -------- UBICACIÓN --------
                ubicacion_elem = item.find_elements(By.CLASS_NAME, "ui-search-item__location")
                ubicacion = ubicacion_elem[0].text if ubicacion_elem else "No disponible"

                # -------- LINK --------
                link_elem = item.find_elements(By.TAG_NAME, "a")
                link = link_elem[0].get_attribute("href") if link_elem else "No disponible"

                # -------- FILTRO --------
                if precio is not None:
                    data.append({
                        "titulo": titulo,
                        "precio": precio,
                        "ubicacion": ubicacion,
                        "link": link
                    })

            except:
                continue

        # -------- DELAY --------
        time.sleep(2)

    except:
        print(f"Error en página {pagina}")
        continue

# -------- CERRAR --------
driver.quit()

# -------- DATAFRAME --------
df = pd.DataFrame(data)

# -------- LIMPIEZA FINAL --------
df = df.drop_duplicates()

print(f"\nTotal de registros: {len(df)}")

# -------- EXPORTAR --------
df.to_excel("terrenos_final.xlsx", index=False)

print("\nArchivo guardado como terrenos_final.xlsx")