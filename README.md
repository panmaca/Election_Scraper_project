# SCRAPER PROJEKT

## Cíl projektu
Cílem projektu je extrahovat výsledky parlamentních voleb v roce 2017 v České republice pro jednotlivé obce vybraného územního celku. Odkaz na územní celky naleznete [zde](https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ).

## Instalace knihoven
Všechny knihovny potřebné pro spuštění kódu jsou uloženy v souboru `requirements.txt`. Pro instalaci doporučuji vytvořit nové virtuální prostředí a spustit následovně: 

```bash
pip install -r requirements.txt
```
## Spuštění projektu
Po instalaci knihoven je možné spustit projekt pomocí souboru `main.py`. Tento soubor v rámci příkazového řádku vyžaduje dva povinné argumenty: 

```bash
python main.py <odkaz_na_uzemni_celek> <název_souboru.csv>
```

Výsledkem projektu jsou výsledky voleb jednotlivých obcí vybraného územního celku uložené v souboru s příponou `.csv`. 

## Ukázka projektu
Pro ukázku projektu byl zvolen územní celek Prostějov. 

1. argument: https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103
2. argument: vysledky_prostejov.csv

Spuštění: 
```bash
python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103" "vysledky_prostejov.csv"
```

Průběh stahování:
```text
Stahuji data z vybraného url: https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103
Ukládám do souboru: vysledky_prostejov.csv
Hotovo, ukončuji election-scraper.
```

Částečný výstup:
```bash
Kód obce,Název obce,Volići v seznamu,Vydané obálky,Platné hlasy,...
506761,Alojzov,205,145,144,29,0,0,9,0,5,17,4,1,1,0,0,18,0,5,32,0,0,6,0,0,1,1,15,0
589268,Bedihošť,834,527,524,51,0,0,28,1,13,123,2,2,14,1,0,34,0,6,140,0,0,26,0,0,0,0,82,1
```
