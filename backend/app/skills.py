from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Skill:
    id: str
    branch: str          # analytics / creative / traffic / panda
    name: str
    description: str
    level_required: int  # минимальный уровень пользователя для разблокировки
    order: int           # порядок отображения внутри ветки


SKILLS: Dict[str, Skill] = {
    # Analytics
    "analytics_ctr_insight": Skill(
        id="analytics_ctr_insight",
        branch="analytics",
        name="CTR Insight",
        description="Немного лучше понимаешь кликабельность объявлений.",
        level_required=1,
        order=1,
    ),
    "analytics_cr_sensei": Skill(
        id="analytics_cr_sensei",
        branch="analytics",
        name="CR Sensei",
        description="Начинаешь замечать слабые места в воронке.",
        level_required=2,
        order=2,
    ),
    "analytics_roi_master": Skill(
        id="analytics_roi_master",
        branch="analytics",
        name="ROI Master",
        description="Быстрее находишь связки с плюсовым ROI.",
        level_required=3,
        order=3,
    ),

    # Creative
    "creative_hook_master": Skill(
        id="creative_hook_master",
        branch="creative",
        name="Hook Master",
        description="Понимаешь, как цеплять внимание в креативах.",
        level_required=1,
        order=1,
    ),
    "creative_storyteller": Skill(
        id="creative_storyteller",
        branch="creative",
        name="Storyteller",
        description="Умеешь строить истории вокруг продукта.",
        level_required=3,
        order=2,
    ),

    # Traffic Sources
    "traffic_meta_novice": Skill(
        id="traffic_meta_novice",
        branch="traffic",
        name="Meta Novice",
        description="Понимаешь базу рекламы в Meta.",
        level_required=2,
        order=1,
    ),
    "traffic_tiktok_apprentice": Skill(
        id="traffic_tiktok_apprentice",
        branch="traffic",
        name="TikTok Apprentice",
        description="Разбираешься в коротких крео под TikTok.",
        level_required=3,
        order=2,
    ),

    # Panda Evolution (просто ветка под эволюцию)
    "panda_evo_stage1": Skill(
        id="panda_evo_stage1",
        branch="panda",
        name="Evolution I",
        description="Панда делает первый шаг к следующей форме.",
        level_required=2,
        order=1,
    ),
    "panda_evo_stage2": Skill(
        id="panda_evo_stage2",
        branch="panda",
        name="Evolution II",
        description="Панда становится ещё сильнее.",
        level_required=4,
        order=2,
    ),
}


def get_skills_for_level(level: int) -> List[Skill]:
    """Возвращает список навыков, доступных пользователю с этим уровнем."""
    return [s for s in SKILLS.values() if level >= s.level_required]
