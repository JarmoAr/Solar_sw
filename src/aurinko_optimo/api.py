import asyncio
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from aurinko_optimo.models import ControlSettings
from aurinko_optimo.services import (
    build_fronius_client,
    build_optimizer,
    build_price_provider,
    build_storage,
    default_control_settings,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.storage = build_storage()
    app.state.fronius = build_fronius_client()
    app.state.price_provider = build_price_provider()
    yield


app = FastAPI(title="AurinkoOptimo", version="0.1.0", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
async def dashboard() -> str:
    return """
    <!doctype html>
    <html lang="fi">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>AurinkoOptimo</title>
        <style>
          :root {
            color-scheme: light;
            font-family: Arial, Helvetica, sans-serif;
            color: #17202a;
            background: #f4f7f8;
          }
          body { margin: 0; }
          main {
            max-width: 920px;
            margin: 0 auto;
            padding: 32px 18px 56px;
          }
          header { margin-bottom: 22px; }
          h1 { font-size: 2rem; margin: 0 0 6px; }
          p { line-height: 1.5; }
          .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 16px;
          }
          section {
            background: #fff;
            border: 1px solid #d7e0e5;
            border-radius: 8px;
            padding: 18px;
          }
          label {
            display: block;
            font-weight: 700;
            margin-top: 14px;
          }
          input {
            box-sizing: border-box;
            width: 100%;
            margin-top: 6px;
            padding: 10px 12px;
            border: 1px solid #b7c4cc;
            border-radius: 6px;
            font-size: 1rem;
          }
          button {
            margin-top: 18px;
            padding: 11px 16px;
            border: 0;
            border-radius: 6px;
            color: white;
            background: #176b87;
            font-weight: 700;
            cursor: pointer;
          }
          button.secondary { background: #53656f; margin-left: 8px; }
          pre {
            overflow: auto;
            background: #17202a;
            color: #e8f4f8;
            border-radius: 8px;
            padding: 14px;
            min-height: 120px;
          }
          .status { min-height: 24px; font-weight: 700; }
          .hint { color: #53656f; font-size: 0.94rem; margin-top: 6px; }
        </style>
      </head>
      <body>
        <main>
          <header>
            <h1>AurinkoOptimo</h1>
            <p>Säädä millä nettomyyntihinnalla tuotantoa rajoitetaan ja kuinka paljon verkkoon saa vielä mennä rajoitustilanteessa.</p>
          </header>

          <div class="grid">
            <section>
              <h2>Asetukset</h2>
              <form id="settings-form">
                <label for="sales_margin_cents_kwh">Sähköyhtiön myyntimarginaali, snt/kWh</label>
                <input id="sales_margin_cents_kwh" name="sales_margin_cents_kwh" type="number" min="0" step="0.001">
                <div class="hint">Esim. 0,35 snt/kWh syötetään arvona 0.35.</div>

                <label for="limit_when_net_price_below_cents_kwh">Rajoita, kun nettomyyntihinta on enintään, snt/kWh</label>
                <input id="limit_when_net_price_below_cents_kwh" name="limit_when_net_price_below_cents_kwh" type="number" step="0.001">

                <label for="limited_export_percent">Sallittu myynti rajoitustilanteessa, %</label>
                <input id="limited_export_percent" name="limited_export_percent" type="number" min="0" max="100" step="0.1">
                <div class="hint">0 % estää myynnin, 5 % sallii pienen ulosmyynnin.</div>

                <label for="max_export_w">Järjestelmän maksimimyyntiteho, W</label>
                <input id="max_export_w" name="max_export_w" type="number" min="0" step="1">

                <button type="submit">Tallenna asetukset</button>
                <button class="secondary" id="refresh-decision" type="button">Päivitä päätös</button>
              </form>
              <p class="status" id="status"></p>
            </section>

            <section>
              <h2>Nykyinen päätös</h2>
              <pre id="decision">Ladataan...</pre>
            </section>
          </div>
        </main>

        <script>
          const form = document.querySelector("#settings-form");
          const statusEl = document.querySelector("#status");
          const decisionEl = document.querySelector("#decision");

          function formDataToJson() {
            const data = new FormData(form);
            return {
              sales_margin_cents_kwh: Number(data.get("sales_margin_cents_kwh")),
              limit_when_net_price_below_cents_kwh: Number(data.get("limit_when_net_price_below_cents_kwh")),
              limited_export_percent: Number(data.get("limited_export_percent")),
              max_export_w: Number(data.get("max_export_w"))
            };
          }

          function fillForm(settings) {
            for (const [key, value] of Object.entries(settings)) {
              const input = form.elements[key];
              if (input) input.value = value;
            }
          }

          async function loadSettings() {
            const response = await fetch("/api/settings");
            fillForm(await response.json());
          }

          async function loadDecision() {
            decisionEl.textContent = "Ladataan...";
            const response = await fetch("/api/decision");
            const data = await response.json();
            decisionEl.textContent = JSON.stringify(data, null, 2);
          }

          form.addEventListener("submit", async (event) => {
            event.preventDefault();
            statusEl.textContent = "Tallennetaan...";
            const response = await fetch("/api/settings", {
              method: "PUT",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(formDataToJson())
            });
            if (!response.ok) {
              statusEl.textContent = "Tallennus epäonnistui.";
              return;
            }
            fillForm(await response.json());
            statusEl.textContent = "Asetukset tallennettu.";
            await loadDecision();
          });

          document.querySelector("#refresh-decision").addEventListener("click", loadDecision);

          loadSettings().then(loadDecision).catch(() => {
            statusEl.textContent = "Asetusten lataus epäonnistui.";
          });
        </script>
      </body>
    </html>
    """


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


def _current_control_settings() -> ControlSettings:
    return app.state.storage.get_control_settings(default_control_settings())


def _current_optimizer():
    return build_optimizer(_current_control_settings())


@app.post("/api/collect")
async def collect() -> dict:
    power, price = await asyncio.gather(
        app.state.fronius.get_power_flow(),
        app.state.price_provider.current_price(),
    )
    decision = _current_optimizer().decide(power=power, price=price)
    app.state.storage.save_measurement(power)
    app.state.storage.save_decision(decision)
    return {
        "measurement": power.model_dump(mode="json"),
        "decision": decision.model_dump(mode="json"),
    }


@app.get("/api/latest")
async def latest() -> dict:
    return {
        "measurement": app.state.storage.latest_measurement(),
        "decision": app.state.storage.latest_decision(),
        "settings": _current_control_settings().model_dump(mode="json"),
    }


@app.get("/api/settings")
async def get_settings() -> dict:
    return _current_control_settings().model_dump(mode="json")


@app.put("/api/settings")
async def update_settings(control_settings: ControlSettings) -> dict:
    app.state.storage.save_control_settings(control_settings)
    return control_settings.model_dump(mode="json")


@app.get("/api/decision")
async def current_decision() -> dict:
    try:
        power = await app.state.fronius.get_power_flow()
    except httpx.HTTPError:
        power = None

    try:
        price = await app.state.price_provider.current_price()
    except RuntimeError:
        price = None

    decision = _current_optimizer().decide(power=power, price=price)
    app.state.storage.save_decision(decision)
    return decision.model_dump(mode="json")


def main() -> None:
    import uvicorn

    uvicorn.run("aurinko_optimo.api:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
