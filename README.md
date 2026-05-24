# 启划健身 · AI智能私教系统

基于 MediaPipe 姿态检测的 AI 健身分析系统，Keep 风格界面设计。

## 功能特性

### 🏋️ 训练分析
- 10种动作识别：深蹲/硬拉/俯卧撑/引体向上/卷腹/平板支撑/弓步蹲/开合跳/波比跳/高抬腿
- 实时摄像头分析 + 视频上传分析
- 动作评分系统（0-100分）
- 语音播报反馈

### 📚 课程系统
- 6套预设课程（HIIT/力量/核心/有氧/全身）
- 倒计时训练播放器
- 组间休息计时

### 📋 训练计划
- 4套周期化计划（燃脂/增肌/入门/柔韧）
- 按周按天推进，进度追踪

### 📏 体测评估
- 5项体能测试（上肢/核心/下肢/心肺/柔韧）
- 自动评级A-D，智能推荐训练计划

### 🏆 成就系统
- 18个成就徽章
- 训练次数/连续天数/动作评分等多维度解锁

### 📊 数据看板
- Keep风格Dashboard首页
- 三环能量环、周趋势图
- 训练历史、身体数据、周报统计

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行应用
```bash
streamlit run fitness_ai_coach.py
```

浏览器自动打开 `http://localhost:8501`

## 项目结构
```
badminton_ai/
├── fitness_ai_coach.py   # 主应用（Streamlit）
├── database.py           # SQLite数据模块
├── courses.py            # 课程系统
├── plans.py              # 训练计划
├── assessment.py         # 体测评估
├── achievements.py       # 成就系统
├── badminton_analyzer.py # 羽毛球挥拍分析（独立脚本）
├── requirements.txt      # 依赖列表
└── README.md             # 项目说明
```

## 技术栈
- **前端**: Streamlit + 自定义CSS
- **姿态检测**: MediaPipe PoseLandmarker
- **视频处理**: OpenCV
- **数据存储**: SQLite
- **语音播报**: pyttsx3

## 许可证
MIT License
