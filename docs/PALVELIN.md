# Palvelinkone AurinkoOptimo-projektiin

## Suositus

Yhden omakotitalon Fronius-aurinkopaneelijärjestelmälle järkevin palvelin on pieni x86-minikone:

- Intel N100 tai N150
- 8-16 GB RAM
- 128-256 GB SSD
- Gigabit Ethernet
- Debian 12 tai Ubuntu Server LTS
- Pieni UPS, jos ohjauksesta tulee myöhemmin tuotantokriittinen

Tällä koneella voi ajaa AurinkoOptimo-palvelun, SQLite- tai PostgreSQL-tietokannan, mahdollisen Grafanan ja myöhemmin myös Home Assistantin. Kone kannattaa kytkeä Ethernetillä samaan lähiverkkoon invertterin kanssa.

## Miksi ei ensisijaisesti Raspberry Pi?

Raspberry Pi 5 toimii teknisesti hyvin, mutta kokonaishinta nousee helposti, kun mukaan lasketaan virtalähde, kotelo, jäähdytys ja SSD-ratkaisu. Minikoneessa SSD, kotelo, virtalähde ja jäähdytys ovat yleensä valmiina, ja Linux-palvelinkäyttö on suoraviivaista.

Raspberry Pi on silti hyvä vaihtoehto, jos:

- halutaan pieni sähkönkulutus ja laaja harrastajayhteisö
- projektissa tarvitaan GPIO-liitäntöjä
- laite on jo valmiiksi saatavilla

## Mitä ei kannata ostaa

- Vanhaa läppäriä 24/7-palvelimeksi, jos akku tai jäähdytys on huonossa kunnossa.
- Pelikonetta tai isoa pöytäkonetta, koska sähkönkulutus ja melu ovat turhia tähän käyttöön.
- Pelkkään microSD-korttiin nojaavaa ratkaisua pitkäaikaiseen tietokantakirjoitukseen.

## Verkkovaatimukset

- Fronius-invertterille kiinteä IP-osoite tai DHCP-varaus.
- Palvelimelle kiinteä IP-osoite tai DHCP-varaus.
- Palvelin ja invertteri samaan lähiverkkoon.
- Etäkäyttö mieluiten VPN:n kautta, ei suoraa porttiavausta internetiin.

## Ohjelmistopino

Ensimmäiseen prototyyppiin riittää:

- Python 3.11+
- FastAPI
- SQLite
- systemd-ajastus tai cron

Laajennusvaiheessa:

- PostgreSQL tai TimescaleDB pidemmälle mittausdatalle
- Grafana visualisointiin
- Home Assistant, jos halutaan yhdistää muuta taloautomaatiota
