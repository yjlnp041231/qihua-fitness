"""
羽毛球挥拍动作分析脚本
使用 MediaPipe PoseLandmarker 进行人体骨骼追踪，计算手臂伸展夹角并可视化
"""

import cv2
import mediapipe as mp
import numpy as np
import math
import sys
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import Image


def calculate_angle(a, b, c):
    """
    计算三个点组成的角度（以 b 为顶点）
    a, b, c: 各点的 (x, y) 坐标
    返回角度值（度）
    """
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    # 计算向量 ba 和 bc
    ba = a - b
    bc = c - b

    # 计算夹角的余弦值
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    # 限制在 [-1, 1] 范围内，避免浮点误差
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)

    # 计算角度（弧度转度）
    angle = np.arccos(cosine_angle)
    return np.degrees(angle)


def get_arm_landmarks(landmarks, side="right"):
    """
    获取指定侧的手臂关键点坐标
    side: "right" 或 "left"
    返回 (shoulder, elbow, wrist) 的 (x, y) 坐标
    """
    if side == "right":
        shoulder = (landmarks[12].x, landmarks[12].y)  # 右肩膀
        elbow = (landmarks[14].x, landmarks[14].y)     # 右手肘
        wrist = (landmarks[16].x, landmarks[16].y)     # 右手腕
    else:
        shoulder = (landmarks[11].x, landmarks[11].y)  # 左肩膀
        elbow = (landmarks[13].x, landmarks[13].y)     # 左手肘
        wrist = (landmarks[15].x, landmarks[15].y)     # 左手腕
    return shoulder, elbow, wrist


def calculate_arm_movement(landmarks_history):
    """
    计算手臂的运动幅度（用于自动选择动作幅度更大的一侧）
    """
    if len(landmarks_history) < 2:
        return 0

    movements = []
    for i in range(1, len(landmarks_history)):
        prev_wrist = landmarks_history[i-1]["wrist"]
        curr_wrist = landmarks_history[i]["wrist"]
        dist = math.sqrt((curr_wrist[0]-prev_wrist[0])**2 + (curr_wrist[1]-prev_wrist[1])**2)
        movements.append(dist)

    return sum(movements) / len(movements) if movements else 0


def process_video(input_path="input.mp4", output_path="output.mp4"):
    """
    处理视频文件，分析挥拍动作并生成标注视频
    """
    # 下载模型文件（如果不存在）
    model_path = "pose_landmarker.task"
    import os
    if not os.path.exists(model_path):
        print("正在下载 PoseLandmarker 模型...")
        import urllib.request
        url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task"
        urllib.request.urlretrieve(url, model_path)
        print("模型下载完成")

    # 创建 PoseLandmarker
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        num_poses=1
    )
    landmarker = vision.PoseLandmarker.create_from_options(options)

    # 打开视频文件
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"错误: 无法打开视频文件 {input_path}")
        sys.exit(1)

    # 获取视频属性
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"视频信息: {width}x{height}, {fps}FPS, 共{total_frames}帧")

    # 创建视频写入器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # 用于存储历史关键点（用于自动选择手臂侧）
    right_history = []
    left_history = []
    selected_side = None  # 在前30帧确定

    frame_count = 0
    timestamp_ms = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        timestamp_ms = int((frame_count - 1) * 1000 / fps)

        # 转换为 MediaPipe Image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # 进行姿态检测
        detection_result = landmarker.detect_for_video(mp_image, timestamp_ms)

        if detection_result.pose_landmarks:
            landmarks = detection_result.pose_landmarks[0]  # 获取第一个检测到的人

            # 获取双臂关键点
            right_shoulder, right_elbow, right_wrist = get_arm_landmarks(landmarks, "right")
            left_shoulder, left_elbow, left_wrist = get_arm_landmarks(landmarks, "left")

            # 存储历史
            right_history.append({"wrist": right_wrist})
            left_history.append({"wrist": left_wrist})

            # 前30帧后自动选择动作幅度更大的一侧
            if selected_side is None and frame_count >= 30:
                right_movement = calculate_arm_movement(right_history)
                left_movement = calculate_arm_movement(left_history)
                selected_side = "right" if right_movement >= left_movement else "left"
                print(f"自动选择: {selected_side.upper()} 手臂 (动作幅度更大)")

            # 如果还没确定，暂时用右侧
            if selected_side is None:
                current_side = "right"
            else:
                current_side = selected_side

            # 获取当前侧的关键点
            shoulder, elbow, wrist = get_arm_landmarks(landmarks, current_side)

            # 转换为像素坐标
            h, w, _ = frame.shape
            shoulder_px = (int(shoulder[0] * w), int(shoulder[1] * h))
            elbow_px = (int(elbow[0] * w), int(elbow[1] * h))
            wrist_px = (int(wrist[0] * w), int(wrist[1] * h))

            # 计算角度
            angle = calculate_angle(shoulder, elbow, wrist)

            # 绘制骨骼连线
            cv2.line(frame, shoulder_px, elbow_px, (0, 255, 0), 3)
            cv2.line(frame, elbow_px, wrist_px, (0, 255, 0), 3)

            # 绘制关键点
            for point in [shoulder_px, elbow_px, wrist_px]:
                cv2.circle(frame, point, 8, (0, 0, 255), -1)

            # 根据角度选择颜色
            if angle >= 160:
                color = (0, 255, 0)  # 绿色 - 挥拍展直
                status = "Extended"
            else:
                color = (0, 0, 255)  # 红色 - 弯曲
                status = "Bent"

            # 在手肘附近显示角度
            text = f"Angle: {angle:.1f}"
            text_pos = (elbow_px[0] - 50, elbow_px[1] - 30)
            cv2.putText(frame, text, text_pos,
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            # 在左上角显示状态
            cv2.putText(frame, f"Side: {current_side.upper()}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Status: {status}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # 写入输出帧
        out.write(frame)

        # 显示进度
        if frame_count % 30 == 0:
            progress = (frame_count / total_frames) * 100
            print(f"处理进度: {progress:.1f}% ({frame_count}/{total_frames})")

    # 释放资源
    cap.release()
    out.release()
    landmarker.close()

    print(f"\n处理完成! 输出文件: {output_path}")
    print(f"共处理 {frame_count} 帧")


if __name__ == "__main__":
    process_video()
