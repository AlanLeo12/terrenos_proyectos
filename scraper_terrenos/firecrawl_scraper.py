from firecrawl import FirecrawlApp
import re
import json
import os
import math
import time
from dotenv import load_dotenv

# -------- CONFIG --------
load_dotenv()
API_KEY = os.getenv('FIRECRAWL_API_KEY')

print(f"API KEY: {API_KEY}")

app = FirecrawlApp(api_key=API_KEY)

# -------- FUNCIONES --------

def save_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# -------- CRAWLER --------

def scrapear_pagina(url):
    print(f"Crawling página: {url}")

    try:
        data = app.scrape(url, formats=["links", "markdown"])
    except:
        print("Intentando con proxy...")
        data = app.scrape(url, formats=["links", "markdown"], proxy="stealth")

    links = data.links if hasattr(data, "links") else []
    markdown = data.markdown if hasattr(data, "markdown") else ""

    return links, markdown


def obtener_paginas(markdown):
    nums = re.findall(r'(\d{1,3}(?:,\d{3})*)', markdown)

    if nums:
        total = int(nums[0].replace(',', ''))
        return math.ceil(total / 30)
    else:
        return 3


def obtener_urls(url_base, nombre_archivo):
    all_links = []

    links, markdown = scrapear_pagina(url_base + "?page=1")

    links = [l for l in links if "lamudi.com.mx/detalle" in l]
    all_links.extend(links)

    num_paginas = obtener_paginas(markdown)
    print(f"Total de páginas: {num_paginas}")

    for i in range(2, min(num_paginas, 3)):
        url = url_base + f"?page={i}"

        links, _ = scrapear_pagina(url)
        links = [l for l in links if "lamudi.com.mx/detalle" in l]

        all_links.extend(links)

    links_unicos = list(set(all_links))

    print(f"Total de links: {len(links_unicos)}")

    save_json(links_unicos, f"links_{nombre_archivo}.json")

    return links_unicos


# -------- SCRAPER --------

def scrapear_propiedades(links, nombre_archivo):
    resultados = []

    print("Extrayendo propiedades...")

    links = links[:10]  # limitar uso de API

    batches = [links[i:i + 5] for i in range(0, len(links), 5)]

    for i, batch in enumerate(batches):
        print(f"Procesando batch {i+1}")

        try:
            data = app.batch_scrape(batch, formats=["markdown"])
        except:
            print("Reintentando con proxy...")
            data = app.batch_scrape(batch, formats=["markdown"], proxy="stealth")

        for item in data.data:
            texto = item.markdown if hasattr(item, "markdown") else ""
            texto = re.sub(r'\s+', ' ', texto)

            resultados.append({
                "url": item.metadata.url if hasattr(item.metadata, "url") else "",
                "contenido": texto[:800]
            })

        time.sleep(1)

    save_json(resultados, f"resultados_{nombre_archivo}.json")

    return resultados


# -------- MAIN --------

if __name__ == "__main__":

    urls = {
        "toluca": "https://www.lamudi.com.mx/estado-de-mexico/toluca/terreno/for-sale/",
        "metepec": "https://www.lamudi.com.mx/estado-de-mexico/metepec/terreno/for-sale/"
    }

    for nombre, url in urls.items():
        print(f"\n--- PROCESANDO {nombre.upper()} ---\n")

        links = obtener_urls(url, nombre)
        scrapear_propiedades(links, nombre)

    print("\nProceso terminado")