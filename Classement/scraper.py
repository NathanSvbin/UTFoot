import requests
from bs4 import BeautifulSoup
import json
import os
import csv
import chardet

print("Répertoire courant :", os.getcwd())
print("Fichiers dans Championnat :", os.listdir("Championnat"))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "DNT": "1"
}

PROXIES = [
    "http://51.159.66.45:3128",
    "http://134.209.29.120:8080",
    "http://195.201.231.22:8080"
]


def get_with_proxy(url):
    """Essaye les proxys un par un jusqu'à trouver celui qui fonctionne."""
    for proxy in PROXIES:
        try:
            print(f"🌐 Test proxy : {proxy}")
            response = requests.get(
                url,
                headers=HEADERS,
                proxies={"http": proxy, "https": proxy},
                timeout=15
            )

            if response.status_code == 200:
                print(f"✔ Proxy OK : {proxy}")
                return response
            else:
                print(f"❌ HTTP {response.status_code} via {proxy}")

        except Exception as e:
            print(f"⚠️ Erreur avec proxy {proxy} : {e}")

    print("🚨 Aucun proxy valide n’a été trouvé.")
    return None

def lire_championnats_csv(fichier_csv):
    with open(fichier_csv, "rb") as f:
        encodage = chardet.detect(f.read())["encoding"]

    with open(fichier_csv, "r", encoding=encodage) as f:
        reader = csv.reader(f)
        next(reader)
        championnats = []

        for row in reader:
            if len(row) >= 3 and row[2].startswith("https"):
                id = row[0]
                nom = row[1].strip()
                lien = row[2].strip()
                pays = row[4]

                lien_classement = lien.replace("startseite", "tabelle") + "/saison_id/2025"
                championnats.append((id, nom, lien_classement, pays))

    return championnats

def scrape_championnat(nom, url):
    print(f"\n📥 Récupération du championnat : {nom}")

    response = get_with_proxy(url)
    if not response or response.status_code != 200:
        print(f"❌ Erreur pour {nom}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="items")

    if not table:
        print(f"⚠️ Tableau non trouvé pour {nom}")
        return []

    equipes = []
    rows = table.find("tbody").find_all("tr")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 9:
            continue

        buts = cols[7].get_text(strip=True).split(":")

        equipe = {
            "position": cols[0].get_text(strip=True).split()[0],
            "nom": cols[2].get_text(strip=True),
            "matchs": cols[3].get_text(strip=True),
            "victoires": cols[4].get_text(strip=True),
            "nuls": cols[5].get_text(strip=True),
            "defaites": cols[6].get_text(strip=True),
            "buts_pour": buts[0] if len(buts) > 0 else "0",
            "buts_contre": buts[1] if len(buts) > 1 else "0",
            "difference": cols[8].get_text(strip=True),
            "points": cols[9].get_text(strip=True)
        }

        equipes.append(equipe)

    print(f"✅ {len(equipes)} équipes trouvées pour {nom}")
    return equipes

def main():
    os.makedirs("Classement", exist_ok=True)
    all_data = []

    championnats = lire_championnats_csv("Championnat/championnat_finalV3_lien.csv")

    for id, nom, url, pays in championnats:
        try:
            equipes = scrape_championnat(nom, url)
            if equipes:
                all_data.append({
                    "id_championnat": id,
                    "championnat": nom,
                    "url": url,
                    "id_pays": pays,
                    "saison": 2025,
                    "equipes": equipes
                })

        except Exception as e:
            print(f"❌ Erreur sur {nom}: {e}")

    filepath = "Classement/classements.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Données sauvegardées dans {os.path.abspath(filepath)}")
    print("🏁 Championnats récupérés :", ", ".join([c[0] for c in championnats]))


if __name__ == "__main__":
    main()














