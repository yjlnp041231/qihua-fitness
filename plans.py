"""训练计划系统"""

from dataclasses import dataclass, field
from typing import List

@dataclass
class PlanDay:
    day: int
    exercises: List[dict]  # [{name, sets, reps, rest_sec}]
    notes: str = ""

@dataclass
class TrainingPlan:
    id: str
    name: str
    goal: str  # lose_fat / gain_muscle / endurance / flexibility
    weeks: int
    days_per_week: int
    difficulty: str
    description: str
    schedule: List[PlanDay] = field(default_factory=list)

PLANS = {
    "lose_fat_4w": TrainingPlan(
        id="lose_fat_4w", name="4周燃脂计划", goal="lose_fat",
        weeks=4, days_per_week=5, difficulty="intermediate",
        description="每周5天，HIIT+力量结合，高效燃脂",
        schedule=[
            PlanDay(1, [{"name":"开合跳","sets":3,"reps":30,"rest_sec":15},
                        {"name":"深蹲","sets":3,"reps":20,"rest_sec":30},
                        {"name":"波比跳","sets":3,"reps":10,"rest_sec":30},
                        {"name":"高抬腿","sets":3,"reps":30,"rest_sec":15}], "HIIT日"),
            PlanDay(2, [{"name":"俯卧撑","sets":4,"reps":15,"rest_sec":45},
                        {"name":"引体向上","sets":3,"reps":8,"rest_sec":60},
                        {"name":"卷腹","sets":3,"reps":25,"rest_sec":30}], "上肢力量"),
            PlanDay(3, [{"name":"开合跳","sets":4,"reps":40,"rest_sec":15},
                        {"name":"高抬腿","sets":4,"reps":30,"rest_sec":15},
                        {"name":"波比跳","sets":3,"reps":12,"rest_sec":30}], "有氧日"),
            PlanDay(4, [{"name":"深蹲","sets":4,"reps":20,"rest_sec":45},
                        {"name":"弓步蹲","sets":3,"reps":15,"rest_sec":30},
                        {"name":"平板支撑","sets":3,"reps":0,"rest_sec":30}], "下肢+核心"),
            PlanDay(5, [{"name":"波比跳","sets":5,"reps":10,"rest_sec":30},
                        {"name":"深蹲","sets":3,"reps":20,"rest_sec":30},
                        {"name":"俯卧撑","sets":3,"reps":15,"rest_sec":30},
                        {"name":"卷腹","sets":3,"reps":25,"rest_sec":30}], "全身冲刺"),
        ]),
    "gain_muscle_4w": TrainingPlan(
        id="gain_muscle_4w", name="4周增肌计划", goal="gain_muscle",
        weeks=4, days_per_week=4, difficulty="intermediate",
        description="每周4天，分化训练，科学增肌",
        schedule=[
            PlanDay(1, [{"name":"俯卧撑","sets":5,"reps":12,"rest_sec":60},
                        {"name":"引体向上","sets":4,"reps":8,"rest_sec":90},
                        {"name":"卷腹","sets":4,"reps":20,"rest_sec":30}], "胸+背"),
            PlanDay(2, [{"name":"深蹲","sets":5,"reps":15,"rest_sec":90},
                        {"name":"弓步蹲","sets":4,"reps":12,"rest_sec":60},
                        {"name":"平板支撑","sets":3,"reps":0,"rest_sec":30}], "腿+核心"),
            PlanDay(3, [{"name":"俯卧撑","sets":4,"reps":15,"rest_sec":45},
                        {"name":"引体向上","sets":3,"reps":10,"rest_sec":60},
                        {"name":"卷腹","sets":3,"reps":25,"rest_sec":30}], "推+拉"),
            PlanDay(4, [{"name":"深蹲","sets":4,"reps":20,"rest_sec":60},
                        {"name":"弓步蹲","sets":3,"reps":15,"rest_sec":45},
                        {"name":"平板支撑","sets":4,"reps":0,"rest_sec":30},
                        {"name":"波比跳","sets":3,"reps":8,"rest_sec":30}], "腿+HIIT"),
        ]),
    "beginner_4w": TrainingPlan(
        id="beginner_4w", name="4周入门计划", goal="endurance",
        weeks=4, days_per_week=3, difficulty="beginner",
        description="每周3天，循序渐进，建立运动习惯",
        schedule=[
            PlanDay(1, [{"name":"开合跳","sets":2,"reps":20,"rest_sec":30},
                        {"name":"深蹲","sets":2,"reps":10,"rest_sec":45},
                        {"name":"平板支撑","sets":2,"reps":0,"rest_sec":30}], "基础有氧"),
            PlanDay(2, [{"name":"俯卧撑","sets":2,"reps":8,"rest_sec":60},
                        {"name":"卷腹","sets":2,"reps":15,"rest_sec":30},
                        {"name":"弓步蹲","sets":2,"reps":10,"rest_sec":45}], "基础力量"),
            PlanDay(3, [{"name":"开合跳","sets":3,"reps":25,"rest_sec":20},
                        {"name":"高抬腿","sets":2,"reps":20,"rest_sec":30},
                        {"name":"深蹲","sets":2,"reps":15,"rest_sec":45},
                        {"name":"平板支撑","sets":2,"reps":0,"rest_sec":30}], "综合训练"),
        ]),
    "flexibility_4w": TrainingPlan(
        id="flexibility_4w", name="4周柔韧计划", goal="flexibility",
        weeks=4, days_per_week=3, difficulty="beginner",
        description="每周3天，提升柔韧性和关节活动度",
        schedule=[
            PlanDay(1, [{"name":"平板支撑","sets":3,"reps":0,"rest_sec":30},
                        {"name":"卷腹","sets":3,"reps":15,"rest_sec":30},
                        {"name":"弓步蹲","sets":2,"reps":10,"rest_sec":30}], "核心稳定"),
            PlanDay(2, [{"name":"深蹲","sets":3,"reps":15,"rest_sec":45},
                        {"name":"弓步蹲","sets":3,"reps":12,"rest_sec":30},
                        {"name":"开合跳","sets":2,"reps":20,"rest_sec":20}], "下肢灵活"),
            PlanDay(3, [{"name":"平板支撑","sets":3,"reps":0,"rest_sec":30},
                        {"name":"俯卧撑","sets":2,"reps":10,"rest_sec":45},
                        {"name":"卷腹","sets":3,"reps":20,"rest_sec":30},
                        {"name":"开合跳","sets":2,"reps":20,"rest_sec":20}], "全身整合"),
        ]),
}

def get_plan_list():
    return [{"id": p.id, "name": p.name, "goal": p.goal, "weeks": p.weeks,
             "days": p.days_per_week, "difficulty": p.difficulty,
             "desc": p.description} for p in PLANS.values()]

def get_plan(plan_id):
    return PLANS.get(plan_id)

GOAL_LABELS = {"lose_fat": "🔥 燃脂减重", "gain_muscle": "💪 增肌塑形",
               "endurance": "🏃 提升体能", "flexibility": "🧘 柔韧灵活"}
