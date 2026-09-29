# ALA: pedagoginen agentti-UX kolmessa näkymässä

29.9.2026 · Toteutussuunnitelma ja ensimmäisen kokeilun rajaus

## Päätös ja tutkimusperusta

ALA säilyttää kolme nykyistä näkymäänsä: aineiston opiskelu, AI-opettaja ja osaamisen varmistaminen. Niitä yhdistävät näkyvä tutor, moduulikohtaiset agenttihahmot sekä opiskelijan omaan työskentelyyn perustuva oppimispolku. Hahmot ilmaisevat sovelluksen toimintaa, eivät opiskelijan oletettuja tunteita. “10x parempi” on kehityksen suunta, ei mitattu tulos.

Ben Degenin [Resurrecting Socrates in the Age of AI](https://arxiv.org/abs/2504.06294), arXiv:2504.06294, 5.4.2025, on **tutkimusprotokolla**, ei vaikuttavuustutkimuksen tulosraportti. Suunnitelmassa verrataan sokraattista tutoria tavalliseen chatbotiin noin 80 biologian opettajaopiskelijalla. Opiskelija muodostaa ensin oman tutkimuskysymyksen, kehittää sitä tuetusti ja soveltaa opittua uuteen ilmiöön. Arviointiin kuuluvat riippumattomat asiantuntija-arviot ja reflektio. Hypoteeseissa tavallinen chatbot voi tuottaa paremman lopputuotoksen, vaikka sokraattinen tutor voisi tukea paremmin siirtovaikutusta. Siksi ALA:n tulee erottaa avustetun vastauksen laatu itsenäisestä osaamisesta. Protokolla ei osoita animoitujen hahmojen hyötyä; niiden vaikutus on arvioitava erikseen.

Liite `ai_tutor_srs_v2.docx` käsitellään alustavana vaatimusehdotuksena. Sen tuotantovalmiutta, suojaustarkkuutta ja suorituskykyä koskevat väitteet eivät ole hyväksymistestien näyttöä.

## Kolme näkymää

| Näkymä | Opiskelijan työ | Agentit ja käyttöliittymä | Tallentuva näyttö |
|---|---|---|---|
| 1. Opiskelu | Lue alkuperäinen kalvo tai asiakirja, tee oma havainto ja yhdistä se tavoitteeseen. | Vasemmalla graafinen moduulipolku, keskellä aineisto ja omat merkinnät, oikealla tutor. Aktiivisen moduulin hahmo näkyy myös yhteisessä agenttirivissä. | Lähdekohtainen merkintä, oma selitys, opiskelumerkintä ja viimeinen lukukohta. |
| 2. AI-opettaja | Kehitä omaa ajatusta yhden kysymyksen avulla kerrallaan. Pyydä vihje tai selitys tarvittaessa. | Tutor on pääroolissa. Moduulin agentti muistuttaa tavoitteesta ja lähteestä. Keskellä keskustelu ja näkyvä työvaihe; oma alkuperäinen vastaus säilyy vertailtavana. | Oma yritys, käytetty tuki, tarkistettu vastaus ja reflektio muutoksesta. |
| 3. Osaamisen varmistaminen | Palauta mieleen ilman aineistoa ja sovella uuteen tilanteeseen. | Aktiivinen moduuli ja tutor säilyvät näkyvissä. Tehtävän tila kertoo, saako apua käyttää. Vastauksen jälkeen palaute näyttää perustelut ja seuraavan harjoituksen. | Itsenäinen vastaus, arviointiperusteet, palaute ja myöhempi uusintayritys. |

Työpöydällä kaikki moduulit ovat löydettävissä yhteisestä agenttirivistä. Kapealla näytöllä tutor pysyy näkyvissä ja moduulirivi vierii vaakasuunnassa. Kaikkien hahmojen samanaikainen mahduttaminen puhelimen leveyteen heikentäisi luettavuutta. Valittu moduuli on aina selvästi merkitty; agenttinimestä avautuu sen aineisto, tavoite ja seuraava tehtävä.

Opiskelunäkymän vasen graafi näyttää moduulien järjestyksen, etenemisrenkaan ja täsmällisen tekstin, esimerkiksi “6 / 12 osiota merkitty opiskelluksi”. Luettu tai merkitty aineisto ei ole hallittua osaamista. Osaamisnäyttö esitetään myöhemmin erillisenä tunnisteena, josta pääsee tehtävään ja arviointiin. Oppaiden, lähteiden ja laadunvarmistuksen kansiot erotetaan jatkossa varsinaisista opetusmoduuleista tuonnin metatiedoilla. Ensimmäinen kokeilu näyttää nykyiset aineistoryhmät sellaisinaan.

## Pedagoginen ohjaus

Tutorin tavoitetilakone on **havainnoi → oma yritys → täsmennä → perustele → tarkastele vaihtoehtoa → korjaa → sovella → reflektoi**. Kaikkia vaiheita ei pakoteta joka keskusteluun. Opiskelija näkee aina, miksi seuraava kysymys auttaa. Yksi varsinainen kysymys esitetään kerrallaan; usean kohdan kuulustelua vältetään.

Kolme tukitilaa ovat näkyviä ja erotettuja:

- **Oppiminen:** oma yritys ensin kun se on tarkoituksenmukaista; pyydettäessä vihje, käsitteen selitys tai perusteltu esimerkki. Suora avunpyyntö ei ole hyökkäys.
- **Harjoittelu:** vihjeet etenevät pienestä suunnasta osittain ratkaistuun esimerkkiin. Käytetty tuki tallentuu yrityksen yhteyteen.
- **Itsenäinen näyttö:** tehtävän avustusrajat kerrotaan etukäteen. Ratkaisuapu pysyy suljettuna suorituksen aikana; palaute avautuu sen jälkeen. Opiskelija voi siirtyä harjoitteluun menettämättä aiempaa työtään.

“En ymmärrä” avaa vaihtoehdot: selitä toisin, anna konkreettinen esimerkki, pienennä tehtävää tai pidä tauko. Kolme virheellistä vastausta ei automaattisesti todista turhautumista eikä käynnistä rangaistusta. Käsitevirhe on ehdotus, joka sidotaan vastauksen kohtaan ja voidaan korjata. Fysiikan tai matematiikan oletuksia ei käytetä kaikkien kurssien pohjana.

Tutkimuskysymystehtävissä käytetään soveltuvaa arviointirubriikkia: rajaus, tutkittavuus, käsitteiden selkeys, näyttö ja toteutettavuus. PICOT voidaan tarjota sopivaan tutkimusasetelmaan, ei kaikille aloille pakolliseksi lomakkeeksi. Opiskelijan omasta perustelusta, palautteen käytöstä ja uudesta sovelluksesta annetaan täsmällinen palaute. Viestimäärä, opiskeluaika tai hahmon hymy eivät nosta osaamisarviota.

## Hahmot, eleet ja motivaatio

SVLA GPU Agents -projektista kopioidut alkuperäiset kasvokerrokset sijaitsevat `web/assets/svla-faces/`-hakemistossa. Alkuperä, lähderevisio ja SHA-256-tiivisteet ovat [SVLA_ASSET_PROVENANCE.json](SVLA_ASSET_PROVENANCE.json)-tiedostossa. Kopiointi on käyttäjän nimenomaisesti pyytämä. Lähteessä ei löytynyt omaa julkista lisenssiä tälle grafiikalle; julkisen jatkojakelun oikeudet on tarkistettava ennen sellaista julkaisua. SVLA:n palvelinta tai sen animaatiomoottoria ei tuoda ALA:n riippuvuudeksi.

| Todellinen tila | Ilme / ele | Näkyvä selite |
|---|---|---|
| Valmis | Kysyvä, rauhallinen | Valmis pohtimaan kanssasi |
| Aineisto avoinna | Lukeva | Moduulin ja lähteen nimi |
| Pyyntö käynnissä | Miettivä; pieni hengitys- ja katseanimaatio | Käsittelen pyyntöäsi |
| Odottaa opiskelijaa | Kysyvä; ei kiirehtivää liikettä | Sinun vuorosi, kun olet valmis |
| Merkinnät valmiit | Lyhyt hyväksyvä ele / onnistumisilme | Osiot merkitty opiskelluksi |
| Tekninen virhe | Korjaava, rauhallinen | Pyyntö ei onnistunut; työsi säilyy |

Opiskelijalle ei näytetä vihaista, pettynyttä tai syyllistävää agenttia virheellisen vastauksen vuoksi. Ei katkeavia pakollisia päiväputkia, tulostauluja tai kiireen tuntua. Opiskelija voi palata tauolta ilman menetystä. Moduulin identiteetti rakentuu nimestä, väristä ja tehtävästä; väri ei koskaan yksin välitä tilaa. Tutorin eleet kuvaavat kuvitteellisen käyttöliittymähahmon toimintaa, eivät todellisia tunteita tai tietoisuutta.

Liike on vähäistä ja keskittyy aktiiviseen toimintoon. Asetus sekä käyttöjärjestelmän vähennetyn liikkeen valinta pysäyttävät sen, samoin piilotettu välilehti. Ilme, teksti ja tila toimivat myös ilman animaatiota. Ääntä ei käynnistetä automaattisesti. Agentit eivät peitä kalvoa, kirjoitusaluetta, virheilmoitusta tai toimintopainikkeita.

## SRS:n vaatimusten päätökset

| Liitteen ehdotus | ALA-ratkaisu |
|---|---|
| Ehdoton valmiiden vastausten kielto | Korvataan näkyvällä tukitilalla. Oppimistila saa selittää; itsenäinen näyttö noudattaa sovittuja rajoja. |
| Yksi kysymys kerrallaan | Säilytetään sokraattisen vuoron invarianttina; käyttöliittymän avunvalinnat eivät ole uusia tehtäväkysymyksiä. |
| Käsitevirheiden tunnistus | Lähteeseen ja omaan yritykseen sidottu epävarma arvio; ei diagnoosia opiskelijasta. |
| Vastausta edeltävä LLM-valvoja | Rakenteen tarkistus ensin, tarvittaessa pedagoginen arvio. Kustannus, viive ja väärät hylkäykset mitataan. |
| Regex ja luokitin hyökkäyksille | Käytetään osana kerroksittaista suojausta. Tuotu aineisto on dataa, eikä se saa muuttaa ohjaussääntöjä. |
| Kolme virhettä / turhautumislippu | Opiskelijan oma avuntarve ohjaa tukea. Automaattisia tunnetulkintoja ei tallenneta. |
| Summarointi 10 viestin välein, 4000 tokenia | Tokenbudjetti ja mallin kyvykkyys ratkaisevat. Alkuperäiset yritykset, lähdeviitteet ja tehtävän rajat säilyvät erillisinä tietueina. |
| WebSocket sekä SSE | Ensimmäinen toteutus säilyttää nykyisen HTTP:n. Pitkiin töihin lisätään yksi versioitu tapahtumakanava tarvittaessa; ei kahta rinnakkaista protokollaa. |
| Valvottu mutta välittömästi suoratoistettu vastaus | Käyttöliittymä voi näyttää työtilan heti. Tarkistamaton vastaus ei ilmesty arvioinnin ohi; validoitu valmis vuoro julkaistaan atomisesti. |
| Next.js/FastAPI/PostgreSQL/Redis | Nykyinen paikallinen Python-palvelin ja SQLite säilyvät. Monikäyttäjätarve ja mitattu kuorma perustelevat mahdolliset myöhemmät vaihdot. |
| LiteLLM/Langfuse ja analytiikka | Selkeä malliyhdyskäytävä; ulkoinen lokitus vain tietoisella valinnalla. Oppijan tekstiä ei lähetetä telemetriaan oletuksena. |
| TTFT < 1,2 s; 99,5 % suojaustarkkuus; 90 % testikattavuus | Testattavat tavoiteprofiilit mallin ja laitteen mukaan. Suojaukselle myös väärien hylkäysten mittaus; kattavuusprosentti ei todista pedagogista tai tietoturvallista oikeellisuutta. |

## Toteutusmoduulit ja sopimukset

1. **Aineisto ja moduulikartta:** nykyinen tuonti ja dokumenttivarasto; vakaa `module_id`, tyyppi ja tavoitteet liitetään dokumentteihin. Tiedostonimi ei ole identiteetti.
2. **Tutorin ohjain:** hallitsee tukitilan ja pedagogisen vaiheen. Malli ehdottaa vuoroa; ohjain tarkistaa sen ennen julkaisua.
3. **Lähdehaku:** palauttaa katkelmat ja pysyvät lähdetunnisteet. Tuodun tekstin ohjeita ei nosteta järjestelmäohjeiksi.
4. **Vihjeet ja tehtävät:** tuottaa tai hakee tavoitteeseen sopivan vihjeen; erottaa harjoittelun itsenäisestä näytöstä.
5. **Näyttö ja palaute:** tallentaa yrityksen, avustustason ja rubriikin. Ei päivitä numeerista mastery-arvoa ilman määriteltyä arviointimallia.
6. **Muistiinpanot ja reflektio:** säilyttää oman yrityksen ja korjauksen rinnakkain. Vastauksen kopiointi muistiinpanoihin sekä leikepöydälle säilyvät.
7. **Malliyhdyskäytävä:** aikarajat, peruutus, mallin kyvykkyydet ja redaktoitu diagnostiikka. Verkkovirhe ei tyhjennä työtilaa.
8. **Agenttien esityskerros:** muuntaa todelliset tilat hahmoiksi. Ei tee omia mallikutsuja eikä päätä oppimistuloksista.

Moduulin agentti on ensisijaisesti pedagoginen rooli ja oma näkyvä identiteetti. Jokaiselle hahmolle ei käynnistetä erillistä LLM-prosessia. Yksi ohjain käyttää kulloisenkin moduulin tavoitetta, lähteitä ja opiskelutilaa. Tämä välttää tarpeettoman kustannuksen, kilpailevat vastaukset ja epäselvän vastuun.

Seuraavan vaiheen tietueet: `learning_attempt(id, vault_id, module_id, task_id, mode, original_answer, support_level, created_at)`, `tutor_turn(id, attempt_id, phase, question, source_refs, validation, revision)` ja `learning_evidence(id, attempt_id, rubric_version, assessment, provenance)`. Migraatiot ovat versioituja ja varmuuskopioituja. Henkilökohtainen tila ei ylitä oppimisympäristön rajoja.

Tuleva `POST /api/tutor/turn` saa `request_id`, `vault_id`, `module_id`, `attempt_id`, `expected_revision`, `mode` ja käyttäjän tekstin. Palvelin validoi omistajuuden ja tilasiirtymän, hylkää vanhan revision sekä palauttaa saman tuloksen saman pyynnön uusinnalle. Käyttöliittymä sivuuttaa myöhäisen vastauksen, jos oppimisympäristö tai yritys on vaihtunut. Tämä on suunnitelma, ei nykyisen `/api/chat`-rajapinnan luvattu ominaisuus.

## Toteutusvaiheet ja hyväksyminen

**A. Nyt toteutettu UX-kokeilu:** `?ux=agents` ottaa käyttöön SVLA-hahmot, aineistoryhmien etenemisgraafin, kolmen näkymän yhteisen agenttirivin, toimintotilan ja liikeasetuksen. Perusnäkymään pääsee takaisin yhdellä painikkeella. Se käyttää nykyisiä dokumentteja ja opiskelumerkintöjä. Sokraattista ohjainta, uutta arviointia tai automaattista tunnetulkintaa ei ole tässä vaiheessa toteutettu. Aktiivisen moduulin ohjekortit ovat käyttöliittymätekstiä, eivät mallin tuottamia pedagogisia päätöksiä.

**B. Seuraava rajattu toimitus:** yksi tutkimuskysymystehtävä alusta loppuun: oma yritys, lähteeseen sidottu kysymys, vihjetasot, oma korjaus, siirtotehtävä ja reflektio. Tallennus ja keskeytyksestä palautuminen toteutetaan ennen uusia sisältötyyppejä. Testataan normaali avunpyyntö, virheellinen aineisto-ohje, katkennut yhteys, kaksoislähetys ja oppimisympäristön vaihto.

**C. Kurssin laajennus:** jokaiselle opetusmoduulille oma tavoite, tehtäväperhe ja näyttö. Oppaan ja lähdekokoelman agentit pysyvät opastavina rooleina. Opettajan koonti rakennetaan vain suostumus- ja tietojen näkyvyyssääntöjen jälkeen.

Hyväksymiskriteerit:

- Pitkä vastaus, pitkä moduulinimi ja alkuperäinen kalvo eivät vuoda paneelista. Näppäimistö, 200 % zoom ja 390 px leveys säilyttävät keskeiset toiminnot.
- Tutor ja aktiivinen moduuli ovat tunnistettavissa kaikissa näkymissä. Hahmokuva ei ole ainoa tilailmaisin.
- Liikkeen poisto ei poista informaatiota. Taustavälilehden animaatio pysähtyy.
- Opiskelumerkinnät ja osaamisnäyttö eivät sekoitu; prosentti on tarkistettavissa laskennan lähteistä.
- Mallivirhe, palvelinkatko tai palautus ei tuhoa luonnosta, omaa yritystä tai aiempaa näyttöä.
- Graafinen kerros ei lisää taustalla mallikutsuja. Lisäresurssit mitataan; kokeilun PNG:t ovat paikallisia ja rajallisia.
- Vaikuttavuuspilotissa verrataan agentti- ja perusnäkymää samalla sisällöllä: tehtävän löytyminen, avun käytettävyys, koettu kuormitus sekä itsenäinen siirtotehtävä. Pelkkä sovelluksessa vietetty aika ei ole onnistumismittari.
- Pitkäkestoisuus, Windowsin lepo/paluu ja puhtaan koneen asennus pysyvät erillisinä avoimina tuotantovalmiuden portteina, kunnes ne on oikeasti ajettu.
