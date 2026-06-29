from datetime import datetime

import httpx

from aurinko_optimo.models import PowerFlow


class FroniusClient:
    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def get_power_flow(self) -> PowerFlow:
        url = f"{self.base_url}/solar_api/v1/GetPowerFlowRealtimeData.fcgi"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            payload = response.json()

        site = payload.get("Body", {}).get("Data", {}).get("Site", {})
        return PowerFlow(
            timestamp=datetime.now().astimezone(),
            production_w=_as_float(site.get("P_PV")),
            consumption_w=_as_float(site.get("P_Load")),
            grid_w=_as_float(site.get("P_Grid")),
            battery_w=_as_float(site.get("P_Akku")),
        )


def _as_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
