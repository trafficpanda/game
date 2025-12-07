from typing import List
from .models import User

def level_from_xp(xp: int) -> int:
    level = 1
    while True:
        required = 100 * (level + 1) ** 2
        if xp < required:
            return level
        level += 1

def rank_name_from_level(level: int) -> str:
    if level < 3:
        return "Новичок"
    elif level < 5:
        return "Джун-арбитражник"
    elif level < 7:
        return "Мидл-арбитражник"
    elif level < 9:
        return "Сеньор-арбитражник"
    elif level < 11:
        return "Трафик-Самурай"
    else:
        return "Трафик-Гуру"

def rating_score(user: User) -> float:
    return user.xp * 2 + user.coins * 0.001 + user.hourly_income * 10

def sort_users_by_rating(users: List[User]) -> List[User]:
    return sorted(users, key=rating_score, reverse=True)
