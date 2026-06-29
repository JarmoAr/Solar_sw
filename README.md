# AurinkoOptimo

AurinkoOptimo is a small prototype for a single detached house solar PV system with a Fronius inverter. The first version reads inverter data, stores measurements locally, combines them with electricity price data, and produces a control decision.

By default the project is safe: it only simulates control decisions. It does not write settings to the inverter.

## Recommended server

For one Fronius inverter and one house, buy a small x86 mini PC rather than an expensive Raspberry Pi kit.

Recommended baseline:

- Intel N100 / N150 mini PC
- 8-16 GB RAM
- 128-256 GB SSD
- Gigabit Ethernet
- Debian 12 or Ubuntu Server LTS
- Optional small UPS

This is enough for the API, SQLite/PostgreSQL, Home Assistant or Grafana later, and 24/7 logging. A Raspberry Pi 5 also works, but once power supply, case and SSD are included, a mini PC is often better value and has stronger storage.

## Fronius setup

Enable the Fronius local Solar API in the inverter web UI and give the inverter a static IP address or DHCP reservation.

Create `.env`:

```env
FRONIUS_BASE_URL=http://192.0.2.50
DATABASE_PATH=./data/aurinko.db
CONTROL_MODE=simulate
NEGATIVE_PRICE_LIMIT_EUR_MWH=0
```

## Run locally

The main program is the API server:

- `aurinko-api` starts the HTTP API.
- `aurinko-collect` runs one measurement and decision cycle.

```powershell
cd Solar_sw
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
aurinko-api
```

Open:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/api/latest`
- `http://127.0.0.1:8000/api/decision`

To run a single collection manually:

```powershell
aurinko-collect
```

If no real Fronius inverter is available at `FRONIUS_BASE_URL`, `/api/decision` can still return a safe decision with missing inverter data. `/api/collect` expects the inverter API to be reachable.

## Project shape

- `src/aurinko_optimo/fronius.py` reads local Fronius Solar API data.
- `src/aurinko_optimo/prices.py` provides current price data. The current version supports a local CSV file and a fallback simulation price.
- `src/aurinko_optimo/optimizer.py` decides whether export should be allowed or limited.
- `src/aurinko_optimo/storage.py` stores measurements and decisions in SQLite.
- `src/aurinko_optimo/api.py` exposes a small HTTP API.

## Next steps

1. Confirm the exact Fronius inverter model and enabled interfaces.
2. Replace CSV/simulated price data with the selected Finnish/Nordic price API.
3. Add a dashboard.
4. Add real inverter control only after testing on the specific device and confirming warranty/grid-code implications.
