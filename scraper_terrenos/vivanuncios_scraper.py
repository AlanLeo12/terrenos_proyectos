from firecrawl import FirecrawlApp
import json
import time
import os
import re
from dotenv import load_dotenv

# -------- CONFIG --------
load_dotenv()
API_KEY = os.getenv('FIRECRAWL_API_KEY')

print(f"API KEY: {API_KEY}")

app = FirecrawlApp(api_key=API_KEY)

# -------- URLS --------

urls = [
    "https://www.vivanuncios.com.mx/s-venta-terrenos/toluca/v1c1097l10782p1",
    "https://www.vivanuncios.com.mx/s-venta-terrenos/metepec/v1c1097l10783p1"
]

# -------- FUNCIONES --------

def extraer_precio(texto):
    match = re.search(r'\$\s?[0-9,]+', texto)
    return match.group(0) if match else None


def extraer_metros(texto):
    match = re.search(r'[0-9,.]+\s*m²', texto)
    return match.group(0) if match else None


# -------- MAIN --------

if __name__ == "__main__":

    resultados = []

    for url in urls:
        print(f"Scrapeando página: {url}")

        try:
            data = app.scrape(url, formats=["markdown"], proxy="stealth")
        except:
            print("Reintentando...")
            time.sleep(2)
            continue

        texto = data.markdown if hasattr(data, "markdown") else ""

        resultados.append({
            "url": url,
            "precio": extraer_precio(texto),
            "metros": extraer_metros(texto),
            "contenido": texto[:1000]
        })

        time.sleep(1)

    with open("resultados_vivanuncios.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)

    print("Proceso terminado")