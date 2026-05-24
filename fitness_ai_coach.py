"""
AI 智能健身私教系统 v3.0
功能：实时分析、动作评分、语音播报、课程系统、训练记录、周报统计
运行：streamlit run fitness_ai_coach.py
"""

import streamlit as st
import cv2
import numpy as np
import tempfile
import os
import time
import threading
from collections import deque
from database import (save_workout, get_workout_history, get_weekly_summary,
                      get_monthly_summary, get_streak, save_body_stats,
                      get_body_stats_history, save_plan_progress, get_plan_progress,
                      mark_plan_day_done, save_assessment, get_assessment_history,
                      unlock_achievement, get_unlocked_achievements, get_achievement_stats)
from courses import COURSES, get_course_list, get_course
from plans import get_plan_list, get_plan, GOAL_LABELS
from assessment import ASSESSMENTS, evaluate, recommend_plan, get_overall_level
from achievements import ACHIEVEMENTS, check_achievements, get_achievement, get_all_achievements

# ==================== 启划健身 皮肤注入 ====================

KEEP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --qh-green: #10b981;
    --qh-green-light: #d1fae5;
    --qh-green-dark: #059669;
    --qh-bg: #f8fafc;
    --qh-card: #ffffff;
    --qh-text: #1e293b;
    --qh-muted: #94a3b8;
    --qh-border: #e2e8f0;
    --qh-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --qh-shadow-md: 0 4px 6px rgba(0,0,0,0.05), 0 2px 4px rgba(0,0,0,0.04);
    --qh-radius: 16px;
    --qh-radius-lg: 24px;
}

/* 全局字体 */
.stApp, .stApp * { font-family: 'Inter', -apple-system, sans-serif !important; }

/* 隐藏默认Streamlit元素 */
#MainMenu, footer, header { visibility: hidden; }

/* 侧边栏美化 */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    border-right: 1px solid var(--qh-border);
}
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stSelectbox label {
    font-weight: 600;
    color: var(--qh-text);
    font-size: 13px;
}
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] div[aria-checked="true"] {
    background-color: var(--qh-green) !important;
    border-color: var(--qh-green) !important;
}

/* 按钮美化 */
.stButton>button {
    background: var(--qh-green) !important;
    color: white !important;
    border: none !important;
    border-radius: 999px !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 10px 24px !important;
    box-shadow: 0 2px 8px rgba(16,185,129,0.25) !important;
    transition: all 0.2s !important;
}
.stButton>button:hover {
    background: var(--qh-green-dark) !important;
    box-shadow: 0 4px 12px rgba(16,185,129,0.35) !important;
    transform: translateY(-1px) !important;
}

/* 卡片容器 */
.qh-card {
    background: var(--qh-card);
    border: 1px solid var(--qh-border);
    border-radius: var(--qh-radius);
    padding: 20px;
    box-shadow: var(--qh-shadow);
    transition: all 0.2s;
}
.qh-card:hover { box-shadow: var(--qh-shadow-md); }

.qh-card-lg {
    background: var(--qh-card);
    border: 1px solid var(--qh-border);
    border-radius: var(--qh-radius-lg);
    padding: 24px;
    box-shadow: var(--qh-shadow);
}

