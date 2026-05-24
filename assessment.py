"""体测评估系统"""

from dataclasses import dataclass

@dataclass
class AssessmentItem:
    name: str
    unit: str
    description: str
    excellent: float  # 优秀线
    good: float       # 良好线
    pass_line: float  # 及格线
    higher_better: bool = True

ASSESSMENTS = {
    "upper_strength": AssessmentItem("上肢力量", "次", "最大俯卧撑次数", 40, 30, 20),
    "core_strength": AssessmentItem("核心力量", "秒", "平板支撑坚持时间", 120, 90, 60),
    "lower_strength": AssessmentItem("下肢力量", "次", "最大深蹲次数", 50, 35, 20),
    "cardio": AssessmentItem("心肺耐力", "次", "1分钟开合跳次数", 60, 45, 30),
    "flexibility": AssessmentItem("柔韧性", "分", "坐位体前屈评分", 20, 15, 10),
}

def evaluate(item: AssessmentItem, value: float) -> tuple:
    """评估成绩，返回 (等级, 评语)"""
    if item.higher_better:
        if value >= item.excellent:
            return "优秀", "体能出众，继续保持！"
        elif value >= item.good:
            return "良好", "基础扎实，还有提升空间。"
        elif value >= item.pass_line:
            return "及格", "达标但需要加强训练。"
        else:
            return "待提升", "建议从入门计划开始。"
    else:
        if value <= item.excellent:
            return "优秀", "体能出众，继续保持！"
        elif value <= item.good:
            return "良好", "基础扎实，还有提升空间。"
        elif value <= item.pass_line:
            return "及格", "达标但需要加强训练。"
        else:
            return "待提升", "建议从入门计划开始。"

def recommend_plan(scores: dict) -> str:
    """根据体测结果推荐计划"""
    weak_areas = []
    for key, (level, _) in scores.items():
        if level in ("待提升", "及格"):
            weak_areas.append(key)

    if not weak_areas:
        return "gain_muscle_4w"

    if "cardio" in weak_areas:
        return "lose_fat_4w"
    if "upper_strength" in weak_areas or "lower_strength" in weak_areas:
        return "gain_muscle_4w"
    if "flexibility" in weak_areas:
        return "flexibility_4w"
    return "beginner_4w"

def get_overall_level(scores: dict) -> str:
    """综合评级"""
    levels = [l for l, _ in scores.values()]
    if levels.count("优秀") >= 3:
        return "A", "体能优秀"
    elif levels.count("良好") + levels.count("优秀") >= 3:
        return "B", "体能良好"
    elif levels.count("及格") + levels.count("良好") + levels.count("优秀") >= 3:
        return "C", "体能及格"
    else:
        return "D", "需要加强"
