from dataclasses import dataclass
from typing import Dict

from .db import (
    get_user,
    get_completed_steps,
    get_user_pandas,
    get_referrals_count,
    get_user_achievements,
    add_user_achievement,
)
from .rating import level_from_xp


@dataclass
class Achievement:
    id: str
    name: str
    description: str
    condition_type: str  # steps_completed / level / pandas_owned / referrals
    threshold: int


ACHIEVEMENTS: Dict[str, Achievement] = {
    "first_step": Achievement(
        id="first_step",
        name="Первый шаг",
        description="Пройди первый урок.",
        condition_type="steps_completed",
        threshold=1,
    ),
    "ten_steps": Achievement(
        id="ten_steps",
        name="Десять уроков",
        description="Пройди 10 шагов обучения.",
        condition_type="steps_completed",
        threshold=10,
    ),
    "all_steps": Achievement(
        id="all_steps",
        name="Гуру обучения",
        description="Заверши всю программу и экзамен.",
        condition_type="steps_completed",
        threshold=20,
    ),
    "level_5": Achievement(
        id="level_5",
        name="Уровень 5",
        description="Достигни 5 уровня панды.",
        condition_type="level",
        threshold=5,
    ),
    "level_10": Achievement(
        id="level_10",
        name="Уровень 10",
        description="Достигни 10 уровня панды.",
        condition_type="level",
        threshold=10,
    ),
    "first_panda": Achievement(
        id="first_panda",
        name="Первая панда",
        description="Купи первую панду в магазине.",
        condition_type="pandas_owned",
        threshold=1,
    ),
    "panda_collector": Achievement(
        id="panda_collector",
        name="Коллекционер панд",
        description="Собери 3 панд или больше.",
        condition_type="pandas_owned",
        threshold=3,
    ),
    "first_referral": Achievement(
        id="first_referral",
        name="Первый друг",
        description="Приведи первого друга в игру.",
        condition_type="referrals",
        threshold=1,
    ),
    "referral_5": Achievement(
        id="referral_5",
        name="Мини-команда",
        description="Приведи 5 друзей.",
        condition_type="referrals",
        threshold=5,
    ),
}


async def ensure_user_achievements_up_to_date(user_id: int):
    user = await get_user(user_id)
    completed_steps = await get_completed_steps(user_id)
    pandas = await get_user_pandas(user_id)
    referrals = await get_referrals_count(user_id)
    user_level = level_from_xp(user.xp)

    already = set(await get_user_achievements(user_id))

    for ach in ACHIEVEMENTS.values():
        if ach.id in already:
            continue

        ok = False
        if ach.condition_type == "steps_completed":
            ok = len(completed_steps) >= ach.threshold
        elif ach.condition_type == "level":
            ok = user_level >= ach.threshold
        elif ach.condition_type == "pandas_owned":
            ok = len(pandas) >= ach.threshold
        elif ach.condition_type == "referrals":
            ok = referrals >= ach.threshold

        if ok:
            await add_user_achievement(user_id, ach.id)


async def get_user_achievements_full(user_id: int):
    await ensure_user_achievements_up_to_date(user_id)
    earned_ids = set(await get_user_achievements(user_id))

    result = []
    for ach in ACHIEVEMENTS.values():
        result.append(
            {
                "id": ach.id,
                "name": ach.name,
                "description": ach.description,
                "earned": ach.id in earned_ids,
            }
        )
    return result
