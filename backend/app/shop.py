from dataclasses import dataclass
from typing import Dict, List

from .models import User
from .db import user_has_panda, add_panda_purchase, update_user
from .rating import level_from_xp, rank_name_from_level


@dataclass
class PandaItem:
    id: str
    name: str
    price: int
    income_bonus: int
    description: str
    image_url: str


PANDAS: Dict[str, PandaItem] = {
    "traffic": PandaItem(
        id="traffic",
        name="Traffic Panda",
        price=100_000,
        income_bonus=50,
        description="Базовая панда-траффикер. С неё начинается путь.",
        image_url="/img/pandas/traffic_panda.png",
    ),
    "crypto": PandaItem(
        id="crypto",
        name="Crypto Panda",
        price=120_000,
        income_bonus=70,
        description="Шарит в крипте и аирдропах, бустит доход.",
        image_url="/img/pandas/crypto_panda.png",
    ),
    "naughty": PandaItem(
        id="naughty",
        name="Naughty Panda",
        price=150_000,
        income_bonus=90,
        description="Любит рисковать и тестировать смелые связки.",
        image_url="/img/pandas/naughty_panda.png",
    ),
    "mother": PandaItem(
        id="mother",
        name="Mother Panda",
        price=180_000,
        income_bonus=120,
        description="Заботится обо всём стаде, даёт максимальный доход.",
        image_url="/img/pandas/mother_panda.png",
    ),
}


def list_pandas() -> List[PandaItem]:
    return list(PANDAS.values())


async def buy_panda(user: User, panda_id: str):
    if panda_id not in PANDAS:
        raise ValueError("Panda not found")

    panda = PANDAS[panda_id]

    if await user_has_panda(user.user_id, panda_id):
        raise ValueError("Panda already purchased")

    if user.coins < panda.price:
        raise ValueError("Not enough coins")

    user.coins -= panda.price
    user.hourly_income += panda.income_bonus
    user.level = level_from_xp(user.xp)
    user.rank_name = rank_name_from_level(user.level)

    await update_user(user)
    await add_panda_purchase(user.user_id, panda_id)
