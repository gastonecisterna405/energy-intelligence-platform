"""Optional electricity price spike model placeholder."""


def describe_optional_price_module() -> str:
    """Explain why price modeling is optional in this project."""
    return (
        "Price-spike modeling is intentionally optional because no verified public price dataset "
        "is bundled with the project. Add a real price CSV to data/raw/ before training this module."
    )
