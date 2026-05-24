"""
训练数据存储模块
"""

import sqlite3
import os
from datetime import datetime, timedelta
from contextlib import contextmanager

DB_PATH = "fitness_data.db"


@contextmanager
def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """初始化数据库"""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exercise TEXT NOT NULL,
                sets INTEGER DEFAULT 0,
                reps INTEGER DEFAULT 0,
                duration_seconds INTEGER DEFAULT 0,
                calories REAL DEFAULT 0,
                avg_score INTEGER DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS body_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                weight REAL,
                height REAL,
                body_fat REAL,
                muscle_mass REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_type TEXT NOT NULL,
                target_value REAL NOT NULL,
                current_value REAL DEFAULT 0,
                deadline TEXT,
                achieved BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS plan_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id TEXT NOT NULL,
                week INTEGER DEFAULT 1,
                day INTEGER DEFAULT 1,
                completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                upper_strength REAL,
                core_strength REAL,
                lower_strength REAL,
                cardio REAL,
                flexibility REAL,
                overall_level TEXT,
                recommended_plan TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                achievement_id TEXT UNIQUE NOT NULL,
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)


def save_workout(exercise, sets, reps, duration_seconds, calories, avg_score, notes=""):
    """保存训练记录"""
    with get_db() as conn:
        conn.execute("""
            INSERT INTO workouts (exercise, sets, reps, duration_seconds, calories, avg_score, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (exercise, sets, reps, duration_seconds, calories, avg_score, notes))


def save_body_stats(weight=None, height=None, body_fat=None, muscle_mass=None, notes=""):
    """保存身体数据"""
    with get_db() as conn:
        conn.execute("""
            INSERT INTO body_stats (weight, height, body_fat, muscle_mass, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (weight, height, body_fat, muscle_mass, notes))


def get_workout_history(days=30):
    """获取训练历史"""
    with get_db() as conn:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        rows = conn.execute("""
            SELECT * FROM workouts WHERE created_at >= ? ORDER BY created_at DESC
        """, (cutoff,)).fetchall()
        return [dict(r) for r in rows]


def get_body_stats_history(limit=10):
    """获取身体数据历史"""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT * FROM body_stats ORDER BY created_at DESC LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]


def get_weekly_summary():
    """获取本周训练汇总"""
    with get_db() as conn:
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        rows = conn.execute("""
            SELECT exercise, COUNT(*) as sessions, SUM(reps) as total_reps,
                   SUM(duration_seconds) as total_duration, SUM(calories) as total_calories,
                   AVG(avg_score) as avg_score
            FROM workouts WHERE created_at >= ?
            GROUP BY exercise
        """, (week_ago,)).fetchall()
        return [dict(r) for r in rows]


def get_monthly_summary():
    """获取本月训练汇总"""
    with get_db() as conn:
        month_ago = (datetime.now() - timedelta(days=30)).isoformat()
        rows = conn.execute("""
            SELECT exercise, COUNT(*) as sessions, SUM(reps) as total_reps,
                   SUM(duration_seconds) as total_duration, SUM(calories) as total_calories,
                   AVG(avg_score) as avg_score
            FROM workouts WHERE created_at >= ?
            GROUP BY exercise
        """, (month_ago,)).fetchall()
        return [dict(r) for r in rows]


def get_streak():
    """获取连续训练天数"""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT DISTINCT DATE(created_at) as day FROM workouts
            ORDER BY day DESC
        """).fetchall()

        if not rows:
            return 0

        streak = 0
        today = datetime.now().date()
        for row in rows:
            day = datetime.strptime(row['day'], '%Y-%m-%d').date()
            if day == today - timedelta(days=streak):
                streak += 1
            else:
                break
        return streak


# ==================== 计划进度 ====================

def save_plan_progress(plan_id, week, day, completed=False):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO plan_progress (plan_id, week, day, completed)
            VALUES (?, ?, ?, ?)
        """, (plan_id, week, day, completed))


def get_plan_progress(plan_id):
    with get_db() as conn:
        rows = conn.execute("""
            SELECT * FROM plan_progress WHERE plan_id = ? ORDER BY week, day
        """, (plan_id,)).fetchall()
        return [dict(r) for r in rows]


def mark_plan_day_done(plan_id, week, day):
    with get_db() as conn:
        existing = conn.execute("""
            SELECT id FROM plan_progress WHERE plan_id=? AND week=? AND day=?
        """, (plan_id, week, day)).fetchone()
        if existing:
            conn.execute("UPDATE plan_progress SET completed=1 WHERE id=?", (existing['id'],))
        else:
            conn.execute("""
                INSERT INTO plan_progress (plan_id, week, day, completed) VALUES (?, ?, ?, 1)
            """, (plan_id, week, day))


# ==================== 体测 ====================

def save_assessment(results, overall_level, recommended_plan):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO assessments (upper_strength, core_strength, lower_strength,
                                     cardio, flexibility, overall_level, recommended_plan)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (results.get('upper_strength'), results.get('core_strength'),
              results.get('lower_strength'), results.get('cardio'),
              results.get('flexibility'), overall_level, recommended_plan))


def get_assessment_history(limit=5):
    with get_db() as conn:
        rows = conn.execute("""
            SELECT * FROM assessments ORDER BY created_at DESC LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]


# ==================== 成就 ====================

def unlock_achievement(achievement_id):
    with get_db() as conn:
        try:
            conn.execute("""
                INSERT INTO achievements (achievement_id) VALUES (?)
            """, (achievement_id,))
            return True
        except sqlite3.IntegrityError:
            return False


def get_unlocked_achievements():
    with get_db() as conn:
        rows = conn.execute("SELECT achievement_id FROM achievements").fetchall()
        return [r['achievement_id'] for r in rows]


def get_achievement_stats():
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) as c FROM workouts").fetchone()['c']
        streak = get_streak()
        pushups = conn.execute("SELECT COALESCE(SUM(reps),0) as c FROM workouts WHERE exercise='俯卧撑'").fetchone()['c']
        squats = conn.execute("SELECT COALESCE(SUM(reps),0) as c FROM workouts WHERE exercise='深蹲'").fetchone()['c']
        calories = conn.execute("SELECT COALESCE(SUM(calories),0) as c FROM workouts").fetchone()['c']
        max_score = conn.execute("SELECT COALESCE(MAX(avg_score),0) as c FROM workouts").fetchone()['c']
        courses = conn.execute("SELECT COUNT(DISTINCT exercise) as c FROM workouts WHERE notes LIKE '%课程%'").fetchone()['c']
        assess = conn.execute("SELECT COUNT(*) as c FROM assessments").fetchone()['c']
        return {"total_workouts": total, "streak": streak, "total_pushups": pushups,
                "total_squats": squats, "total_calories": calories, "max_score": max_score,
                "courses_done": courses, "assessments_done": assess}


# 初始化
init_db()
