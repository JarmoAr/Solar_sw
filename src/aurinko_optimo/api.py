import asyncio
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from aurinko_optimo.services import (
    build_fronius_client,
    build_optimizer,
    build_price_provider,
    build_storage,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.storage = build_storage()
    app.state.fronius = build_fronius_client()
    app.state.price_provider = build_price_provider()
    app.state.optimizer = build_optimizer()
    yield


app = FastAPI(title="AurinkoOptimo", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/collect")
async def collect() -> dict:
    power, price = await asyncio.gather(
        app.state.fronius.get_power_flow(),
        app.state.price_provider.current_price(),
    )
    decision = app.state.optimizer.decide(power=power, price=price)
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
    }


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

    decision = app.state.optimizer.decide(power=power, price=price)
    app.state.storage.save_decision(decision)
    return decision.model_dump(mode="json")


def main() -> None:
    import uvicorn

    uvicorn.run("aurinko_optimo.api:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
