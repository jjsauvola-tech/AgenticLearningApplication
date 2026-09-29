# Agentti-UX:n tarkistus 29.9.2026

Rajaus: ensimmäinen valinnainen esityskerros, `?ux=agents`. Pedagogisen ohjaimen suunnitelma on `UX_PEDAGOGY_SPEC.md`-tiedostossa. Käyttäjän varsinaiseen oppimisvarastoon ei lisätty testimerkintöjä.

## Automaattiset tarkistukset

- Python: 47 testiä läpäisi. Mukana käynnistyskilpailu ja kaatumisesta palautuminen, tuonti/palautus, varastojen eristys, mallivastauksen validointi sekä PNG-tiedostojen tarjoilu ja projektitiedostojen suojaus.
- JavaScript: 16 testiä läpäisi. Mukana aikarajat, myöhäiset vastaukset, luonnokset, pitkän vastauksen kopiointi, kansiotuonti sekä neljä agenttikerroksen testiä.
- Agenttitestit tarkistavat opiskeltujen osioiden laskennan, erillisten kurssien samannimiset moduulit, HTML-escapingin sekä rinnakkaisten pyyntöjen todellisen toimintatilan ja varastorajauksen.

## Selaimessa tarkistettu

Kurssin varmuuskopiosta palautettu erillinen `Agentti-UX kokeilu`: 42 dokumenttia, 12 aineistoryhmää. Alkuperäisiä release-tiedostoja ei muutettu.

- Opiskele-, AI-opettaja- ja Osaamisen harjoittelu -näkymät avautuivat ja yhteinen agenttirivi säilyi.
- Kaikki kasvokerrosten kuvat latautuivat. Moduulipolun ja agenttirivin näppäimistövalinta vaihtoi vastaavaan aineistoon.
- Ensimmäisen oppaan osion opiskelumerkintä päivittyi graafiin muodossa `1 / 15 · 7 %`.
- Liikekytkin muutti `aria-pressed`-tilan ja pysäyttävän CSS-luokan. Valinta säilyi uudelleenlatauksessa.
- 390 px näkymässä dokumentin leveys ei ylittänyt ikkunan leveyttä. Työpöydän 1440 px näkymässä kaikki kolme opiskelupaneelia näkyivät.
- Ilman valittua mallia harjoituskysymys palautti selkeän virheen; tutor vaihtui korjaavaan ilmeeseen ja harjoituslomake säilyi.
- Käyttöliittymän virhelokissa ei ollut JavaScript-virheitä tarkistuksen aikana.

Selainohjauksen suuri näkymäkoko aiheutti joissakin osoitinnapsautuksissa työkalun kohdistusvirheen. Vastaavat moduulivalinnat varmistettiin näppäimistöllä ja DOM:n näkyvällä lopputuloksella. Yksi selaimen valintakutsu viivästyi pitkäksi aikaa; tätä ei tulkittu sovelluksen suorituskykymittaukseksi.

## Avoimet hyväksymisportit

Ei vielä väitettä tuotantovalmiudesta tai paremmista oppimistuloksista. Sokraattinen tilakone, rubriikkiperusteinen arviointi ja itsenäinen siirtotehtävä ovat seuraavaa toimitusta. Ruudunlukijan koko työnkulku, käyttöjärjestelmän liikeasetus, 200 % zoom, pitkäkestoinen UX-kuorma, Windowsin lepo/paluu ja puhtaan koneen asennus tarvitsevat erillisen testiajon. Käynnistinskriptin testikopiolle tekemä käynnistys ei tässä ympäristössä avannut tietokantaa; sama testipalvelin käynnistettiin onnistuneesti suoraan projektin Python-komennolla. Tätä käynnistinrajoitusta ei merkitä ratkaistuksi.
