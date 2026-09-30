# Jatkaminen toisella koneella – ALA 0.2.0

Päivitetty 30.9.2026. Tämä on keskeytyneen paikallisen 0.2-työn säilytyshaara `codex/v0.2-learning-quiz-handoff`, EI nykyisen main-haaran korvaaja. Sen lähtöcommit on `a3820e9`. Tarkistushetkellä toisella koneella jatkettu main oli jo versiossa 0.2.3-dev, commit `24ad5fbf6548127b7f14afee701d84945c16261e`, ja sen x64/ARM64-CI oli onnistunut.

Jatka sovelluksen varsinaista kehitystä uusimmasta main-haarasta ja lue siellä `AGENTS.md` sekä `docs/HANDOFF_0_2_3.md`. Älä yhdistä tätä haaraa sellaisenaan: tavoitteiden toteutus, tietokantamuutokset, käynnistys ja käyttöliittymä ovat osittain päällekkäisiä mainin kanssa. Poimi tästä tarvittaessa erikseen monivalinnan tilannekuviin perustuva pisteytys, korttien muokkaus, opiskelutuotosten vienti ja niiden testit. Sovita ne nykyiseen tietomalliin ja testaa yhdistelmä. Alla oleva tilannekuva kuvaa tämän haaran työtä 28.9., ei mainin nykyisiä puutteita.

## Lähtökohta

Sovellus on yleinen Windows 11 -oppimistyötila mille tahansa kurssille. Säilytä tämä repositorio erillään esimerkkikurssista. Älä julkaise kurssimateriaaleja, opiskelutietoja, tietokantoja, ajonaikaisia istunto-osoitteita tai tunnuksia. `PRODUCT_REQUIREMENTS.md` kuvaa tuotesuunnan. Käyttäjä on hyväksynyt tavalliset toteutustoimet ilman toistuvia lupakyselyjä.

## Tässä versiossa toteutettu

- `ala/learning.py`: muokattavat tavoitteet, moduulinimet, esitiedot ja lähdeankkurit. Riippuvuussyklit, saman tavoitteen viittaus ja eri kurssiin osoittava riippuvuus hylätään.
- Tavoitteiden etenemisarvio on erillinen materiaalin lukumerkinnöistä. Esitietojen valmius on ohjaava tieto, ei virallinen osaamisarvio.
- Monivalintakysymyspankki, neljä vaihtoehtoa, oikea vastaus ja perustelu. Harjoitus tallentaa kysymysten tilannekuvan ennen vastaamista. Pisteytys on deterministinen ja toistettu lähetys palauttaa saman tallennetun tuloksen.
- Korttien muokkaus sekä tietotyyppikohtainen opiskelutuotosten JSON-vienti esikatselulla.
- `web/learning.js`: näiden toimintojen FI/EN-käyttöliittymät, tavoitteiden riippuvuusnäkymä ja otsikoista ehdotettavien tavoitteiden hyväksyntä.
- Tietokantaversio 2. Vanha tietokanta päivitetään lisäämällä taulut; varmuuskopioiden versiot 1 ja 2 hyväksytään. Aiemmat aineistot ja opiskelutiedot säilyvät.
- `tools/generate_icon.py` generoi `assets/ala.ico`-kuvakkeen rakennusvaiheessa. `tools/install_shortcut.ps1` luo vain ALA:n oman oikotien. Rakennusskripti sisällyttää kuvakkeen EXE:en ja oikotieskriptin pakettiin.

## Varmistetut tulokset

- 18 yksikkö- ja HTTP-testiä läpäisty paikallisessa Windows-ympäristössä.
- Molempien JavaScript-tiedostojen syntaksitarkistus läpäisty.
- Version 0.2 Windows x64 -EXE rakennettu. Pakatun EXE:n toimintatesti läpäisi kaikki kolme tuontimuotoa, PDF-kuvan, asetukset, muistiinpanot, tavoitteet, monivalinnan pisteytyksen, kortin muokkauksen, varmuuskopioinnin ja tietojen säilymisen uudelleenkäynnistyksessä.
- Selaimessa on varmistettu tavoitteen luonti, lähdeankkuri ja tallennetun tavoitteen näkyminen riippuvuusnäkymässä. Koko uuden käyttöliittymän läpikäynti jäi kesken käyttäjän pyydettyä välitöntä synkronointia.
- Version 0.1 GitHubin x64- ja ARM64-rakennustestit läpäisivät. Version 0.2 julkaisu käynnistää uuden työnkulun; tarkista sen tulos Actions-välilehdeltä.

## Seuraavat tehtävät

1. Tarkista tämän commitin Windows x64- ja ARM64-työnkulkujen tulokset. Korjaa mahdolliset aidot virheet ennen lisäominaisuuksia.
2. Viimeistele selaintestaus: tavoiteriippuvuus ja syklin virheilmoitus, monivalintakysymyksen luonti → vastaus → pisteet → uusinta, kortin muokkaus, opiskelutuotosten esikatselu/vienti sekä varaston vaihto.
3. Asenna työpöytäkuvake käyttäjän haluamalle koneelle `install_shortcut.ps1`-skriptillä ja varmista kohde. Työpöydän ALA.lnk-kuvaketta ei ollut vielä asennettu tämän tilannekuvan julkaisuhetkellä.
4. Tarkista tavoitekontekstin tyhjentyminen myös sivunvaihdossa, keskeneräisen monivalinnan jatkamiskokemus ja ison tavoitejoukon käytettävyys. Nämä ovat jatkotarkistuksia, eivät varmennettuja virheitä.
5. Päivitä julkaisuohje ja QA-raportti lopullisen käyttöliittymätestin jälkeen, paketoi jakelu ja julkaise testatut muutokset.
6. Tuotesuunnitelman seuraavat laajennukset: pilvimallisovitin ja avainten turvallinen säilytys, lähdeviitteiden pysyvyys keskusteluhistoriassa, tuonnin hyväksyntäesikatselu, OCR, miellekartat ja puhe. Älä väitä näitä jo toteutetuiksi.

## Komennot

```powershell
git clone https://github.com/jjsauvola-tech/AgenticLearningApplication.git
cd AgenticLearningApplication
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt pyinstaller==6.22.3
.\.venv\Scripts\python -m unittest discover -s tests -v
.\.venv\Scripts\python main.py
.\build_windows.ps1 -Python .\.venv\Scripts\python.exe
.\.venv\Scripts\python tools/smoke_packaged.py dist/ALA/ALA.exe
```

Valmis paketti ei vaadi opiskelijalta Pythonia. GitHub Actions tuottaa x64- ja ARM64-paketit. Käyttäjän oma varasto siirretään sovelluksen varmuuskopioinnilla ja palautuksella; GitHub sisältää lähdekoodin, ei käyttäjädataa.
