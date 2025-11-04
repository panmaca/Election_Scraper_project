"""
main.py: třetí projekt do Engeto Datová analýza s Pythonem

author: Marcela Trávníčková
email: travnickovamarcela@gmail.com
discord: Marcela T. (pan.maca)
"""

import requests
from bs4 import BeautifulSoup as bs
import csv
import sys
import time
from bs4.element import Tag, ResultSet


def validuj_argumenty() -> tuple:
    """Zkontroluje argumenty příkazové řádky a vrátí URL a název souboru."""
    if len(sys.argv) != 3:
        print("Chyba: Zadejte přesně 2 argumenty.")
        print("Správný způsob: python main.py <odkaz> <nazev_souboru.csv>")
        sys.exit(1)

    url_celek = sys.argv[1]
    nazev_souboru = sys.argv[2]

    if "volby.cz" not in url_celek:
        print("Chyba: První argument musí být odkaz na stránku volby.cz")
        sys.exit(1)

    if not nazev_souboru.endswith(".csv"):
        print("Chyba: Druhý argument musí končit .csv")
        sys.exit(1)

    return url_celek, nazev_souboru


def hlavni(url_celek: str) -> tuple:
    """Koordinuje sběr dat z voleb a vrací výsledky, kódy a názvy obcí."""
    vsechny_tabulky = parsovani(url_celek)
    radky_tabulky = projdi_tabulky(vsechny_tabulky)
    vysledky_vsechny_obce, kody, obce_nazvy = projdi_radky(radky_tabulky)
    return vysledky_vsechny_obce, kody, obce_nazvy


def parsovani(url_celek: str) -> ResultSet:
    """Parsuje a vrací všechny tabulky z vloženého odkazu."""
    print("Stahuji data z vybraného url:", url_celek)
    try:
        obsah = requests.get(url_celek)
        parsed = bs(obsah.text, features="html.parser")
        vsechny_tabulky = parsed.find_all("table", {"class": "table"})
        return vsechny_tabulky
    except:
        print(f"Chyba při stahování. Zkontrolujte {url_celek}")
        sys.exit(1)

def projdi_tabulky(vsechny_tabulky: ResultSet) -> list:
    """Prochází parsované tabulky a vrací jednotlivé řádky mimo záhlaví."""
    radky_tabulky = []
    for tabulka in vsechny_tabulky:
        radek_tabulky = list(tabulka.find_all("tr"))
        for radek in radek_tabulky[2:]:
            radky_tabulky.append(radek.find_all("td"))
    return radky_tabulky

def projdi_radky(radky_tabulky: list) -> tuple:
    """Koordinuje sběr a vrací výsledky obcí, jejich kódy a názvy."""
    vysledky_vsechny_obce = []
    odkazy, kody, obce_nazvy = najdi_odkaz_kody_obce(radky_tabulky)
    for odkaz in odkazy:
        href = "https://www.volby.cz/pls/ps2017nss/" + odkaz.get("href")
        parsed_obec = parsovani_obec(href)
        vysledky_obce = vysledky_jedne_obce(parsed_obec)
        vysledky_vsechny_obce.append(vysledky_obce)
        time.sleep(3)  # proti agresivnímu scrapingu
    return vysledky_vsechny_obce, kody, obce_nazvy

def najdi_odkaz_kody_obce(radky_tabulky: list) -> tuple:
    """Získává a vrací odkazy na jednotlivé obce, jejich kódy a názvy."""
    odkazy = []
    kody = []
    obce_nazvy = []
    for radek_bunek in radky_tabulky:
        odkaz = radek_bunek[0].find("a")
        if odkaz:
            odkazy.append(odkaz)
            kody.append(radek_bunek[0].text)
            obce_nazvy.append(radek_bunek[1].text)
    return odkazy, kody, obce_nazvy

def vysledky_jedne_obce(parsed_obec: bs) -> dict:
    """Získává a vrací výsledky konkrétní obce."""
    volici, obalky, hlasy = prvni_tabulka(parsed_obec)
    vysledky = projdi_vysledky(parsed_obec)
    strany, hlasy_stran = projdi_strany(vysledky)
    vysledky_obce = {
        "volici": volici,
        "obalky": obalky,
        "hlasy": hlasy,
        "strany": strany,
        "hlasy_stran": hlasy_stran
    }
    return vysledky_obce

