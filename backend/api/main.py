from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import BOT_USERNAME
from app.db import (
    init_db,
    get_user,
    get_all_users,
    get_completed_steps,
    get_user_pandas,
    get_referrals_count,
    update_user,
)
from app.course import COURSE_STEPS, get_next_step_for_user
from app.rating import sort_users_by_rating, rating_score, level_from_xp, rank_name_from_level
from app.shop import list_pandas, buy_panda, PANDAS
from app.achievements import get_user_achievements_full, ensure_user_achievements_up_to_date
from app.skills import get_skills_for_level
from app.storyline import get_unlocked_chapters
from app.stars import list_products
from pydantic import BaseModel


app = FastAPI(title="Traffic Panda API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # на проде можно ограничить до trafficpanda.net
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    await init_db()
    print("✅ API started")


# ===== Профиль =====

@app.get("/profile/{user_id}")
async def get_profile(user_id: int) -> Dict[str, Any]:
    user = await get_user(user_id)
    owned = await get_user_pandas(user.user_id)

    main_panda_id = None
    if owned:
        main_panda_id = max(
            owned,
            key=lambda pid: PANDAS.get(pid).price if pid in PANDAS else 0
        )

    if main_panda_id and main_panda_id in PANDAS:
        avatar_url = PANDAS[main_panda_id].image_url
    else:
        avatar_url = "/img/pandas/base_panda.png"

    achievements = await get_user_achievements_full(user.user_id)
    earned_count = sum(1 for a in achievements if a["earned"])

    return {
        "user_id": user.user_id,
        "username": user.username,
        "coins": user.coins,
        "xp": user.xp,
        "hourly_income": user.hourly_income,
        "level": user.level,
        "rank_name": user.rank_name,
        "rating_score": int(rating_score(user)),
        "avatar_url": avatar_url,
        "owned_pandas": owned,
        "achievements_count": earned_count,
    }


# ===== Рейтинг =====

@app.get("/rating")
async def get_rating(limit: int = 10) -> Dict[str, Any]:
    users = await get_all_users()
    top = sort_users_by_rating(users)[:limit]
    return {
        "items": [
            {
                "user_id": u.user_id,
                "username": u.username,
                "level": u.level,
                "rank_name": u.rank_name,
                "rating_score": int(rating_score(u)),
            }
            for u in top
        ]
    }


# ===== Прогресс обучения =====

@app.get("/course-progress/{user_id}")
async def get_course_progress(user_id: int) -> Dict[str, Any]:
    user = await get_user(user_id)
    completed = await get_completed_steps(user.user_id)
    next_step = await get_next_step_for_user(user.user_id)

    next_step_payload = None
    if next_step:
        next_step_payload = {
            "id": next_step.id,
            "module_id": next_step.module_id,
            "title": next_step.title,
            "content": next_step.content,
            "question": next_step.question,
            "options": next_step.options,
        }

    return {
        "completed_step_ids": completed,
        "next_step": next_step_payload,
        "total_steps": len(COURSE_STEPS),
    }


class CourseAnswerRequest(BaseModel):
    user_id: int
    step_id: str
    answer_index: int


@app.post("/course/answer")
async def answer_course_step(req: CourseAnswerRequest) -> Dict[str, Any]:
    user = await get_user(req.user_id)
    step = COURSE_STEPS.get(req.step_id)
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")

    correct = req.answer_index == step.correct_index

    if correct:
        user.xp += step.reward_xp
        user.coins += step.reward_coins
        user.level = level_from_xp(user.xp)
        user.rank_name = rank_name_from_level(user.level)
        await update_user(user)
        await ensure_user_achievements_up_to_date(user.user_id)
        message = f"Верно! Награда: +{step.reward_xp} XP, +{step.reward_coins} монет 🪙"
    else:
        message = "Неправильный ответ. Попробуй ещё раз 👀"

    profile = await get_profile(user.user_id)
    course_progress = await get_course_progress(user.user_id)

    return {
        "correct": correct,
        "message": message,
        "profile": profile,
        "course_progress": course_progress,
    }


# ===== Магазин панд =====

@app.get("/shop/pandas/{user_id}")
async def shop_pandas(user_id: int) -> Dict[str, Any]:
    user = await get_user(user_id)
    owned = set(await get_user_pandas(user.user_id))
    pandas = list_pandas()

    items = []
    for p in pandas:
        items.append(
            {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "income_bonus": p.income_bonus,
                "description": p.description,
                "image_url": p.image_url,
                "owned": p.id in owned,
                "can_afford": (user.coins >= p.price) and (p.id not in owned),
            }
        )

    return {"items": items, "coins": user.coins, "hourly_income": user.hourly_income}


class BuyPandaRequest(BaseModel):
    user_id: int
    panda_id: str


@app.post("/shop/buy")
async def shop_buy(req: BuyPandaRequest) -> Dict[str, Any]:
    user = await get_user(req.user_id)

    if req.panda_id not in PANDAS:
        raise HTTPException(status_code=404, detail="Panda not found")

    try:
        await buy_panda(user, req.panda_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    profile = await get_profile(user.user_id)
    return {
        "status": "ok",
        "user": profile,
    }


# ===== Задания (пока статические) =====

@app.get("/tasks/{user_id}")
async def get_tasks(user_id: int) -> Dict[str, Any]:
    tasks = [
        {
            "id": "day1_learn",
            "title": "Завершить День 1 обучения",
            "description": "Пройди первые уроки и ответь на вопросы.",
            "reward_xp": 100,
            "reward_coins": 15_000,
            "type": "learn",
            "is_completed": False,
        },
        {
            "id": "invite_friend",
            "title": "Пригласить друга",
            "description": "Поделись реферальной ссылкой и приведи друга.",
            "reward_xp": 100,
            "reward_coins": 25_000,
            "type": "social",
            "is_completed": False,
        },
        {
            "id": "exam_pass",
            "title": "Пройти экзамен",
            "description": "Ответь на все экзаменационные вопросы.",
            "reward_xp": 300,
            "reward_coins": 50_000,
            "type": "exam",
            "is_completed": False,
        },
    ]
    return {"items": tasks}


# ===== Ачивки =====

@app.get("/achievements/{user_id}")
async def get_achievements(user_id: int) -> Dict[str, Any]:
    items = await get_user_achievements_full(user_id)
    return {"items": items}


# ===== Друзья =====

@app.get("/friends/{user_id}")
async def get_friends(user_id: int) -> Dict[str, Any]:
    referrals = await get_referrals_count(user_id)
    link = None
    if BOT_USERNAME:
        link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    return {
        "referrals_count": referrals,
        "referral_link": link,
    }


# ===== Skills =====

@app.get("/skills/{user_id}")
async def get_skills(user_id: int) -> Dict[str, Any]:
    user = await get_user(user_id)
    skills = get_skills_for_level(user.level)
    return {
        "items": [
            {
                "id": s.id,
                "branch": s.branch,
                "name": s.name,
                "description": s.description,
                "level_required": s.level_required,
            }
            for s in skills
        ]
    }


# ===== Story =====

@app.get("/story/{user_id}")
async def get_story(user_id: int) -> Dict[str, Any]:
    completed = await get_completed_steps(user_id)
    chapters = get_unlocked_chapters(len(completed))
    return {
        "items": [
            {
                "id": c.id,
                "day": c.day,
                "title": c.title,
                "text": c.text,
            }
            for c in sorted(chapters, key=lambda ch: ch.day)
        ]
    }


# ===== Stars mock-buy (симуляция покупки через Stars) =====

class StarsMockBuyRequest(BaseModel):
    user_id: int
    product_id: str


@app.post("/stars/mock-buy")
async def stars_mock_buy(req: StarsMockBuyRequest):
    user = await get_user(req.user_id)

    # Примитивная симуляция покупки продукта
    if req.product_id == "coins_small":
        user.coins += 50_000
        msg = "Начислено 50 000 монет 🪙"
    elif req.product_id == "coins_medium":
        user.coins += 120_000
        msg = "Начислено 120 000 монет 🪙"
    elif req.product_id == "coins_big":
        user.coins += 400_000
        msg = "Начислено 400 000 монет 🪙"
    elif req.product_id == "xp_boost":
        user.xp += 500
        msg = "Выдан XP бустер (+500 XP) ✨"
    elif req.product_id == "coins_boost":
        user.coins += 200_000
        msg = "Выдан Coin бустер (+200 000 монет) 💰"
    elif req.product_id == "mythic_panda":
        from app.db import add_panda_purchase
        await add_panda_purchase(user.user_id, "mythic")
        msg = "Открыта Мифическая Панда ⭐"
    elif req.product_id == "season_pass":
        msg = "Season Pass активирован! 🎫"
    else:
        raise HTTPException(status_code=400, detail="Неизвестный продукт")

    user.level = level_from_xp(user.xp)
    user.rank_name = rank_name_from_level(user.level)
    await update_user(user)
    await ensure_user_achievements_up_to_date(user.user_id)

    profile = await get_profile(user.user_id)

    return {
        "status": "ok",
        "message": msg,
        "profile": profile,
    }


# ===== Stars (donation products) =====
class StarsMockBuyRequest(BaseModel):
    user_id: int
    product_id: str


@app.get("/stars/products")
async def get_star_products() -> Dict[str, Any]:
    items = list_products()
    return {
        "items": [
            {
                "id": p.id,
                "name_ru": p.name_ru,
                "name_en": p.name_en,
                "stars_price": p.stars_price,
                "type": p.type,
                "payload": p.payload,
            }
            for p in items
        ]
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/stars/mock-buy")
async def stars_mock_buy(req: StarsMockBuyRequest) -> Dict[str, Any]:
    """
    Мок-покупка Stars: никакой реальной оплаты, просто выдаём бонусы.
    Потом этот endpoint можно заменить реальной интеграцией с Telegram Stars.
    """
    user = await get_user(req.user_id)

    # Примитивная логика бонусов
    if req.product_id == "coins_small":
        user.coins += 50_000
        msg = "Начислено 50 000 монет 🪙"
    elif req.product_id == "coins_medium":
        user.coins += 120_000
        msg = "Начислено 120 000 монет 🪙"
    elif req.product_id == "coins_big":
        user.coins += 400_000
        msg = "Начислено 400 000 монет 🪙"
    elif req.product_id == "xp_boost":
        user.xp += 500
        msg = "Выдан XP бустер (симуляция) +500 XP ✨"
    elif req.product_id == "coins_boost":
        user.coins += 200_000
        msg = "Выдан Coin бустер (симуляция) +200 000 монет 💰"
    elif req.product_id == "mythic_panda":
        # можно привязать к отдельной “мифической” панде
        from app.db import add_panda_purchase  # импорт внутри, чтобы не зациклить
        await add_panda_purchase(user.user_id, "mythic")
        msg = "Открыта Мифическая Панда ⭐"
    elif req.product_id == "season_pass":
        msg = "Season Pass (симуляция) активирован!"
    else:
        raise HTTPException(status_code=400, detail="Неизвестный продукт")

    # Обновляем уровень/ранг и сохраняем пользователя
    user.level = level_from_xp(user.xp)
    user.rank_name = rank_name_from_level(user.level)
    await update_user(user)
    await ensure_user_achievements_up_to_date(user.user_id)

    profile = await get_profile(user.user_id)

    return {
        "status": "ok",
        "message": msg,
        "profile": profile,
    }
