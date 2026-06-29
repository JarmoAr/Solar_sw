# AurinkoOptimo-projektisuunnitelma

## Yhteenveto

AurinkoOptimo on omakotitalon aurinkosähköjärjestelmän optimointiprototyyppi. Järjestelmä lukee Fronius-invertterin tuotanto- ja tehotietoja, hakee sähkön hintatietoa, huomioi sähköyhtiön myyntimarginaalin ja tekee päätöksen tuotannon rajoittamisesta.

Tavoite on välttää taloudellisesti huonoa verkkoon myyntiä silloin, kun nettomyyntihinta on nolla tai negatiivinen. Nettomyyntihinnalla tarkoitetaan pörssihintaa, josta on vähennetty sähköyhtiön myyntimarginaali.

## Rajaus

Ensimmäinen versio on turvallinen prototyyppi:

- lukee invertterin tietoja
- tallentaa mittaukset paikallisesti
- tarjoaa selainkäyttöliittymän asetuksille
- tekee ohjauspäätöksen
- ei vielä kirjoita asetuksia invertteriin

Varsinainen invertterin tehorajoitus toteutetaan vasta erillisen testauksen ja laitemallikohtaisen varmistuksen jälkeen.

## Käyttäjän asetukset

Käyttäjä voi määrittää selainkäyttöliittymässä:

- sähköyhtiön myyntimarginaalin, snt/kWh
- rajan, jonka alittuessa tuotantoa rajoitetaan
- kuinka suuri osuus tuotannosta saa mennä myyntiin rajoitustilanteessa
- järjestelmän maksimimyyntitehon

Esimerkkejä:

- `0 %` myyntiin: verkkoon vienti pyritään estämään rajoitustilanteessa.
- `5 %` myyntiin: pieni ulosmyynti sallitaan mittaus- ja ohjausviiveiden takia.

## Ohjauslogiikka

Laskenta:

```text
nettomyyntihinta (snt/kWh) = pörssihinta (snt/kWh) - sähköyhtiön myyntimarginaali (snt/kWh)
```

Käyttöliittymässä ja pientuotannon asetuksissa hinnat esitetään muodossa `snt/kWh`, koska kuluttajapalvelut ja sähköyhtiöiden pientuotantoehdot käyttävät tätä yleensä. Suurten markkinarajapintojen `€/MWh`-hinnat muunnetaan ohjelman sisällä muotoon `snt/kWh`.

Jos nettomyyntihinta on pienempi tai yhtä suuri kuin käyttäjän määrittämä raja, järjestelmä antaa päätöksen `limit_export`.

Jos nettomyyntihinta on rajan yläpuolella, järjestelmä antaa päätöksen `allow_export`.

Rajoitustilanteessa sallittu myyntiteho lasketaan:

```text
vientiraja watteina = maksimimyyntiteho * sallittu myyntiprosentti / 100
```

## Tekninen arkkitehtuuri

Komponentit:

- Fronius-lukija: hakee tuotanto- ja tehotiedot paikallisesta Solar API -rajapinnasta.
- Hintamoduuli: hakee tai simuloi sähkön hintatiedon.
- Optimointimoduuli: laskee nettomyyntihinnan ja tekee päätöksen.
- Tallennus: SQLite-tietokanta mittauksille, päätöksille ja asetuksille.
- Selainapplikaatio: asetusten muuttaminen ja nykyisen päätöksen tarkastelu.
- API-palvelin: FastAPI-palvelu paikallisessa verkossa.

## Toteutusvaiheet

1. Ohjelmistopohja ja simuloitu päätöksenteko.
2. Fronius Solar API -lukemisen testaus oikeassa lähiverkossa.
3. Selainkäyttöliittymä marginaalille ja rajoitusprosentille.
4. Oikean hintarajapinnan lisääminen.
5. Päätösten ja mittausten raportointi.
6. Laitemallikohtainen selvitys todellisesta tehorajoituksesta.
7. Hallittu invertteriohjaus vain, jos se voidaan toteuttaa turvallisesti.

## Riskit

- Hintarajapinnan saatavuus voi vaihdella.
- Invertterin ohjausrajapinta voi olla mallikohtainen.
- Liian aggressiivinen rajoitus voi heikentää tuotannon hyödyntämistä.
- Kotiverkon tai palvelinkoneen katkos voi estää ohjauksen.

Riskien hallinta:

- oletusasetuksena simulointi
- ei suoraa internet-altistusta
- asetukset paikalliseen tietokantaan
- erillinen testaus ennen fyysistä ohjausta

## Tuotokset

- Python/FastAPI-pohjainen prototyyppi
- selainkäyttöliittymä asetuksille
- SQLite-tallennus
- palvelinkoneen käyttöönotto-ohje
- GitHub-julkaisun tarkistuslista
- jatkokehityssuunnitelma todelliselle invertteriohjaukselle