/* 圆环进度条 */
.qh-ring-container {
    position: relative;
    width: 120px;
    height: 120px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.qh-ring-container svg { transform: rotate(-90deg); }
.qh-ring-center {
    position: absolute;
    text-align: center;
}
.qh-ring-value {
    font-size: 28px;
    font-weight: 800;
    color: var(--qh-text);
    line-height: 1;
    font-family: 'JetBrains Mono', monospace;
}
.qh-ring-label {
    font-size: 10px;
    color: var(--qh-muted);
    font-weight: 600;
    margin-top: 2px;
}

/* 大数字 */
.qh-big-number {
    font-size: 48px;
    font-weight: 800;
    color: var(--qh-text);
    line-height: 1;
    font-family: 'Inter', sans-serif;
}
.qh-big-unit {
    font-size: 16px;
    font-weight: 600;
    color: var(--qh-muted);
    margin-left: 4px;
}

/* 指标卡片 */
.qh-metric-card {
    background: var(--qh-card);
    border: 1px solid var(--qh-border);
    border-radius: var(--qh-radius);
    padding: 16px;
    text-align: center;
}
.qh-metric-icon {
    font-size: 24px;
    margin-bottom: 8px;
}
.qh-metric-value {
    font-size: 24px;
    font-weight: 800;
    color: var(--qh-text);
    font-family: 'Inter', sans-serif;
}
.qh-metric-label {
    font-size: 11px;
    color: var(--qh-muted);
    font-weight: 600;
    margin-top: 4px;
}

/* 标签 */
.qh-tag {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
}
.qh-tag-green { background: var(--qh-green-light); color: var(--qh-green); }
.qh-tag-red { background: #fee2e2; color: #ef4444; }
.qh-tag-amber { background: #fef3c7; color: #f59e0b; }
.qh-tag-blue { background: #dbeafe; color: #3b82f6; }

/* 进度条 */
.qh-progress {
    height: 6px;
    background: #f1f5f9;
    border-radius: 999px;
    overflow: hidden;
}
.qh-progress-bar {
    height: 100%;
    background: linear-gradient(90deg, var(--qh-green), #34d399);
    border-radius: 999px;
    transition: width 0.5s ease;
}

/* 课程卡片 */
.qh-course-card {
    background: var(--qh-card);
    border: 1px solid var(--qh-border);
    border-radius: var(--qh-radius-lg);
    padding: 16px;
    cursor: pointer;
    transition: all 0.2s;
}
.qh-course-card:hover {
    border-color: var(--qh-green);
    box-shadow: 0 4px 12px rgba(16,185,129,0.15);
}

/* 数据表格 */
.qh-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
}
.qh-table th {
    background: #f8fafc;
    padding: 10px 14px;
    text-align: left;
    font-size: 11px;
    font-weight: 700;
    color: var(--qh-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid var(--qh-border);
}
.qh-table td {
    padding: 12px 14px;
    font-size: 13px;
    border-bottom: 1px solid #f1f5f9;
}

/* Streamlit组件覆盖 */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: #f1f5f9;
    border-radius: 12px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    font-weight: 600;
    font-size: 13px;
    padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: var(--qh-green) !important;
    box-shadow: var(--qh-shadow);
}

/* 隐藏元素 */
.stDeployButton { display: none; }
[data-testid="stToolbar"] { display: none; }
</style>
"""

st.markdown(KEEP_CSS, unsafe_allow_html=True)

# ==================== 工具函数 ====================

def calc_angle(a, b, c):
    a, b, c = np.array(a, float), np.array(b, float), np.array(c, float)
    ba, bc = a - b, c - b
    cos = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    return np.degrees(np.arccos(np.clip(cos, -1, 1)))

def px(lm, idx, w, h):
    return (int(lm[idx].x * w), int(lm[idx].y * h))

def nx(lm, idx):
    return (lm[idx].x, lm[idx].y)

def speak(text):
    def _run():
        try:
            import pyttsx3
            e = pyttsx3.init()
            e.setProperty('rate', 150)
            e.say(text)
            e.runAndWait()
        except: pass
    threading.Thread(target=_run, daemon=True).start()

# ==================== 卡路里估算 ====================

CALORIE_RATES = {
    "squat": 0.32, "deadlift": 0.35, "pushup": 0.28, "pullup": 0.35,
    "crunch": 0.20, "plank": 0.15, "lunge": 0.30, "burpee": 0.50,
    "jumping_jack": 0.25, "high_knee": 0.30
}

def estimate_calories(exercise, duration_sec, reps=0):
    rate = CALORIE_RATES.get(exercise, 0.25)
    if reps > 0:
        return round(reps * rate, 1)
    return round(duration_sec * rate / 60, 1)

# ==================== 模型加载 ====================

@st.cache_resource
def load_model():
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    model_path = "pose_landmarker.task"
    if not os.path.exists(model_path):
        import urllib.request
        try:
            urllib.request.urlretrieve(
                "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task",
                model_path)
        except Exception as e:
            st.error(f"模型下载失败: {e}")
            st.stop()
    base = python.BaseOptions(model_asset_path=model_path)
    opts = vision.PoseLandmarkerOptions(
        base_options=base, running_mode=vision.RunningMode.VIDEO,
        min_pose_detection_confidence=0.5, min_tracking_confidence=0.5, num_poses=1)
    return vision.PoseLandmarker.create_from_options(opts)

# ==================== 动作评分 ====================

def score_squat(r):
    s, d = 100, []
    ka, ba = r["knee_angle"], r["back_angle"]
    if ka < 60: s -= 25; d.append("深蹲过深 -25")
    elif ka < 70: s -= 10; d.append("深蹲略深 -10")
    elif ka > 120: s -= 20; d.append("深蹲不足 -20")
    if ba > 30: s -= 25; d.append("背部严重弯曲 -25")
    elif ba > 20: s -= 15; d.append("背部轻微弯曲 -15")
    if r["knee_valgus"]: s -= 20; d.append("膝盖内扣 -20")
    if r["knee_over_toe"]: s -= 15; d.append("膝盖超脚尖 -15")
    return max(0, s), d

def score_pushup(r):
    s, d = 100, []
    if r["elbow_angle"] > 120: s -= 30; d.append("下沉不足 -30")
    elif r["elbow_angle"] > 100: s -= 15; d.append("下沉略浅 -15")
    if not r["body_ok"]: s -= 25; d.append("身体未直线 -25")
    return max(0, s), d

# ==================== 深蹲/硬拉分析 ====================

def analyze_squat(lm, w, h):
    SH, HP, KN, AN, TO = 12, 24, 26, 28, 30
    shoulder, hip, knee, ankle = px(lm, SH, w, h), px(lm, HP, w, h), px(lm, KN, w, h), px(lm, AN, w, h)
    kx, ky = nx(lm, KN); hx, hy = nx(lm, HP); ax, ay = nx(lm, AN); tx, ty = nx(lm, TO)
    knee_angle = calc_angle(hip, knee, ankle)
    back_angle = calc_angle((shoulder[0], shoulder[1]-200), shoulder, hip)
    mid_x = (hx + ax) / 2
    knee_valgus = abs(kx - mid_x) > 0.07
    knee_over_toe = kx > tx + 0.04
    warnings = []
    if knee_valgus: warnings.append("双膝内扣")
    if knee_over_toe: warnings.append("膝盖超脚尖")
    if back_angle > 25: warnings.append("背部弯曲")
    if knee_angle < 60: warnings.append("深蹲过深")
    return {"shoulder": shoulder, "hip": hip, "knee": knee, "ankle": ankle,
            "knee_angle": knee_angle, "back_angle": back_angle,
            "knee_valgus": knee_valgus, "knee_over_toe": knee_over_toe, "warnings": warnings}

def draw_squat(frame, r, score=None):
    color = (0, 0, 255) if r["warnings"] else (0, 255, 0)
    cv2.line(frame, r["shoulder"], r["hip"], color, 3)
    cv2.line(frame, r["hip"], r["knee"], color, 3)
    cv2.line(frame, r["knee"], r["ankle"], color, 3)
    for p in [r["shoulder"], r["hip"], r["knee"], r["ankle"]]:
        cv2.circle(frame, p, 8, (255, 0, 0), -1)
    cv2.putText(frame, f"Knee:{r['knee_angle']:.0f}", (r["knee"][0]+10, r["knee"][1]-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    if score is not None:
        sc = (0,255,0) if score>=80 else (0,255,255) if score>=60 else (0,0,255)
        cv2.putText(frame, f"Score:{score}", (frame.shape[1]-200, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, sc, 3)
    y = 30
    for w in r["warnings"]:
        cv2.putText(frame, f"! {w}", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        y += 30
    return frame

# ==================== 俯卧撑分析 ====================

class PushupCounter:
    def __init__(self):
        self.count = 0; self.peak = 0.0; self.valley = 1.0
        self.state = "up"; self.depth_log = []; self.score_log = []

    def update(self, lm, w, h):
        SH, EL, WR, HP, AN = 12, 14, 16, 24, 28
        shoulder, elbow, wrist = px(lm, SH, w, h), px(lm, EL, w, h), px(lm, WR, w, h)
        hip, ankle = px(lm, HP, w, h), px(lm, AN, w, h)
        sy = lm[SH].y
        elbow_angle = calc_angle(shoulder, elbow, wrist)
        body_angle = calc_angle(shoulder, hip, ankle)
        body_ok = abs(body_angle - 180) < 20
        if sy > self.peak: self.peak = sy; self.state = "down"
        if sy < self.valley: self.valley = sy
        new_count = False
        if self.state == "down" and sy < self.peak - 0.03:
            self.count += 1; new_count = True
            self.depth_log.append(elbow_angle < 100)
            self.score_log.append(score_pushup({"elbow_angle": elbow_angle, "body_ok": body_ok})[0])
            self.state = "up"; self.peak = 0.0; self.valley = 1.0
        return {"shoulder": shoulder, "elbow": elbow, "wrist": wrist, "hip": hip,
                "elbow_angle": elbow_angle, "body_ok": body_ok, "count": self.count,
                "last_depth_ok": self.depth_log[-1] if self.depth_log else None,
                "new_count": new_count, "last_score": self.score_log[-1] if self.score_log else None}

def draw_pushup(frame, r):
    color = (0, 255, 0) if r["body_ok"] else (0, 0, 255)
    cv2.line(frame, r["shoulder"], r["elbow"], color, 3)
    cv2.line(frame, r["elbow"], r["wrist"], color, 3)
    cv2.line(frame, r["shoulder"], r["hip"], (255, 255, 0), 2)
    for p in [r["shoulder"], r["elbow"], r["wrist"], r["hip"]]:
        cv2.circle(frame, p, 8, (255, 0, 0), -1)
    cv2.putText(frame, f"Count:{r['count']}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    if r["last_score"]:
        sc = (0,255,0) if r["last_score"]>=80 else (0,255,255) if r["last_score"]>=60 else (0,0,255)
        cv2.putText(frame, f"Score:{r['last_score']}", (frame.shape[1]-200, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, sc, 3)
    return frame

# ==================== 卷腹分析 ====================

class CrunchCounter:
    def __init__(self):
        self.count = 0; self.peak = 0.0; self.state = "down"
    def update(self, lm, w, h):
        SH, HP = 12, 24
        shoulder, hip = px(lm, SH, w, h), px(lm, HP, w, h)
        sy = lm[SH].y
        torso_angle = calc_angle(shoulder, hip, (hip[0], hip[1]+100))
        if sy > self.peak: self.peak = sy; self.state = "down"
        new_count = False
        if self.state == "down" and sy < self.peak - 0.04:
            self.count += 1; new_count = True; self.state = "up"; self.peak = 0.0
        return {"shoulder": shoulder, "hip": hip, "torso_angle": torso_angle,
                "count": self.count, "new_count": new_count}

def draw_crunch(frame, r):
    cv2.line(frame, r["shoulder"], r["hip"], (0, 255, 0), 3)
    cv2.circle(frame, r["shoulder"], 8, (255, 0, 0), -1)
    cv2.circle(frame, r["hip"], 8, (255, 0, 0), -1)
    cv2.putText(frame, f"Count:{r['count']}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    return frame

# ==================== 平板支撑分析 ====================

class PlankTimer:
    def __init__(self):
        self.start_time = None; self.total = 0; self.hip_log = []
    def update(self, lm, w, h):
        SH, HP, AN = 12, 24, 28
        shoulder, hip, ankle = px(lm, SH, w, h), px(lm, HP, w, h), px(lm, AN, w, h)
        body_angle = calc_angle(shoulder, hip, ankle)
        body_ok = abs(body_angle - 170) < 20
        if self.start_time is None: self.start_time = time.time()
        elapsed = time.time() - self.start_time
        self.hip_log.append(body_ok)
        return {"shoulder": shoulder, "hip": hip, "ankle": ankle,
                "body_angle": body_angle, "body_ok": body_ok, "elapsed": elapsed}

def draw_plank(frame, r):
    color = (0, 255, 0) if r["body_ok"] else (0, 0, 255)
    cv2.line(frame, r["shoulder"], r["hip"], color, 3)
    cv2.line(frame, r["hip"], r["ankle"], color, 3)
    cv2.putText(frame, f"Time:{r['elapsed']:.0f}s", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    if not r["body_ok"]:
        cv2.putText(frame, "Keep body straight!", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    return frame

# ==================== 弓步蹲分析 ====================

class LungeCounter:
    def __init__(self):
        self.count = 0; self.peak = 0.0; self.state = "up"
    def update(self, lm, w, h):
        HP, KN, AN = 24, 26, 28
        hip, knee, ankle = px(lm, HP, w, h), px(lm, KN, w, h), px(lm, AN, w, h)
        knee_angle = calc_angle(hip, knee, ankle)
        hy = lm[HP].y
        if hy > self.peak: self.peak = hy; self.state = "down"
        new_count = False
        if self.state == "down" and hy < self.peak - 0.03:
            self.count += 1; new_count = True; self.state = "up"; self.peak = 0.0
        return {"hip": hip, "knee": knee, "ankle": ankle, "knee_angle": knee_angle,
                "count": self.count, "new_count": new_count}

def draw_lunge(frame, r):
    cv2.line(frame, r["hip"], r["knee"], (0, 255, 0), 3)
    cv2.line(frame, r["knee"], r["ankle"], (0, 255, 0), 3)
    cv2.putText(frame, f"Count:{r['count']}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    cv2.putText(frame, f"Knee:{r['knee_angle']:.0f}", (r["knee"][0]+10, r["knee"][1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return frame

# ==================== 开合跳分析 ====================

class JumpingJackCounter:
    def __init__(self):
        self.count = 0; self.state = "together"
    def update(self, lm, w, h):
        LW, RW, LA, RA = 15, 16, 27, 28
        lw, rw = px(lm, LW, w, h), px(lm, RW, w, h)
        la, ra = px(lm, LA, w, h), px(lm, RA, w, h)
        hand_dist = abs(lw[0] - rw[0]) / w
        foot_dist = abs(la[0] - ra[0]) / w
        spread = hand_dist > 0.3 and foot_dist > 0.15
        new_count = False
        if self.state == "together" and spread:
            self.state = "apart"
        elif self.state == "apart" and not spread:
            self.count += 1; new_count = True; self.state = "together"
        return {"lw": lw, "rw": rw, "la": la, "ra": ra,
                "count": self.count, "new_count": new_count, "spread": spread}

def draw_jumping_jack(frame, r):
    color = (0, 255, 0) if r["spread"] else (0, 255, 255)
    cv2.circle(frame, r["lw"], 8, color, -1); cv2.circle(frame, r["rw"], 8, color, -1)
    cv2.circle(frame, r["la"], 8, color, -1); cv2.circle(frame, r["ra"], 8, color, -1)
    cv2.putText(frame, f"Count:{r['count']}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    return frame

# ==================== 波比跳分析 ====================

class BurpeeCounter:
    def __init__(self):
        self.count = 0; self.phase = "stand"; self.lowest_y = 0
    def update(self, lm, w, h):
        SH, HP, AN = 12, 24, 28
        sy, hy = lm[SH].y, lm[HP].y
        shoulder = px(lm, SH, w, h); hip = px(lm, HP, w, h)
        new_count = False
        if self.phase == "stand" and hy > 0.6:
            self.phase = "down"
        elif self.phase == "down":
            self.lowest_y = max(self.lowest_y, hy)
            if sy < 0.4: self.phase = "jump"
        elif self.phase == "jump" and hy < 0.5:
            self.count += 1; new_count = True; self.phase = "stand"; self.lowest_y = 0
        return {"shoulder": shoulder, "hip": hip, "count": self.count, "new_count": new_count, "phase": self.phase}

def draw_burpee(frame, r):
    cv2.putText(frame, f"Count:{r['count']}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    cv2.putText(frame, f"Phase:{r['phase']}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
    return frame

# ==================== 高抬腿分析 ====================

class HighKneeCounter:
    def __init__(self):
        self.count = 0; self.state = "down"
    def update(self, lm, w, h):
        LK, RK, LH, RH = 25, 26, 23, 24
        lk_y, rk_y = lm[LK].y, lm[RK].y
        knee = px(lm, LK, w, h) if lk_y < rk_y else px(lm, RK, w, h)
        hip_y = (lm[LH].y + lm[RH].y) / 2
        raised = min(lk_y, rk_y) < hip_y - 0.05
        new_count = False
        if self.state == "down" and raised:
            self.count += 1; new_count = True; self.state = "up"
        elif self.state == "up" and not raised:
            self.state = "down"
        return {"knee": knee, "count": self.count, "new_count": new_count, "raised": raised}

def draw_high_knee(frame, r):
    color = (0, 255, 0) if r["raised"] else (0, 255, 255)
    cv2.circle(frame, r["knee"], 10, color, -1)
    cv2.putText(frame, f"Count:{r['count']}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    return frame

# ==================== 引体向上分析 ====================

class PullupCounter:
    def __init__(self):
        self.count = 0; self.peak = 1.0; self.state = "down"
    def update(self, lm, w, h):
        SH, EL, WR = 12, 14, 16
        shoulder, elbow, wrist = px(lm, SH, w, h), px(lm, EL, w, h), px(lm, WR, w, h)
        sy = lm[SH].y
        elbow_angle = calc_angle(shoulder, elbow, wrist)
        if sy < self.peak: self.peak = sy
        new_count = False
        if self.state == "down" and sy < 0.35:
            self.state = "up"
        elif self.state == "up" and sy > 0.45:
            self.count += 1; new_count = True; self.state = "down"; self.peak = 1.0
        return {"shoulder": shoulder, "elbow": elbow, "wrist": wrist,
                "elbow_angle": elbow_angle, "count": self.count, "new_count": new_count}

def draw_pullup(frame, r):
    cv2.line(frame, r["shoulder"], r["elbow"], (0, 255, 0), 3)
    cv2.line(frame, r["elbow"], r["wrist"], (0, 255, 0), 3)
    cv2.putText(frame, f"Count:{r['count']}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    return frame

# ==================== 视频处理 ====================

EXERCISE_MAP = {
    "深蹲": ("squat", analyze_squat, draw_squat, score_squat),
    "硬拉": ("squat", analyze_squat, draw_squat, score_squat),
    "俯卧撑": ("pushup", None, draw_pushup, score_pushup),
    "引体向上": ("pullup", None, draw_pullup, None),
    "卷腹": ("crunch", None, draw_crunch, None),
    "平板支撑": ("plank", None, draw_plank, None),
    "弓步蹲": ("lunge", None, draw_lunge, None),
    "开合跳": ("jj", None, draw_jumping_jack, None),
    "波比跳": ("burpee", None, draw_burpee, None),
    "高抬腿": ("hk", None, draw_high_knee, None),
}

def make_counter(key):
    return {"pushup": PushupCounter, "pullup": PullupCounter, "crunch": CrunchCounter,
            "plank": PlankTimer, "lunge": LungeCounter, "jj": JumpingJackCounter,
            "burpee": BurpeeCounter, "hk": HighKneeCounter}.get(key, lambda: None)()

def process_video(video_path, exercise_name):
    landmarker = load_model()
    from mediapipe import Image, ImageFormat
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    output_path = tempfile.mktemp(suffix='.mp4')
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))

    key, analyze_fn, draw_fn, score_fn = EXERCISE_MAP[exercise_name]
    counter = make_counter(key)
    all_warnings, all_scores, frame_count = [], [], 0
    progress = st.progress(0); status = st.empty()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        frame_count += 1
        ts = int((frame_count - 1) * 1000 / fps)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = landmarker.detect_for_video(Image(image_format=ImageFormat.SRGB, data=rgb), ts)

        if result.pose_landmarks:
            lm = result.pose_landmarks[0]
            if analyze_fn:
                r = analyze_fn(lm, w, h)
                if score_fn:
                    sc, _ = score_fn(r); all_scores.append(sc)
                    frame = draw_fn(frame, r, sc)
                else:
                    frame = draw_fn(frame, r)
                all_warnings.extend(r.get("warnings", []))
            elif counter:
                r = counter.update(lm, w, h)
                frame = draw_fn(frame, r)

        out.write(frame)
        progress.progress(min(frame_count / total, 1.0))
        if frame_count % 30 == 0:
            status.text(f"处理中... {frame_count}/{total}")

    cap.release(); out.release()
    avg_score = int(sum(all_scores)/len(all_scores)) if all_scores else 0
    reps = counter.count if counter and hasattr(counter, 'count') else 0
    dur = int(frame_count / fps)
    return output_path, {"frames": frame_count, "warnings": list(set(all_warnings)),
                         "count": reps, "avg_score": avg_score, "duration": dur}

# ==================== 实时摄像头 ====================

def process_webcam(exercise_name):
    landmarker = load_model()
    from mediapipe import Image, ImageFormat
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("无法打开摄像头"); return

    key, analyze_fn, draw_fn, score_fn = EXERCISE_MAP[exercise_name]
    counter = make_counter(key)
    fps_buf = deque(maxlen=30)
    last_t = time.time()
    last_warn = 0

    frame_ph = st.empty()
    metrics_ph = st.empty()
    stop = False
    start_t = time.time()

    while not stop:
        ret, frame = cap.read()
        if not ret: break
        now = time.time()
        fps_buf.append(1.0 / (now - last_t + 1e-6))
        last_t = now
        h, w = frame.shape[:2]
        ts = int(now * 1000) % 1000000
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = landmarker.detect_for_video(Image(image_format=ImageFormat.SRGB, data=rgb), ts)

        score = 0
        if result.pose_landmarks:
            lm = result.pose_landmarks[0]
            if analyze_fn:
                r = analyze_fn(lm, w, h)
                if score_fn:
                    score, _ = score_fn(r)
                    frame = draw_fn(frame, r, score)
                else:
                    frame = draw_fn(frame, r)
                if r.get("warnings") and now - last_warn > 5:
                    speak(r["warnings"][0]); last_warn = now
            elif counter:
                r = counter.update(lm, w, h)
                frame = draw_fn(frame, r)
                score = r.get("last_score", 0) or 0
                if r.get("new_count"): speak(str(r["count"]))

        elapsed = int(now - start_t)
        m, s = divmod(elapsed, 60)
        cv2.putText(frame, f"FPS:{sum(fps_buf)/len(fps_buf):.0f}", (10, h-20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        cv2.putText(frame, f"Time:{m:02d}:{s:02d}", (w-180, h-20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        frame_ph.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)

        with metrics_ph.container():
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("时间", f"{m:02d}:{s:02d}")
            with c2: st.metric("评分", f"{score}分")
            with c3: st.metric("次数", counter.count if counter and hasattr(counter, 'count') else "-")

    cap.release()
    st.success("训练完成！")
    reps = counter.count if counter and hasattr(counter, 'count') else 0
    dur = int(time.time() - start_t)
    calories = estimate_calories(key, dur, reps)
    save_workout(exercise_name, 1, reps, dur, calories, score)
    st.metric("卡路里消耗", f"{calories} kcal")

# ==================== 页面：训练 ====================

def page_training():
    st.header("🏋️ 训练")

    with st.sidebar:
        exercise = st.selectbox("训练动作", list(EXERCISE_MAP.keys()))
        input_mode = st.radio("输入方式", ["📹 实时摄像头", "📤 上传视频"])

        tips = {"深蹲": "背部挺直，膝盖与脚尖同向", "硬拉": "髋关节主导，背部挺直",
                "俯卧撑": "身体一条直线，下沉到位", "引体向上": "下巴过杠，控制速度",
                "卷腹": "下背贴地，腹肌发力", "平板支撑": "身体一条直线，核心收紧",
                "弓步蹲": "膝盖不超过脚尖，躯干直立", "开合跳": "手脚同步，落地轻柔",
                "波比跳": "动作连贯，跳跃充分", "高抬腿": "膝盖过髋，摆臂配合"}
        st.info(f"**要点：** {tips.get(exercise, '')}")

    if input_mode == "📹 实时摄像头":
        st.subheader(f"📹 {exercise} - 实时分析")
        if st.button("🚀 开始训练", type="primary"):
            process_webcam(exercise)
    else:
        video = st.file_uploader("上传训练视频", type=['mp4', 'avi', 'mov', 'mkv'])
        if video:
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            tfile.write(video.read()); tfile.close()
            st.video(video)
            if st.button("🚀 开始分析", type="primary"):
                with st.spinner("分析中..."):
                    out_path, stats = process_video(tfile.name, exercise)
                st.success("分析完成！")
                with open(out_path, 'rb') as f: st.video(f.read())

                avg = stats["avg_score"]
                sc_icon = "🟢" if avg >= 80 else "🟡" if avg >= 60 else "🔴"
                st.markdown(f"### {sc_icon} 综合评分：{avg}分")

                c1, c2, c3 = st.columns(3)
                with c1: st.metric("完成次数", stats["count"])
                with c2: st.metric("训练时长", f"{stats['duration']}秒")
                cal = estimate_calories(exercise.lower(), stats["duration"], stats["count"])
                with c3: st.metric("卡路里", f"{cal} kcal")

                if stats["warnings"]:
                    st.error("检测到问题：")
                    for w in stats["warnings"]: st.write(f"- {w}")
                else:
                    st.success("动作规范！")

                save_workout(exercise, 1, stats["count"], stats["duration"], cal, avg)
                os.unlink(tfile.name); os.unlink(out_path)

# ==================== 页面：课程 ====================

def page_courses():
    st.header("📚 训练课程")

    cols = st.columns(3)
    for i, c in enumerate(get_course_list()):
        with cols[i % 3]:
            diff_color = {"beginner": "🟢", "intermediate": "🟡", "advanced": "🔴"}
            st.markdown(f"""
            **{c['name']}**
            {c['description']}
            {diff_color.get(c['difficulty'], '')} {c['difficulty']} | ⏱ {c['duration']}min | 🔥 {c['calories']}kcal
            """)
            if st.button(f"开始", key=f"course_{c['key']}"):
                st.session_state.selected_course = c['key']

    if 'selected_course' in st.session_state:
        course = get_course(st.session_state.selected_course)
        if course:
            st.markdown("---")
            st.subheader(f"📋 {course.name}")
            st.write(course.description)

            for i, step in enumerate(course.exercises):
                rep_text = f"x{step.reps}" if step.reps > 0 else f"{step.duration}秒"
                rest_text = f" → 休息{step.rest_after}秒" if step.rest_after > 0 else ""
                st.write(f"{i+1}. **{step.name}** {rep_text}{rest_text}")

            if st.button("🏃 开始课程", type="primary"):
                st.session_state.course_running = True
                st.session_state.course_step = 0

    if st.session_state.get('course_running'):
        course = get_course(st.session_state.selected_course)
        step_idx = st.session_state.course_step

        if step_idx < len(course.exercises):
            step = course.exercises[step_idx]
            st.markdown(f"### 当前：{step.name}")

            timer_ph = st.empty()
            if step.duration > 0:
                for remaining in range(step.duration, 0, -1):
                    timer_ph.markdown(f"# ⏱ {remaining}秒")
                    time.sleep(1)
                timer_ph.markdown("# ✅ 完成！")
            else:
                timer_ph.markdown(f"# 目标：{step.reps}次")

            if step.rest_after > 0:
                st.info(f"休息 {step.rest_after}秒")
                rest_ph = st.empty()
                for r in range(step.rest_after, 0, -1):
                    rest_ph.markdown(f"# 😮‍💨 {r}秒")
                    time.sleep(1)

            if st.button("下一动作"):
                st.session_state.course_step += 1
                st.rerun()
        else:
            st.balloons()
            st.success(f"🎉 {course.name} 完成！")
            save_workout(course.name, len(course.exercises), 0, course.duration * 60, course.calories, 0)
            st.session_state.course_running = False

# ==================== 页面：记录 ====================

def page_history():
    st.header("📊 训练记录")

    streak = get_streak()
    st.metric("🔥 连续训练", f"{streak}天")

    history = get_workout_history(30)
    if history:
        import pandas as pd
        df = pd.DataFrame(history)
        df['created_at'] = pd.to_datetime(df['created_at'])

        st.subheader("近期训练")
        for h in history[:10]:
            st.write(f"- **{h['exercise']}** | {h['reps']}次 | {h['calories']}kcal | 评分{h['avg_score']} | {h['created_at'][:10]}")

        st.subheader("卡路里趋势")
        daily = df.groupby(df['created_at'].dt.date)['calories'].sum().reset_index()
        daily.columns = ['日期', '卡路里']
        st.bar_chart(daily.set_index('日期'))
    else:
        st.info("暂无训练记录，开始第一次训练吧！")

# ==================== 页面：身体数据 ====================

def page_body():
    st.header("📏 身体数据")

    with st.form("body_form"):
        c1, c2 = st.columns(2)
        with c1:
            weight = st.number_input("体重 (kg)", 30.0, 200.0, 70.0, 0.1)
            height = st.number_input("身高 (cm)", 100, 250, 170)
        with c2:
            body_fat = st.number_input("体脂率 (%)", 3.0, 60.0, 20.0, 0.1)
            muscle = st.number_input("肌肉量 (kg)", 20.0, 100.0, 30.0, 0.1)
        notes = st.text_input("备注")
        if st.form_submit_button("保存"):
            save_body_stats(weight, height, body_fat, muscle, notes)
            st.success("已保存")

    history = get_body_stats_history(10)
    if history:
        import pandas as pd
        df = pd.DataFrame(history)
        df['created_at'] = pd.to_datetime(df['created_at'])
        st.subheader("趋势")
        chart_data = df[['created_at', 'weight']].set_index('created_at')
        st.line_chart(chart_data)
        st.dataframe(df[['created_at', 'weight', 'body_fat', 'muscle_mass']].rename(
            columns={'created_at': '日期', 'weight': '体重', 'body_fat': '体脂率', 'muscle_mass': '肌肉量'}
        ))

# ==================== 页面：周报 ====================

def page_report():
    st.header("📈 训练周报")

    weekly = get_weekly_summary()
    if weekly:
        total_sessions = sum(w['sessions'] for w in weekly)
        total_cal = sum(w['total_calories'] or 0 for w in weekly)
        total_dur = sum(w['total_duration'] or 0 for w in weekly)

        c1, c2, c3 = st.columns(3)
        with c1: st.metric("训练次数", total_sessions)
        with c2: st.metric("总卡路里", f"{total_cal:.0f} kcal")
        with c3: st.metric("总时长", f"{total_dur//60}分钟")

        st.subheader("各项目详情")
        for w in weekly:
            with st.expander(f"{w['exercise']} ({w['sessions']}次)"):
                st.write(f"- 总次数：{w['total_reps'] or 0}")
                st.write(f"- 平均评分：{w['avg_score']:.0f}分" if w['avg_score'] else "- 平均评分：N/A")
                st.write(f"- 消耗卡路里：{w['total_calories']:.0f} kcal" if w['total_calories'] else "- 消耗：N/A")
    else:
        st.info("本周暂无训练记录")

    monthly = get_monthly_summary()
    if monthly:
        st.markdown("---")
        st.subheader("本月汇总")
        total_m = sum(m['sessions'] for m in monthly)
        cal_m = sum(m['total_calories'] or 0 for m in monthly)
        c1, c2 = st.columns(2)
        with c1: st.metric("本月训练", f"{total_m}次")
        with c2: st.metric("本月消耗", f"{cal_m:.0f} kcal")

# ==================== 页面：训练计划 ====================

def page_plans():
    st.header("📋 训练计划")

    plans = get_plan_list()
    cols = st.columns(2)
    for i, p in enumerate(plans):
        with cols[i % 2]:
            goal_icon = GOAL_LABELS.get(p['goal'], '')
            diff = {"beginner": "🟢 入门", "intermediate": "🟡 进阶", "advanced": "🔴 高级"}
            st.markdown(f"""
            ### {p['name']}
            {goal_icon} | {diff.get(p['difficulty'], '')} | {p['weeks']}周 | 每周{p['days']}天

            {p['desc']}
            """)
            if st.button(f"选择此计划", key=f"plan_{p['id']}"):
                st.session_state.active_plan = p['id']
                st.session_state.plan_week = 1
                st.rerun()

    if 'active_plan' in st.session_state:
        plan = get_plan(st.session_state.active_plan)
        if plan:
            st.markdown("---")
            st.subheader(f"📌 当前计划：{plan.name}")

            progress = get_plan_progress(plan.id)
            completed_days = set((p['week'], p['day']) for p in progress if p['completed'])

            for week in range(1, plan.weeks + 1):
                with st.expander(f"第 {week} 周", expanded=(week == st.session_state.get('plan_week', 1))):
                    for day_plan in plan.schedule:
                        is_done = (week, day_plan.day) in completed_days
                        icon = "✅" if is_done else "⬜"
                        st.markdown(f"**{icon} Day {day_plan.day} - {day_plan.notes}**")
                        for ex in day_plan.exercises:
                            rep = f"{ex['reps']}次" if ex['reps'] > 0 else f"{ex.get('duration', 30)}秒"
                            st.write(f"  - {ex['name']} {ex['sets']}组 x {rep}")

                        if not is_done:
                            if st.button(f"完成此训练", key=f"done_{week}_{day_plan.day}"):
                                mark_plan_day_done(plan.id, week, day_plan.day)
                                st.balloons()
                                st.success(f"第{week}周 Day{day_plan.day} 已完成！")
                                st.rerun()

            total_days = plan.weeks * len(plan.schedule)
            done_count = len(completed_days)
            st.progress(done_count / total_days if total_days > 0 else 0)
            st.write(f"进度：{done_count}/{total_days} 天")

            if st.button("切换计划"):
                del st.session_state.active_plan
                st.rerun()

# ==================== 页面：体测评估 ====================

def page_assessment():
    st.header("📏 体测评估")
    st.write("完成以下测试，系统将自动评估你的体能水平并推荐训练计划。")

    with st.form("assessment_form"):
        scores = {}
        for key, item in ASSESSMENTS.items():
            st.markdown(f"**{item.name}** - {item.description}")
            val = st.number_input(f"{item.name} ({item.unit})", 0.0, 999.0, 0.0, key=f"assess_{key}")
            scores[key] = val

        submitted = st.form_submit_button("📊 提交评估", type="primary")

    if submitted and any(v > 0 for v in scores.values()):
        results = {}
        for key, val in scores.items():
            if val > 0:
                level, comment = evaluate(ASSESSMENTS[key], val)
                results[key] = (level, comment)

        overall_level, overall_desc = get_overall_level(results)
        recommended = recommend_plan(results)

        st.markdown("---")
        st.subheader("📊 评估结果")

        # 综合评级
        level_colors = {"A": "🟢", "B": "🟡", "C": "🟠", "D": "🔴"}
        st.markdown(f"### {level_colors.get(overall_level, '')} 综合评级：{overall_level} - {overall_desc}")

        # 各项详情
        cols = st.columns(len(results))
        for i, (key, (level, comment)) in enumerate(results.items()):
            with cols[i]:
                item = ASSESSMENTS[key]
                st.metric(item.name, f"{scores[key]} {item.unit}")
                st.write(f"等级：**{level}**")
                st.caption(comment)

        # 推荐计划
        plan = get_plan(recommended)
        if plan:
            st.markdown("---")
            st.info(f"**推荐计划：{plan.name}**\n\n{plan.description}")
            if st.button("采纳此计划"):
                st.session_state.active_plan = recommended
                st.success("已设置为当前计划！请前往「训练计划」页面查看。")

        # 保存记录
        save_assessment(scores, overall_level, recommended)

        # 检查成就
        stats = get_achievement_stats()
        stats['assessments_done'] = len(get_assessment_history())
        new_achievements = check_achievements(stats)
        unlocked = get_unlocked_achievements()
        for aid in new_achievements:
            if aid not in unlocked:
                unlock_achievement(aid)
                ach = get_achievement(aid)
                if ach:
                    st.toast(f"🏆 解锁成就：{ach.icon} {ach.name}")

    # 历史记录
    history = get_assessment_history(5)
    if history:
        st.markdown("---")
        st.subheader("📜 历史体测")
        for h in history:
            with st.expander(f"{h['created_at'][:10]} - 综合评级 {h['overall_level']}"):
                c1, c2, c3, c4, c5 = st.columns(5)
                with c1: st.metric("上肢", f"{h['upper_strength'] or '-'}")
                with c2: st.metric("核心", f"{h['core_strength'] or '-'}")
                with c3: st.metric("下肢", f"{h['lower_strength'] or '-'}")
                with c4: st.metric("心肺", f"{h['cardio'] or '-'}")
                with c5: st.metric("柔韧", f"{h['flexibility'] or '-'}")

# ==================== 页面：成就系统 ====================

def page_achievements():
    st.header("🏆 成就系统")

    # 检查并解锁新成就
    stats = get_achievement_stats()
    new_achievements = check_achievements(stats)
    unlocked = get_unlocked_achievements()

    newly_unlocked = []
    for aid in new_achievements:
        if aid not in unlocked:
            unlock_achievement(aid)
            newly_unlocked.append(aid)
            unlocked.append(aid)

    if newly_unlocked:
        for aid in newly_unlocked:
            ach = get_achievement(aid)
            st.toast(f"🏆 新成就：{ach.icon} {ach.name}")

    # 统计概览
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("总训练次数", stats['total_workouts'])
    with c2: st.metric("连续训练", f"{stats['streak']}天")
    with c3: st.metric("总卡路里", f"{stats['total_calories']:.0f} kcal")
    with c4: st.metric("成就解锁", f"{len(unlocked)}/{len(ACHIEVEMENTS)}")

    st.markdown("---")

    # 成就展示
    categories = {
        "训练次数": ["first_workout", "workout_10", "workout_50", "workout_100"],
        "连续训练": ["streak_3", "streak_7", "streak_30"],
        "俯卧撑": ["pushup_50", "pushup_500"],
        "深蹲": ["squat_100", "squat_1000"],
        "动作评分": ["score_90", "score_perfect"],
        "卡路里": ["cal_1000", "cal_10000"],
        "课程": ["course_1", "course_10"],
        "体测": ["assess_1"],
    }

    for cat_name, aids in categories.items():
        st.subheader(f"{cat_name}")
        cols = st.columns(4)
        for i, aid in enumerate(aids):
            ach = get_achievement(aid)
            if ach:
                with cols[i % 4]:
                    is_unlocked = aid in unlocked
                    if is_unlocked:
                        st.markdown(f"""
                        ### {ach.icon}
                        **{ach.name}**
                        {ach.description}
                        ✅ 已解锁
                        """)
                    else:
                        st.markdown(f"""
                        ### 🔒
                        **{ach.name}**
                        {ach.condition_desc}
                        ❌ 未解锁
                        """)

# ==================== 主应用 ====================

# ==================== Keep风格首页 ====================

def page_dashboard():
    stats = get_achievement_stats()
    weekly = get_weekly_summary()
    streak = get_streak()
    total_cal = sum(w['total_calories'] or 0 for w in weekly) if weekly else 0
    total_mins = sum(w['total_duration'] or 0 for w in weekly) // 60 if weekly else 0
    total_sessions = sum(w['sessions'] or 0 for w in weekly) if weekly else 0

    cal_target = 400
    mins_target = 30
    sess_target = 3
    cal_pct = min(total_cal / cal_target * 100, 100)
    mins_pct = min(total_mins / mins_target * 100, 100)
    sess_pct = min(total_sessions / sess_target * 100, 100)
    overall_pct = int((cal_pct + mins_pct + sess_pct) / 3)

    # 顶部欢迎区
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;">
        <div style="display:flex;align-items:center;gap:12px;">
            <div style="width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,#10b981,#34d399);display:flex;align-items:center;justify-content:center;font-size:20px;color:white;">💪</div>
            <div>
                <div style="font-size:15px;font-weight:700;color:#1e293b;">启划健身 · 智能私教</div>
                <div style="font-size:11px;color:#94a3b8;">⚡ 已连续训练 {streak} 天</div>
            </div>
        </div>
        <div class="qh-tag qh-tag-green">V.LV 4</div>
    </div>
    """, unsafe_allow_html=True)

    # 三环能量区 + 今日目标
    st.markdown(f"""
    <div class="qh-card-lg" style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;">
        <div style="flex:1;padding-right:24px;">
            <div style="font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:16px;">
                <span style="color:#10b981;">🔥</span> 今日运动目标
            </div>
            <div style="display:flex;flex-direction:column;gap:12px;">
                <div style="display:flex;align-items:center;justify-content:space-between;">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <div style="width:8px;height:8px;border-radius:50%;background:#10b981;"></div>
                        <span style="font-size:13px;color:#64748b;font-weight:600;">消耗能量</span>
                    </div>
                    <span style="font-size:13px;font-weight:700;color:#1e293b;font-family:monospace;">{total_cal:.0f} / {cal_target} <span style="font-size:10px;color:#94a3b8;">kcal</span></span>
                </div>
                <div style="display:flex;align-items:center;justify-content:space-between;">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <div style="width:8px;height:8px;border-radius:50%;background:#0ea5e9;"></div>
                        <span style="font-size:13px;color:#64748b;font-weight:600;">训练时长</span>
                    </div>
                    <span style="font-size:13px;font-weight:700;color:#1e293b;font-family:monospace;">{total_mins} / {mins_target} <span style="font-size:10px;color:#94a3b8;">分钟</span></span>
                </div>
                <div style="display:flex;align-items:center;justify-content:space-between;">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <div style="width:8px;height:8px;border-radius:50%;background:#f97316;"></div>
                        <span style="font-size:13px;color:#64748b;font-weight:600;">今日打卡</span>
                    </div>
                    <span style="font-size:13px;font-weight:700;color:#1e293b;font-family:monospace;">{total_sessions} / {sess_target} <span style="font-size:10px;color:#94a3b8;">次</span></span>
                </div>
            </div>
        </div>
        <div class="qh-ring-container">
            <svg width="120" height="120">
                <circle cx="60" cy="60" r="52" fill="none" stroke="#f1f5f9" stroke-width="5"/>
                <circle cx="60" cy="60" r="42" fill="none" stroke="#f1f5f9" stroke-width="5"/>
                <circle cx="60" cy="60" r="32" fill="none" stroke="#f1f5f9" stroke-width="5"/>
                <circle cx="60" cy="60" r="52" fill="none" stroke="#10b981" stroke-width="5"
                    stroke-dasharray="{326.7}" stroke-dashoffset="{326.7 * (1 - cal_pct/100)}" stroke-linecap="round"/>
                <circle cx="60" cy="60" r="42" fill="none" stroke="#0ea5e9" stroke-width="5"
                    stroke-dasharray="{263.9}" stroke-dashoffset="{263.9 * (1 - mins_pct/100)}" stroke-linecap="round"/>
                <circle cx="60" cy="60" r="32" fill="none" stroke="#f97316" stroke-width="5"
                    stroke-dasharray="{201.1}" stroke-dashoffset="{201.1 * (1 - sess_pct/100)}" stroke-linecap="round"/>
            </svg>
            <div class="qh-ring-center">
                <div class="qh-ring-value">{overall_pct}%</div>
                <div class="qh-ring-label">已完成</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 四个快捷入口
    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px;">
        <div class="qh-card" style="text-align:center;cursor:pointer;padding:16px 8px;">
            <div style="font-size:28px;margin-bottom:6px;">🏋️</div>
            <div style="font-size:11px;font-weight:700;color:#64748b;">开始训练</div>
        </div>
        <div class="qh-card" style="text-align:center;cursor:pointer;padding:16px 8px;">
            <div style="font-size:28px;margin-bottom:6px;">📚</div>
            <div style="font-size:11px;font-weight:700;color:#64748b;">课程大厅</div>
        </div>
        <div class="qh-card" style="text-align:center;cursor:pointer;padding:16px 8px;">
            <div style="font-size:28px;margin-bottom:6px;">📋</div>
            <div style="font-size:11px;font-weight:700;color:#64748b;">训练计划</div>
        </div>
        <div class="qh-card" style="text-align:center;cursor:pointer;padding:16px 8px;">
            <div style="font-size:28px;margin-bottom:6px;">📏</div>
            <div style="font-size:11px;font-weight:700;color:#64748b;">体测评估</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 本周卡路里趋势
    st.markdown("""
    <div class="qh-card" style="margin-bottom:20px;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
            <div style="display:flex;align-items:center;gap:6px;">
                <span style="color:#10b981;font-weight:700;">📈</span>
                <span style="font-size:13px;font-weight:700;color:#1e293b;">周卡路里燃烧趋势</span>
            </div>
            <span style="font-size:10px;color:#94a3b8;font-family:monospace;">周目标 2500 kcal</span>
        </div>
        <div style="display:flex;align-items:flex-end;justify-content:space-between;height:80px;padding:0 8px;">
            <div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:4px;">
                <div style="width:16px;background:#e2e8f0;border-radius:4px 4px 0 0;height:40%;"></div>
                <span style="font-size:9px;color:#94a3b8;">周一</span>
            </div>
            <div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:4px;">
                <div style="width:16px;background:#e2e8f0;border-radius:4px 4px 0 0;height:65%;"></div>
                <span style="font-size:9px;color:#94a3b8;">周二</span>
            </div>
            <div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:4px;">
                <div style="width:16px;background:#e2e8f0;border-radius:4px 4px 0 0;height:25%;"></div>
                <span style="font-size:9px;color:#94a3b8;">周三</span>
            </div>
            <div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:4px;">
                <div style="width:16px;background:#e2e8f0;border-radius:4px 4px 0 0;height:45%;"></div>
                <span style="font-size:9px;color:#94a3b8;">周四</span>
            </div>
            <div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:4px;">
                <div style="width:16px;background:#e2e8f0;border-radius:4px 4px 0 0;height:75%;"></div>
                <span style="font-size:9px;color:#94a3b8;">周五</span>
            </div>
            <div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:4px;">
                <div style="width:16px;background:linear-gradient(to top,#10b981,#34d399);border-radius:4px 4px 0 0;height:52%;box-shadow:0 2px 6px rgba(16,185,129,0.2);"></div>
                <span style="font-size:9px;color:#10b981;font-weight:700;">周六</span>
            </div>
            <div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:4px;">
                <div style="width:16px;background:#e2e8f0;border-radius:4px 4px 0 0;height:5%;"></div>
                <span style="font-size:9px;color:#94a3b8;">周日</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 累计数据大卡
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="qh-metric-card">
            <div class="qh-metric-icon">🔥</div>
            <div class="qh-metric-value">{stats['total_calories']:.0f}</div>
            <div class="qh-metric-label">累计千卡</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="qh-metric-card">
            <div class="qh-metric-icon">💪</div>
            <div class="qh-metric-value">{stats['total_workouts']}</div>
            <div class="qh-metric-label">训练次数</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="qh-metric-card">
            <div class="qh-metric-icon">🏆</div>
            <div class="qh-metric-value">{len(get_unlocked_achievements())}</div>
            <div class="qh-metric-label">成就解锁</div>
        </div>
        """, unsafe_allow_html=True)

    # 最近训练记录
    history = get_workout_history(7)
    if history:
        st.markdown("""
        <div style="margin-top:20px;margin-bottom:12px;display:flex;align-items:center;gap:6px;">
            <span style="color:#0ea5e9;">📅</span>
            <span style="font-size:13px;font-weight:700;color:#1e293b;">近期训练记录</span>
        </div>
        """, unsafe_allow_html=True)
        for h in history[:5]:
            icon = {"俯卧撑": "💪", "深蹲": "🦵", "引体向上": "💪", "卷腹": "🧘", "平板支撑": "🧘", "弓步蹲": "🦵", "开合跳": "🤸", "波比跳": "🏋️", "高抬腿": "🏃"}.get(h['exercise'], "🏋️")
            st.markdown(f"""
            <div class="qh-card" style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;padding:14px 16px;">
                <div style="display:flex;align-items:center;gap:12px;">
                    <div style="width:40px;height:40px;border-radius:12px;background:#ecfdf5;display:flex;align-items:center;justify-content:center;font-size:18px;">{icon}</div>
                    <div>
                        <div style="font-size:13px;font-weight:700;color:#1e293b;">{h['exercise']}</div>
                        <div style="font-size:10px;color:#94a3b8;font-family:monospace;">{h['created_at'][:10]}</div>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:13px;font-weight:700;color:#1e293b;font-family:monospace;">{h['calories']:.0f} kcal</div>
                    <div style="font-size:10px;color:#94a3b8;">{h['reps']}次 · 评分{h['avg_score']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


def main():
    st.set_page_config(page_title="启划健身 · AI智能私教", page_icon="💪", layout="wide")

    page = st.sidebar.radio("导航", ["🏠 首页", "🏋️ 训练", "📚 课程", "📋 计划", "📏 体测", "🏆 成就", "📊 记录", "📏 身体数据", "📈 周报"])

    if page == "🏠 首页": page_dashboard()
    elif page == "🏋️ 训练": page_training()
    elif page == "📚 课程": page_courses()
    elif page == "📋 计划": page_plans()
    elif page == "📏 体测": page_assessment()
    elif page == "🏆 成就": page_achievements()
    elif page == "📊 记录": page_history()
    elif page == "📏 身体数据": page_body()
    elif page == "📈 周报": page_report()

if __name__ == "__main__":
    main()

# ==================== 开合跳分析 ====================

class JumpingJackCounter:
    def __init__(self):
        self.count = 0; self.state = "together"
    def update(self, lm, w, h):
        LW, RW, LA, RA = 15, 16, 27, 28
        lw, rw = px(lm, LW, w, h), px(lm, RW, w, h)
        la, ra = px(lm, LA, w, h), px(lm, RA, w, h)
        hand_dist = abs(lw[0] - rw[0]) / w
        foot_dist = abs(la[0] - ra[0]) / w
        spread = hand_dist > 0.3 and foot_dist > 0.15
        new_count = False
        if self.state == "together" and spread:
            self.state = "apart"
        elif self.state == "apart" and not spread:
            self.count += 1; new_count = True; self.state = "together"
        return {"lw": lw, "rw": rw, "la": la, "ra": ra,
                "count": self.count, "new_count": new_count, "spread": spread}

def draw_jumping_jack(frame, r):
    color = (0, 255, 0) if r["spread"] else (0, 255, 255)
    cv2.circle(frame, r["lw"], 8, color, -1); cv2.circle(frame, r["rw"], 8, color, -1)
    cv2.circle(frame, r["la"], 8, color, -1); cv2.circle(frame, r["ra"], 8, color, -1)
    cv2.putText(frame, f"Count:{r['count']}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    return frame