def parsovani_obec(href: str) -> bs:
    """Stahuje a parsuje HTML stránku konkrétní obce."""
    try:
        obsah = requests.get(href, timeout=10)
        parsed_obec = bs(obsah.text, features="html.parser")
        return parsed_obec
    except:
        print(f"Chyba při stahování. Zkontrolujte: {href}")
        sys.exit(1)

def prvni_tabulka(parsed_obec: bs) -> tuple:
    """Získává a vrací údaje z první tabulky - voliči, obálky, platné hlasy."""
    statistiky = parsed_obec.find("table", {"class": "table"})
    vsechny_radky = list(statistiky.find_all("tr"))
    bunky = list(vsechny_radky[2].find_all("td"))
    volici = bunky[3].text
    obalky = bunky[4].text
    hlasy = bunky[7].text
    return volici, obalky, hlasy

def projdi_vysledky(parsed_obec: bs) -> list:
    """Získává a vrací výsledky voleb z parsované stránky."""
    vsechny_tabulky = parsed_obec.find_all("table",
                                          {"class": "table"})
    radky_tabulky = najdi_radky(vsechny_tabulky)
    bunky_tabulky = najdi_bunky(radky_tabulky)
    return bunky_tabulky

def najdi_radky(vsechny_tabulky: ResultSet) -> list[Tag]:
    """Prochází tabulky s výsledky a vrací jejich jednotlivé řádky."""
    radky_tabulky = []
    for tabulka in vsechny_tabulky[1:]:
        radky_teto_tabulky = tabulka.find_all("tr")
        radky_tabulky.extend(radky_teto_tabulky[2:])
    return radky_tabulky

def najdi_bunky(radky_tabulky: list[Tag]) -> list:
    """Prochází řádky a vrací hledané buňky řádků."""
    vysledky = []
    for radek in radky_tabulky:
        bunky_radku = radek.find_all("td")
        bunky = [bunky_radku[1].text, bunky_radku[2].text]
        vysledky.append(bunky)
    return vysledky

def projdi_strany(vysledky: list) -> tuple:
    """Získává a vrací názvy stran a počet hlasů."""
    strany = []
    hlasy_stran = []
    for a in vysledky:
        strany.append(a[0])
        hlasy_stran.append(a[1])
    return strany, hlasy_stran


def uloz_do_csv(vysledky_vsechny_obce: list, kody: list, obce_nazvy: list,
                nazev_souboru: str) -> None:
    """Uloží výsledky voleb do CSV souboru."""
    print("Ukládám do souboru:", nazev_souboru)

    with open(nazev_souboru, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)

        strany_hlavicky = vysledky_vsechny_obce[0]["strany"]
        fix_hlavicky = ["Kód obce", "Název obce", "Voliči v seznamu",
                        "Vydané obálky", "Platné hlasy"]
        hlavicky = fix_hlavicky + strany_hlavicky
        writer.writerow(hlavicky)

        for i, vysledky_obce in enumerate(vysledky_vsechny_obce):
            kod = kody[i]
            obec = obce_nazvy[i]
            volici = vysledky_obce["volici"]
            obalky = vysledky_obce["obalky"]
            hlasy = vysledky_obce["hlasy"]
            hlasy_stran = vysledky_obce["hlasy_stran"]

            fix_data = [kod, obec, volici, obalky, hlasy]
            data = fix_data + hlasy_stran
            writer.writerow(data)

    print("Hotovo, ukončuji election-scraper.")


def main() -> None:
    """Hlavní funkce programu - spouští scraping a ukládání dat."""
    url_celek, nazev_souboru = validuj_argumenty()
    vysledky_vsechny_obce, kody, obce_nazvy = hlavni(url_celek)
    uloz_do_csv(vysledky_vsechny_obce, kody, obce_nazvy, nazev_souboru)


if __name__ == "__main__":
    main()
