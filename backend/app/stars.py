from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Product:
    id: str
    name_ru: str
    name_en: str
    stars_price: int
    type: str  # coins / booster / panda / season_pass
    payload: str


PRODUCTS: Dict[str, Product] = {
    "coins_small": Product(
        id="coins_small",
        name_ru="Пак монет S",
        name_en="Coin Pack S",
        stars_price=100,
        type="coins",
        payload="coins:50000",
    ),
    "coins_medium": Product(
        id="coins_medium",
        name_ru="Пак монет M",
        name_en="Coin Pack M",
        stars_price=200,
        type="coins",
        payload="coins:120000",
    ),
    "coins_big": Product(
        id="coins_big",
        name_ru="Пак монет L",
        name_en="Coin Pack L",
        stars_price=500,
        type="coins",
        payload="coins:400000",
    ),
    "mythic_panda": Product(
        id="mythic_panda",
        name_ru="Мифическая Панда",
        name_en="Mythic Panda",
        stars_price=800,
        type="panda",
        payload="panda:mythic",
    ),
    "xp_boost": Product(
        id="xp_boost",
        name_ru="XP бустер x2 (1ч)",
        name_en="XP booster x2 (1h)",
        stars_price=150,
        type="booster",
        payload="booster:xp2h1",
    ),
    "coins_boost": Product(
        id="coins_boost",
        name_ru="Доход x2 (1ч)",
        name_en="Income x2 (1h)",
        stars_price=150,
        type="booster",
        payload="booster:coins2h1",
    ),
    "season_pass": Product(
        id="season_pass",
        name_ru="Season Pass",
        name_en="Season Pass",
        stars_price=600,
        type="season_pass",
        payload="season:pass",
    ),
}


def list_products() -> List[Product]:
    return list(PRODUCTS.values())
