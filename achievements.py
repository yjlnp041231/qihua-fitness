"""成就系统"""

from dataclasses import dataclass

@dataclass
class Achievement:
    id: str
    name: str
    icon: str
    description: str
    condition_desc: str

ACHIEVEMENTS = {
    # 训练次数
    "first_workout": Achievement("first_workout", "初出茅庐", "🎯", "完成第一次训练", "训练1次"),
    "workout_10": Achievement("workout_10", "小有坚持", "🔥", "累计训练10次", "训练10次"),
    "workout_50": Achievement("workout_50", "健身达人", "💪", "累计训练50次", "训练50次"),
    "workout_100": Achievement("workout_100", "百炼成钢", "🏆", "累计训练100次", "训练100次"),
    # 连续训练
    "streak_3": Achievement("streak_3", "三天打鱼", "📅", "连续训练3天", "连续3天"),
    "streak_7": Achievement("streak_7", "一周不落", "🗓️", "连续训练7天", "连续7天"),
    "streak_30": Achievement("streak_30", "月度战士", "⭐", "连续训练30天", "连续30天"),
    # 俯卧撑
    "pushup_50": Achievement("pushup_50", "俯卧撑入门", "🫸", "累计完成50个俯卧撑", "50个俯卧撑"),
    "pushup_500": Achievement("pushup_500", "俯卧撑高手", "🤲", "累计完成500个俯卧撑", "500个俯卧撑"),
    # 深蹲
    "squat_100": Achievement("squat_100", "深蹲入门", "🦵", "累计完成100个深蹲", "100个深蹲"),
    "squat_1000": Achievement("squat_1000", "铁腿战士", "🦿", "累计完成1000个深蹲", "1000个深蹲"),
    # 评分
    "score_90": Achievement("score_90", "完美动作", "✨", "单次评分达到90分", "评分≥90"),
    "score_perfect": Achievement("score_perfect", "满分大师", "👑", "单次评分达到100分", "评分100"),
    # 卡路里
    "cal_1000": Achievement("cal_1000", "千卡俱乐部", "🔥", "累计消耗1000千卡", "消耗1000kcal"),
    "cal_10000": Achievement("cal_10000", "万卡传奇", "🌋", "累计消耗10000千卡", "消耗10000kcal"),
    # 课程
    "course_1": Achievement("course_1", "课程初体验", "📚", "完成第一个课程", "完成1个课程"),
    "course_10": Achievement("course_10", "课程达人", "🎓", "完成10个课程", "完成10个课程"),
    # 体测
    "assess_1": Achievement("assess_1", "了解自己", "📏", "完成第一次体测", "完成1次体测"),
}

def check_achievements(db_stats: dict) -> list:
    """检查是否解锁新成就，返回新解锁的成就ID列表"""
    new = []
    total = db_stats.get("total_workouts", 0)
    streak = db_stats.get("streak", 0)
    total_pushups = db_stats.get("total_pushups", 0)
    total_squats = db_stats.get("total_squats", 0)
    total_cal = db_stats.get("total_calories", 0)
    max_score = db_stats.get("max_score", 0)
    courses_done = db_stats.get("courses_done", 0)
    assessments_done = db_stats.get("assessments_done", 0)

    checks = [
        ("first_workout", total >= 1), ("workout_10", total >= 10),
        ("workout_50", total >= 50), ("workout_100", total >= 100),
        ("streak_3", streak >= 3), ("streak_7", streak >= 7), ("streak_30", streak >= 30),
        ("pushup_50", total_pushups >= 50), ("pushup_500", total_pushups >= 500),
        ("squat_100", total_squats >= 100), ("squat_1000", total_squats >= 1000),
        ("score_90", max_score >= 90), ("score_perfect", max_score >= 100),
        ("cal_1000", total_cal >= 1000), ("cal_10000", total_cal >= 10000),
        ("course_1", courses_done >= 1), ("course_10", courses_done >= 10),
        ("assess_1", assessments_done >= 1),
    ]
    for aid, cond in checks:
        if cond:
            new.append(aid)
    return new

def get_achievement(achievement_id):
    return ACHIEVEMENTS.get(achievement_id)

def get_all_achievements():
    return list(ACHIEVEMENTS.values())
