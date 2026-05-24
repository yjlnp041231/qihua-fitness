"""
训练课程系统
"""

from dataclasses import dataclass
from typing import List


@dataclass
class ExerciseStep:
    """训练步骤"""
    name: str
    duration: int  # 秒
    reps: int = 0  # 次数（0表示按时间）
    rest_after: int = 0  # 组间休息秒数


@dataclass
class Course:
    """训练课程"""
    name: str
    description: str
    difficulty: str  # beginner/intermediate/advanced
    duration: int  # 总时长（分钟）
    calories: int  # 预估卡路里
    exercises: List[ExerciseStep]
    category: str  # hiit/strength/cardio/flexibility


# ==================== 预设课程 ====================

COURSES = {
    "hiit_20": Course(
        name="HIIT 燃脂 20分钟",
        description="高强度间歇训练，快速燃脂",
        difficulty="intermediate",
        duration=20,
        calories=250,
        category="hiit",
        exercises=[
            ExerciseStep("开合跳", 30, rest_after=10),
            ExerciseStep("深蹲", 30, reps=15, rest_after=10),
            ExerciseStep("高抬腿", 30, rest_after=10),
            ExerciseStep("俯卧撑", 30, reps=10, rest_after=10),
            ExerciseStep("波比跳", 30, reps=8, rest_after=10),
            ExerciseStep("开合跳", 30, rest_after=10),
            ExerciseStep("深蹲", 30, reps=15, rest_after=10),
            ExerciseStep("高抬腿", 30, rest_after=10),
            ExerciseStep("俯卧撑", 30, reps=10, rest_after=10),
            ExerciseStep("波比跳", 30, reps=8, rest_after=10),
        ]
    ),

    "strength_upper": Course(
        name="上肢力量训练",
        description="针对胸、肩、臂的力量训练",
        difficulty="intermediate",
        duration=25,
        calories=180,
        category="strength",
        exercises=[
            ExerciseStep("俯卧撑", 0, reps=15, rest_after=30),
            ExerciseStep("俯卧撑", 0, reps=12, rest_after=30),
            ExerciseStep("俯卧撑", 0, reps=10, rest_after=30),
            ExerciseStep("引体向上", 0, reps=8, rest_after=45),
            ExerciseStep("引体向上", 0, reps=6, rest_after=45),
            ExerciseStep("引体向上", 0, reps=5, rest_after=30),
        ]
    ),

    "strength_lower": Course(
        name="下肢力量训练",
        description="针对腿部和臀部的力量训练",
        difficulty="intermediate",
        duration=25,
        calories=200,
        category="strength",
        exercises=[
            ExerciseStep("深蹲", 0, reps=20, rest_after=30),
            ExerciseStep("深蹲", 0, reps=18, rest_after=30),
            ExerciseStep("深蹲", 0, reps=15, rest_after=30),
            ExerciseStep("弓步蹲", 0, reps=12, rest_after=30),
            ExerciseStep("弓步蹲", 0, reps=10, rest_after=30),
        ]
    ),

    "core_10": Course(
        name="核心训练 10分钟",
        description="强化核心肌群",
        difficulty="beginner",
        duration=10,
        calories=80,
        category="strength",
        exercises=[
            ExerciseStep("卷腹", 0, reps=20, rest_after=15),
            ExerciseStep("平板支撑", 30, rest_after=15),
            ExerciseStep("卷腹", 0, reps=20, rest_after=15),
            ExerciseStep("平板支撑", 30, rest_after=15),
            ExerciseStep("卷腹", 0, reps=20, rest_after=15),
        ]
    ),

    "cardio_15": Course(
        name="有氧燃脂 15分钟",
        description="中低强度有氧训练",
        difficulty="beginner",
        duration=15,
        calories=150,
        category="cardio",
        exercises=[
            ExerciseStep("开合跳", 60, rest_after=15),
            ExerciseStep("高抬腿", 45, rest_after=15),
            ExerciseStep("开合跳", 60, rest_after=15),
            ExerciseStep("高抬腿", 45, rest_after=15),
            ExerciseStep("开合跳", 60, rest_after=15),
        ]
    ),

    "full_body": Course(
        name="全身训练 30分钟",
        description="全身综合训练",
        difficulty="advanced",
        duration=30,
        calories=350,
        category="hiit",
        exercises=[
            ExerciseStep("开合跳", 30, rest_after=10),
            ExerciseStep("深蹲", 0, reps=20, rest_after=15),
            ExerciseStep("俯卧撑", 0, reps=15, rest_after=15),
            ExerciseStep("弓步蹲", 0, reps=12, rest_after=15),
            ExerciseStep("卷腹", 0, reps=20, rest_after=15),
            ExerciseStep("波比跳", 0, reps=10, rest_after=20),
            ExerciseStep("平板支撑", 45, rest_after=15),
            ExerciseStep("高抬腿", 30, rest_after=10),
            ExerciseStep("深蹲", 0, reps=20, rest_after=15),
            ExerciseStep("俯卧撑", 0, reps=15, rest_after=15),
            ExerciseStep("弓步蹲", 0, reps=12, rest_after=15),
            ExerciseStep("卷腹", 0, reps=20, rest_after=15),
        ]
    ),
}


def get_course_list():
    """获取课程列表"""
    result = []
    for key, course in COURSES.items():
        result.append({
            "key": key,
            "name": course.name,
            "description": course.description,
            "difficulty": course.difficulty,
            "duration": course.duration,
            "calories": course.calories,
            "category": course.category
        })
    return result


def get_course(key):
    """获取课程详情"""
    return COURSES.get(key)


def get_courses_by_category(category):
    """按分类获取课程"""
    return [c for c in COURSES.values() if c.category == category]
