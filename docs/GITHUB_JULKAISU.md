# GitHub-julkaisun tarkistuslista

Tavoite: GitHubiin menee vain koodi ja yleinen tekninen dokumentaatio. Henkilötiedot, hankedokumentit, sopimukset, budjetit, osoitteet, tunnukset ja paikalliset asetukset pidetään poissa repositoriosta.

## Ei GitHubiin

- `.env` tai muut paikalliset asetustiedostot
- tietokannat ja mittausdata
- lokit
- Word-, PowerPoint-, Excel- ja PDF-dokumentit
- henkilönimet, osoitteet, puhelinnumerot ja sähköpostit
- hankebudjetit, rahoitussuunnitelmat ja sopimustiedot
- API-avaimet, tokenit, salasanat ja yksityisavaimet
- kodin tai invertterin todelliset IP-osoitteet

## Ennen ensimmäistä pushia

Aja tarkistus:

```powershell
cd Solar_sw
git status --short
```

Jos listalla näkyy tiedostoja kuten `.docx`, `.pptx`, `.xlsx`, `.pdf`, `.env`, `.db` tai `.log`, niitä ei pidä lisätä committiin.

Tarkista myös mahdolliset salaisuudet:

```powershell
rg -n "(password|secret|token|api[_-]?key|bearer|BEGIN .*KEY|192\.168|10\.)" -S .
```

Jos GitHub-repo tehdään julkiseksi, julkaise mieluummin liian vähän kuin liian paljon.
