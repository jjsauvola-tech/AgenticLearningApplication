# Jatkaminen toisella Windows-koneella — 0.2.3-dev

## Ohjelma

Hae GitHubista uusin `main` (tai sama julkaistu `codex/learning-goals`-haara). Älä kopioi tämän koneen localhost-osoitetta toiselle koneelle.

```powershell
git pull --ff-only
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/install-desktop.ps1
```

Jos `.venv` ja riippuvuudet ovat jo kunnossa, niitä ei tarvitse asentaa uudelleen. Käynnistä työpöydän **ALA 0.2.3-dev** tai `Start-ALA.cmd`. Käynnistys tarkistaa paikallisen lähdekoodin version; GitHub-muutokset haetaan erikseen `git pull` -komennolla. Se ei päivitä muita työpöydän kuvakkeita tai Windows-asetuksia.

Ohjelma käyttää `%LOCALAPPDATA%\ALA`-hakemistoa. Käynnistin pitää samalla koneella osoitteen ja istuntotunnisteen samoina päivitysten yli, jos portti on käytettävissä. Tunniste pysyy paikallisessa runtime-tiedostossa eikä kuulu Gitiin. Ulkopuoliset Origin/Host-pyynnöt ja tunnisteettomat kirjoitukset estetään edelleen.

## Aineisto ja opiskelutiedot

GitHub sisältää ohjelman, testit ja speksit. Se ei sisällä kurssiaineistoa, muistiinpanoja, mallipainoja tai istuntotunnisteita.

Täyden oppimisvaraston siirto: **Asetukset → Varmuuskopiointi → Vie varmuuskopio**, siirrä `.ala.zip` omalla tiedostonsiirtotavallasi ja palauta se toisen koneen ALA:ssa. Palautus luo uuden varaston. Pelkkä release-kansion tuonti tuo aineistot, mutta ei tämän koneen muistiinpanoja tai opiskelumerkintöjä.

Muistiinpanojen tallentamattomat luonnokset säilyvät kirjoittamiseen käytetyssä selaimessa. Ne eivät siirry Gitin tai oppimisvaraston varmuuskopion mukana ennen onnistunutta tallennusta. Tallennuksen epäonnistuessa paina uudelleen Tallenna yhteyden palattua; sama tunniste estää kaksoiskopion.

## Käyttöliittymä ja AI

- Dokumentti ja Kalvot ovat vierekkäin yhteisessä palkissa kaikissa kolmessa näkymässä. Kummallakin on oma viimeinen lukukohta. Saman moduulin dokumentit ja kalvot yhdistetään tuonnin kokoelmatiedon avulla; sivunumeroita ei väitetä yksi yhteen vastaaviksi.
- Moduuliagentit ovat sivupalkissa, eivät enää toistuvassa yläpalkissa. Moduulin alla ovat lähteen otsikoista johdetut aiheasiantuntijat. Valinta rajaa tutorin lähteen ja asiantuntijaroolin kyseiseen aiheeseen. Tämä on yhteisen mallin roolitus, ei itsenäisesti validoitu asiantuntijajärjestelmä.
- Käynnistä AI käynnistää tarvittaessa koneelle jo asennetun Ollaman ja lataa valitun, jo asennetun mallin muistiin. Puuttuva asennus tai malli ohjaa asetuksiin; ohjelma ei lataa ohjelmistoja tai mallipainoja automaattisesti.
- Tässä versiossa on paikallinen Ollama-yhteys. Erillinen pilvipalveluliitin ei ole toteutettu; käyttöliittymä ei väitä käynnistävänsä pilvimallia. Sen toteutuksessa tarvitaan palveluvalinta, tunnistautuminen ja selkeä tieto aineiston lähettämisestä.
- GPT-OSS käyttää Ollaman `low`-päättelyasetusta ja suurempaa vastausbudjettia; muut nykyiset mallit käyttävät aiempaa ei-päättelytilaa. Lähdevalidointi säilyy. [Ollaman mallikohtaiset päättelyasetukset](https://github.com/ollama/ollama/blob/main/docs/capabilities/thinking.mdx).
- PPTX-kuva tarvitsee tällä Windows-toteutuksella asennetun PowerPointin. Tekstinäkymä toimii ilman esikatselun onnistumista.

## Testaus ja rajat

Automaattinen koko testijoukko sekä selaimessa dokumentti–kalvovaihto, lähdeasiantuntijan valinta, AI-käynnistys ja muistiinpanon tallennus. Tarkemmat tulokset kirjataan `QA_0_2_3.md`-tiedostoon.

Uusi paketoitu EXE, puhtaan toisen koneen asennus, lepo/paluu ja pitkäkestoinen kuormitus ovat edelleen erillisiä hyväksymisportteja. Sokraattisen oppimisen koko tilakone ja itsenäisen osaamisen arviointi ovat suunnitelmassa, eivät tämän korjausversion valmiita ominaisuuksia.
