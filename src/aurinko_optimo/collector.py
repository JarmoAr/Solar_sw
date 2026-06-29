import asyncio

from aurinko_optimo.services import (
    build_fronius_client,
    build_optimizer,
    build_price_provider,
    build_storage,
    default_control_settings,
)


async def collect_once() -> None:
    storage = build_storage()
    fronius = build_fronius_client()
    price_provider = build_price_provider()
    control_settings = storage.get_control_settings(default_control_settings())
    optimizer = build_optimizer(control_settings)

    power = await fronius.get_power_flow()
    price = await price_provider.current_price()
    decision = optimizer.decide(power=power, price=price)

    storage.save_measurement(power)
    storage.save_decision(decision)

    print(decision.model_dump_json(indent=2))


def main() -> None:
    asyncio.run(collect_once())


if __name__ == "__main__":
    main()
