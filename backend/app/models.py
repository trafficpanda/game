from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    user_id: int
    username: Optional[str]
    coins: int
    xp: int
    hourly_income: int
    level: int
    rank_name: str
    referred_by: Optional[int]
