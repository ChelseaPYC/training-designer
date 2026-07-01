import streamlit as st
import requests
import json
import time
import base64
from pathlib import Path

# ============================================================
# 图片资源 - Base64 嵌入（每张 < 200KB，已压缩到 480px 宽度）
# ============================================================
def img_to_base64(filename):
    img_path = Path(__file__).parent / "images" / filename
    if img_path.exists():
        return base64.b64encode(img_path.read_bytes()).decode()
    return ""

FEATURE_IMAGES = {
    "outline": img_to_base64("feature-outline.png"),
    "ppt": img_to_base64("feature-ppt.png"),
    "assessment": img_to_base64("feature-assessment.png"),
    "practice": img_to_base64("feature-practice.png"),
}

# ============================================================
# 配置区：默认 API Key（通过 Streamlit Secrets 配置，用户无需手动设置）
# ============================================================
# 在 Streamlit Cloud 后台 Settings -> Secrets 中配置：
# DEEPSEEK_API_KEY = "sk-你的APIKey"
# 本地开发时可在 .streamlit/secrets.toml 中配置（已加入 .gitignore，不会上传）
DEFAULT_API_KEY = st.secrets.get("DEEPSEEK_API_KEY", "")

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="企业培训智能化平台",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# 常量定义
# ============================================================
MODULE_LABELS = {
    "blueprint": "培训课程大纲",
    "hands_on": "实操练习手册",
    "assessment": "考核试题库",
    "materials": "培训 PPT 课件",
    "transfer": "学习迁移计划",
    "evaluation": "效果评估方案"
}

MODULE_DESCRIPTIONS = {
    "blueprint": "结构化课程目录与学习目标",
    "hands_on": "场景化练习与案例分析",
    "assessment": "选择题、判断题等多元题型",
    "materials": "完整演示文稿，可直接使用",
    "transfer": "30天在岗实践计划",
    "evaluation": "Kirkpatrick四级评估框架"
}

MODULE_ICONS = {
    "blueprint": "📋",
    "hands_on": "🔧",
    "assessment": "🎯",
    "materials": "📑",
    "transfer": "🔄",
    "evaluation": "📊"
}

MODULE_TAGS = {
    "blueprint": "智能生成",
    "hands_on": "实战导向",
    "assessment": "多维度",
    "materials": "一键输出",
    "transfer": "体系化",
    "evaluation": "数据驱动"
}

# ============================================================
# 自定义 CSS 样式 - TrainMind 风格
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');
    
    /* ===== 全局基础 ===== */
    :root {
        --primary-color: #4f46e5 !important;
        --st-primary-color: #4f46e5 !important;
    }
    * {
        font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    body, .stApp {
        background: #0a0e17 !important;
        color: white;
    }
    
    /* ===== 强制覆盖 Streamlit 主题色（按钮、滑块等） ===== */
    .stApp [data-testid="stSidebar"] { background: rgba(10,14,23,0.95) !important; }
    
    /* Primary 按钮 - 全局蓝紫色 */
    .stButton button[kind="primary"],
    .stButton button[data-testid="baseButton-primary"],
    .stButton > button[data-testid="baseButton-primary"],
    .stApp .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 16px rgba(79, 70, 229, 0.35) !important;
    }
    .stButton button[kind="primary"]:hover,
    .stButton button[data-testid="baseButton-primary"]:hover {
        background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%) !important;
        box-shadow: 0 6px 22px rgba(79, 70, 229, 0.45) !important;
    }
    .stButton button[kind="primary"]:disabled,
    .stButton button[data-testid="baseButton-primary"]:disabled {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        opacity: 0.6 !important;
        cursor: not-allowed !important;
    }
    
    /* Select Slider - 强制全局蓝紫色（覆盖所有内部元素） */
    [data-baseweb="slider"] [role="slider"] {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        border: 2px solid #0a0e17 !important;
        box-shadow: 0 0 0 1px #4f46e5, 0 2px 8px rgba(79, 70, 229, 0.4) !important;
    }
    /* Thumb value label (the number above the slider) */
    [data-baseweb="slider"] [data-testid="stThumbValue"] {
        color: #818cf8 !important;
        font-weight: 700 !important;
    }
    [data-baseweb="slider"] [data-testid="stThumbValue"] * {
        color: #818cf8 !important;
    }
    /* Slider track - filled portion */
    [data-baseweb="slider"] [role="progressbar"],
    [data-baseweb="slider"] [data-testid="stSliderActiveTrack"],
    [data-baseweb="slider"] > div > div > div > div:first-child {
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%) !important;
    }
    /* Slider track - unfilled portion */
    [data-baseweb="slider"] [data-testid="stSliderInactiveTrack"],
    [data-baseweb="slider"] > div > div > div > div:last-child {
        background: rgba(255,255,255,0.12) !important;
    }
    /* All slider child divs that look like rails */
    [data-baseweb="slider"] div[style*="background-color"] {
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%) !important;
    }
    /* Slider min/max labels */
    [data-baseweb="slider"] [data-testid="stTickBarMin"],
    [data-baseweb="slider"] [data-testid="stTickBarMax"] {
        color: rgba(255,255,255,0.5) !important;
    }
    /* Number markers under slider (1, 2, 3 ... 10) */
    [data-baseweb="slider"] [data-testid="stTickBar"] span,
    [data-baseweb="slider"] [data-testid="stTickBar"] {
        color: rgba(199, 210, 254, 0.7) !important;
    }
    
    .main .block-container {
        padding: 0 1rem 2rem 1rem;
        max-width: 100%;
        background: transparent;
    }
    
    /* ===== 隐藏 Streamlit 默认元素 ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header {visibility: hidden;}
    
    /* ===== 顶部导航栏 ===== */
    .nav-bar {
        background: rgba(10, 14, 23, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 0.75rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: -1rem -1rem 0 -1rem;
        position: sticky;
        top: 0;
        z-index: 100;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .nav-brand {
        font-size: 1.25rem;
        font-weight: 800;
        color: white;
        letter-spacing: 0.02em;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .nav-brand::before {
        content: '';
        width: 28px;
        height: 28px;
        background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
        border-radius: 8px;
        display: inline-block;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.35);
    }
    .nav-brand span {
        background: linear-gradient(135deg, #ffffff 0%, #c7d2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .nav-btn {
        background: transparent;
        border: 1px solid rgba(129, 140, 248, 0.3);
        color: #c7d2fe;
        padding: 0.4rem 1rem;
        border-radius: 6px;
        font-size: 0.8rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    .nav-btn:hover {
        background: rgba(129, 140, 248, 0.12);
        border-color: rgba(129, 140, 248, 0.5);
    }
    
    /* ===== Hero 区域 ===== */
    .hero-section {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        padding: 4rem 2rem 5rem 2rem;
        color: white;
        text-align: left;
        position: relative;
        overflow: hidden;
        margin: 0 -1rem;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 80%;
        height: 200%;
        background: radial-gradient(circle at 70% 40%, rgba(79, 70, 229, 0.25) 0%, rgba(6, 182, 212, 0.1) 40%, transparent 70%);
        pointer-events: none;
    }
    .hero-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        max-width: 1200px;
        margin: 0 auto;
        position: relative;
        gap: 4rem;
    }
    .hero-content {
        flex: 1;
        min-width: 0;
    }
    .hero-graphic {
        flex: 0 0 480px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .hero-eyebrow {
        display: inline-block;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #818cf8;
        padding: 0.4rem 0.85rem;
        background: rgba(79, 70, 229, 0.12);
        border: 1px solid rgba(129, 140, 248, 0.25);
        border-radius: 999px;
        margin-bottom: 1.25rem;
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 1.25rem;
        line-height: 1.2;
        color: white;
        position: relative;
        letter-spacing: -0.03em;
        text-shadow: 0 0 40px rgba(79, 70, 229, 0.3);
        white-space: nowrap;
    }
    .hero-title .highlight {
        background: linear-gradient(135deg, #818cf8 0%, #c4b5fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: rgba(199, 210, 254, 0.8);
        font-weight: 400;
        line-height: 1.8;
        max-width: 520px;
        position: relative;
        margin-bottom: 0.5rem;
    }
    .hero-buttons {
        margin-top: 1.75rem;
        display: flex;
        gap: 1rem;
        position: relative;
    }
    .hero-stats {
        margin-top: 2.5rem;
        display: flex;
        align-items: center;
        gap: 1.5rem;
        position: relative;
    }
    .hero-stat {
        display: flex;
        flex-direction: column;
    }
    .hero-stat-num {
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #818cf8 0%, #c4b5fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
    }
    .hero-stat-label {
        font-size: 0.75rem;
        color: rgba(255,255,255,0.45);
        margin-top: 0.2rem;
    }
    .hero-stat-divider {
        width: 1px;
        height: 32px;
        background: rgba(129, 140, 248, 0.2);
    }
    .hero-btn-primary {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        padding: 0.85rem 2rem;
        border-radius: 10px;
        font-size: 0.95rem;
        font-weight: 500;
        border: none;
        cursor: pointer;
        transition: all 0.2s;
        box-shadow: 0 4px 16px rgba(79, 70, 229, 0.35);
        text-decoration: none;
        display: inline-flex;
        align-items: center;
    }
    .hero-btn-primary:hover {
        background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%);
        box-shadow: 0 6px 22px rgba(79, 70, 229, 0.45);
        transform: translateY(-1px);
    }
    .hero-btn-secondary {
        background: rgba(255,255,255,0.05);
        color: rgba(255,255,255,0.85);
        padding: 0.85rem 2rem;
        border-radius: 10px;
        font-size: 0.95rem;
        font-weight: 500;
        border: 1px solid rgba(255,255,255,0.15);
        cursor: pointer;
        transition: all 0.2s;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
    }
    .hero-btn-secondary:hover {
        border-color: rgba(255,255,255,0.3);
        background: rgba(255,255,255,0.1);
        color: white;
    }
    
    /* ===== 三步流程 ===== */
    .steps-section {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.8) 0%, rgba(10, 14, 23, 0.95) 100%);
        padding: 3rem 2rem;
        margin: 0 -1rem;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .steps-header {
        text-align: left;
        max-width: 1200px;
        margin: 0 auto 2rem auto;
    }
    .steps-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: white;
        margin-bottom: 0.5rem;
        padding-left: 1rem;
        border-left: 4px solid #4f46e5;
    }
    .steps-subtitle {
        font-size: 0.9rem;
        color: rgba(255,255,255,0.5);
        padding-left: 1.25rem;
    }
    .steps-container {
        display: flex;
        align-items: stretch;
        gap: 0;
        max-width: 1000px;
        margin: 0 auto;
    }
    .step-card {
        flex: 1;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 1.75rem;
        transition: all 0.2s;
        text-align: center;
        position: relative;
    }
    .step-card:hover {
        background: rgba(255,255,255,0.08);
        border-color: rgba(129, 140, 248, 0.3);
        transform: translateY(-2px);
    }
    .step-arrow {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        flex-shrink: 0;
    }
    .step-arrow svg {
        width: 28px;
        height: 28px;
        color: rgba(129, 140, 248, 0.6);
    }
    .step-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 44px;
        height: 44px;
        background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
        color: white;
        border-radius: 12px;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 1rem;
        box-shadow: 0 4px 16px rgba(79, 70, 229, 0.35);
    }
    .step-name {
        font-size: 1.05rem;
        font-weight: 600;
        color: white;
        margin-bottom: 0.5rem;
    }
    .step-desc {
        font-size: 0.8rem;
        color: rgba(255,255,255,0.55);
        line-height: 1.6;
    }
    
    /* ===== 功能模块展示 - 左右交替布局 ===== */
    .features-section {
        background: linear-gradient(180deg, rgba(10, 14, 23, 0.95) 0%, rgba(15, 23, 42, 0.9) 100%);
        padding: 4rem 2rem;
        margin: 0 -1rem;
    }
    .features-header {
        text-align: left;
        max-width: 1200px;
        margin: 0 auto 2.5rem auto;
    }
    .features-title {
        font-size: 1.7rem;
        font-weight: 700;
        color: white;
        margin-bottom: 0.5rem;
        padding-left: 1rem;
        border-left: 4px solid #4f46e5;
    }
    .features-subtitle {
        font-size: 0.95rem;
        color: rgba(255,255,255,0.5);
        max-width: 600px;
        margin: 0;
        padding-left: 1.25rem;
        line-height: 1.6;
    }
    .feature-row {
        display: flex;
        align-items: center;
        gap: 3rem;
        margin-bottom: 2rem;
        max-width: 1200px;
        margin-left: auto;
        margin-right: auto;
    }
    .feature-row.reverse {
        flex-direction: row-reverse;
    }
    .feature-content {
        flex: 1;
        min-width: 0;
        text-align: left;
    }
    .feature-tag {
        display: inline-block;
        padding: 0.3rem 0.75rem;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        background: rgba(129, 140, 248, 0.12);
        color: #c7d2fe;
    }
    .feature-name {
        font-size: 1.35rem;
        font-weight: 700;
        color: white;
        margin-bottom: 0.75rem;
    }
    .feature-desc {
        font-size: 0.9rem;
        color: rgba(255,255,255,0.55);
        line-height: 1.8;
    }
    .feature-preview {
        flex: 1;
        min-width: 0;
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.08);
        background: rgba(255,255,255,0.03);
    }
    .feature-preview img {
        width: 100%;
        height: auto;
        display: block;
        transition: transform 0.3s;
    }
    .feature-row:hover .feature-preview img {
        transform: scale(1.03);
    }
    
    /* ===== 工作区 ===== */
    .workspace-section {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.9) 0%, rgba(10, 14, 23, 0.95) 100%);
        padding: 3rem 2rem;
        margin: 0 -1rem;
        min-height: auto;
        border-top: 1px solid rgba(255,255,255,0.05);
    }
    .workspace-header {
        text-align: left;
        max-width: 1200px;
        margin: 0 auto 2rem auto;
    }
    .workspace-title {
        font-size: 1.7rem;
        font-weight: 700;
        color: white;
        margin-bottom: 0.5rem;
        padding-left: 1rem;
        border-left: 4px solid #4f46e5;
        background: linear-gradient(90deg, rgba(79, 70, 229, 0.15) 0%, transparent 100%);
    }
    .workspace-subtitle {
        font-size: 0.9rem;
        color: rgba(255,255,255,0.5);
        padding-left: 1.25rem;
    }
    .workspace-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        max-width: 1200px;
        margin: 0 auto;
    }

    /* 左侧输入区 - 统一蓝紫高端风格 */
    .input-panel {
        background: linear-gradient(180deg, rgba(79, 70, 229, 0.08) 0%, rgba(124, 58, 237, 0.05) 100%), rgba(255,255,255,0.03);
        border: 1px solid rgba(129, 140, 248, 0.2);
        border-radius: 20px;
        padding: 1.75rem;
        height: 100%;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 24px rgba(79, 70, 229, 0.08);
    }
    .input-panel::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #4f46e5 0%, #7c3aed 100%);
    }
    .input-panel-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: white;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        border-bottom: 1px solid rgba(129, 140, 248, 0.15);
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .input-panel-title .icon {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 1.25rem;
    }
    .form-label {
        font-size: 0.78rem;
        font-weight: 500;
        color: rgba(255,255,255,0.75);
        margin-bottom: 0.4rem;
    }
    .form-label strong {
        color: #818cf8;
        font-weight: 600;
    }
    .form-input {
        margin-bottom: 1rem;
    }
    .form-hint {
        font-size: 0.72rem;
        color: rgba(255,255,255,0.35);
        margin-top: 0.2rem;
    }

    /* 右侧预览区 - 与左侧输入区风格完全统一 */
    .preview-panel {
        background: linear-gradient(180deg, rgba(79, 70, 229, 0.08) 0%, rgba(124, 58, 237, 0.05) 100%), rgba(255,255,255,0.03);
        border: 1px solid rgba(129, 140, 248, 0.2);
        border-radius: 20px;
        padding: 1.75rem;
        height: 100%;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 24px rgba(79, 70, 229, 0.08);
    }
    .preview-panel::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #4f46e5 0%, #7c3aed 100%);
    }
    .preview-panel-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: white;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        border-bottom: 1px solid rgba(129, 140, 248, 0.15);
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .preview-panel-title .icon {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 1.25rem;
    }
    .preview-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.6rem;
        display: flex;
        align-items: center;
        gap: 0.9rem;
        transition: all 0.2s;
    }
    .preview-card:hover {
        background: rgba(255,255,255,0.06);
    }
    .preview-card.selected {
        border-color: rgba(129, 140, 248, 0.5);
        background: rgba(79, 70, 229, 0.1);
    }
    .preview-icon {
        font-size: 1.1rem;
        width: 34px;
        height: 34px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, rgba(129, 140, 248, 0.2) 0%, rgba(192, 132, 252, 0.15) 100%);
        border-radius: 8px;
        flex-shrink: 0;
    }
    .preview-info {
        flex: 1;
    }
    .preview-name {
        font-size: 0.85rem;
        font-weight: 500;
        color: white;
        margin-bottom: 0.15rem;
    }
    .preview-desc {
        font-size: 0.72rem;
        color: rgba(255,255,255,0.45);
    }
    
    /* ===== 结果展示区 ===== */
    .results-section {
        background: rgba(10, 14, 23, 0.8);
        padding: 2rem 2rem;
        margin: 0 -1rem;
    }
    .result-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    
    /* ===== 页脚 ===== */
    .footer-section {
        background: rgba(10, 14, 23, 0.95);
        padding: 2rem 2rem 1.5rem 2rem;
        margin: 0 -1rem;
        border-top: 1px solid rgba(255,255,255,0.06);
    }
    .footer-brand {
        font-size: 1rem;
        font-weight: 600;
        background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.4rem;
    }
    .footer-tagline {
        font-size: 0.75rem;
        color: rgba(255,255,255,0.4);
        margin-bottom: 1.25rem;
    }
    .footer-links {
        display: flex;
        justify-content: center;
        gap: 1.5rem;
        margin-bottom: 1.25rem;
        flex-wrap: wrap;
    }
    .footer-links a {
        color: rgba(255,255,255,0.45);
        font-size: 0.75rem;
        text-decoration: none;
        transition: color 0.2s;
    }
    .footer-links a:hover {
        color: #818cf8;
    }
    .footer-column-title {
        display: none;
    }
    .footer-link {
        display: none;
    }
    .footer-bottom {
        margin-top: 1.5rem;
        padding-top: 1.25rem;
        border-top: 1px solid rgba(255,255,255,0.06);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .footer-copyright {
        font-size: 0.7rem;
        color: rgba(255,255,255,0.25);
    }
    
    /* ===== 设置弹窗 ===== */
    .settings-overlay {
        background: rgba(0,0,0,0.6);
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 200;
    }
    .settings-panel {
        background: rgba(15, 23, 42, 0.95);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.4);
        max-width: 400px;
        margin: 100px auto;
    }
    
    /* ===== 进度条 ===== */
    .progress-container {
        background: rgba(255,255,255,0.1);
        border-radius: 999px;
        height: 6px;
        overflow: hidden;
        margin: 1rem 0;
    }
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #4f46e5, #7c3aed);
        border-radius: 999px;
        transition: width 0.5s ease;
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stMultiselect > div > div > div {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: white !important;
        border-radius: 8px !important;
    }
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: rgba(255,255,255,0.35) !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > div:focus,
    .stMultiselect > div > div > div:focus {
        border-color: rgba(129, 140, 248, 0.5) !important;
        box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.15) !important;
    }
    /* Streamlit 内置 Slider 组件 - 通用主题色覆盖 */
    .stSlider > div > div {
        background: rgba(255,255,255,0.1) !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        background: rgba(255,255,255,0.06);
        padding: 0.4rem;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        font-size: 0.85rem;
        color: rgba(255,255,255,0.6);
    }
    .stTabs [aria-selected="true"] {
        background: rgba(79, 70, 229, 0.25) !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(79, 70, 229, 0.2);
    }
    
    /* ===== 响应式 ===== */
    @media (max-width: 1024px) {
        .features-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        .workspace-grid {
            grid-template-columns: 1fr;
        }
        .hero-graphic {
            flex: 0 0 360px;
        }
    }
    @media (max-width: 768px) {
        .hero-container {
            flex-direction: column;
            text-align: center;
            gap: 2rem;
        }
        .hero-graphic {
            display: none;
        }
        .hero-title {
            font-size: 2.2rem;
        }
        .hero-subtitle {
            margin: 0 auto;
        }
        .hero-buttons {
            justify-content: center;
        }
        .steps-container {
            flex-direction: column;
            gap: 1rem;
        }
        .step-arrow {
            transform: rotate(90deg);
            width: auto;
            height: 32px;
        }
        .features-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 辅助函数
# ============================================================
def call_deepseek(prompt, api_key, max_tokens=4000):
    """调用 DeepSeek API 生成内容"""
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是产品设计培训专家，擅长为企业软件/硬件产品编写专业的培训内容。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            },
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"❌ API 调用失败（状态码 {response.status_code}）：{response.text}"
    except Exception as e:
        return f"❌ API 调用出错：{str(e)}"

def build_prompt(module, product_name, product_type, training_roles, training_days, product_doc=""):
    """根据模块类型和用户输入构建提示词"""
    
    base_info = f"""
产品名称：{product_name}
产品类型：{product_type}
培训对象：{', '.join(training_roles)}
培训周期：{training_days}天
"""
    
    if product_doc:
        base_info += f"\n产品文档：\n{product_doc}"
    
    prompts = {
        "blueprint": f"""
{base_info}

请生成一份完整的产品培训蓝图，包含以下内容：

1. **产品定位**：核心价值主张、目标客户、竞争优势
2. **模块全景图**：产品功能模块结构（用层级列表展示）
3. **场景串讲脚本**：3-5个典型使用场景的讲解脚本
4. **术语表**：20-30个关键术语解释
5. **常见问题FAQ**：15-20个学员常见问题及标准答案
6. **知识点考核**：每个模块配备3-5个考核点

输出格式要求：
- 使用Markdown格式
- 结构清晰，层次分明
- 可直接用于培训
""",
        
        "hands_on": f"""
{base_info}

请根据培训对象的岗位等级，生成实操任务设计：

**岗位等级判断规则**：
- L3（深度实操）：实施、运维、技术支持 → 需要完整的实操任务包
- L2（基础实操）：销售、客户成功、售前 → 需要演示操作任务
- L1（无需实操）：市场、行政、财务 → 输出"产品价值速览卡"

请为每个L3/L2岗位生成：
- 实操任务清单（3-5个任务）
- 每个任务的环境准备
- 操作步骤详解
- 预期结果
- 常见错误及排查
- 评分标准

输出格式要求：
- 使用Markdown格式
- 任务描述清晰可操作
- 包含评分标准
""",
        
        "assessment": f"""
{base_info}

请生成一套完整的考核系统，包含以下内容：

1. **场景分析题**：3-5个真实工作场景，要求学员分析并给出解决方案
2. **实操演练任务**：对应培训蓝图中知识点考核的实操部分
3. **模拟答辩题目**：10-15个答辩题目，用于检验学员理解深度

每个考核项包含：
- 题目描述
- 考察要点
- 评分标准
- 参考答案

输出格式要求：
- 使用Markdown格式
- 题目具有实际工作场景
- 评分标准客观可操作
""",
        
        "materials": f"""
{base_info}

请生成完整的培训素材包，包含以下材料的大纲和内容框架：

1. **PPT大纲**：完整的幻灯片结构（章节+每页要点）
2. **讲师手册**：每页PPT的讲解要点、时间分配、互动提示
3. **学员练习册**：课后练习题目、案例分析、实操记录表
4. **速查卡**：A4纸大小，包含核心功能快捷键、常用操作流程图

输出格式要求：
- 使用Markdown格式
- 每个材料独立成章
- 可直接交给设计师或讲师使用
""",
        
        "transfer": f"""
{base_info}

请生成一份{training_days}天学习迁移计划，基于70-20-10学习模型：

**70% 在岗实践**：
- 熟悉环境，完成基础配置
- 独立完成小任务
- 独立完成中等任务
- 能够指导他人

**20% 向他人学习**：
- 导师分配
- 同伴学习小组
- 每周分享会

**10% 正式学习**：
- 复习培训材料
- 在线课程推荐
- 相关证书考试

输出格式要求：
- 使用Markdown格式
- 每天/每周的任务明确
- 包含检查点和验收标准
""",
        
        "evaluation": f"""
{base_info}

请生成基于Kirkpatrick四级模型的效果评估框架：

**Level 1 - 满意度评估**：
- 培训反馈问卷（10-15个问题）
- 净推荐值(NPS)调查

**Level 2 - 学习成果评估**：
- 培训前后测试题目（15-20题）
- 实操考核评分表

**Level 3 - 行为改变评估**：
- 行为观察表
- 主管评价问卷

**Level 4 - 业务结果评估**：
- ROI计算模型
- 关键业务指标(KPI)跟踪表

输出格式要求：
- 使用Markdown格式
- 每个层级包含具体的评估工具
- 包含数据分析模板
"""
    }
    
    return prompts.get(module, "模块提示词未定义")

# ============================================================
# Session State 初始化
# ============================================================
if "api_key" not in st.session_state:
    st.session_state.api_key = DEFAULT_API_KEY
if "show_settings" not in st.session_state:
    st.session_state.show_settings = False
if "product_name" not in st.session_state:
    st.session_state.product_name = ""
if "product_type" not in st.session_state:
    st.session_state.product_type = "软件"
if "training_roles" not in st.session_state:
    st.session_state.training_roles = []
if "training_days" not in st.session_state:
    st.session_state.training_days = 3
if "product_doc" not in st.session_state:
    st.session_state.product_doc = ""
if "module_selection" not in st.session_state:
    st.session_state.module_selection = {
        "blueprint": True,
        "hands_on": True,
        "assessment": True,
        "materials": True,
        "transfer": True,
        "evaluation": True
    }
if "generated_content" not in st.session_state:
    st.session_state.generated_content = {}
if "generation_complete" not in st.session_state:
    st.session_state.generation_complete = False
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False
if "show_workspace" not in st.session_state:
    st.session_state.show_workspace = False
if "scroll_to_workspace" not in st.session_state:
    st.session_state.scroll_to_workspace = False

# ============================================================
# 顶部导航栏
# ============================================================
st.markdown('<div id="top" style="position: absolute; top: 0; left: 0; width: 0; height: 0;"></div>', unsafe_allow_html=True)
nav_cols = st.columns([6, 1])
with nav_cols[0]:
    st.markdown('<div class="nav-brand"><span>企业培训智能化平台</span></div>', unsafe_allow_html=True)

# ============================================================
# Hero 区域 - 配图 + 跳转按钮
# ============================================================
st.html("""
<div class="hero-section">
    <div class="hero-container">
        <div class="hero-content">
            <div class="hero-eyebrow">AI-Powered Training Design</div>
            <h1 class="hero-title">从产品到培训，<span class="highlight">一步到位</span></h1>
            <div class="hero-subtitle">只需输入产品信息，描述核心功能与场景，即可自动生成全套培训方案，从蓝图到1V1点评，让产品培训事半功倍。</div>
            <div class="hero-buttons">
                <a href="#workspace" class="hero-btn-primary">立即体验</a>
                <a href="#features" class="hero-btn-secondary">了解功能</a>
            </div>
            <div class="hero-stats">
                <div class="hero-stat">
                    <div class="hero-stat-num">6+</div>
                    <div class="hero-stat-label">输出模块</div>
                </div>
                <div class="hero-stat-divider"></div>
                <div class="hero-stat">
                    <div class="hero-stat-num">10天</div>
                    <div class="hero-stat-label">培训周期</div>
                </div>
                <div class="hero-stat-divider"></div>
                <div class="hero-stat">
                    <div class="hero-stat-num">3分钟</div>
                    <div class="hero-stat-label">生成全套方案</div>
                </div>
            </div>
        </div>
        <div class="hero-graphic">
            <svg viewBox="0 0 480 320" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:480px;height:auto;display:block;filter:drop-shadow(0 30px 60px rgba(0,0,0,0.5));">
                <defs>
                    <linearGradient id="dash-board-bg" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#1e1b4b;stop-opacity:0.95"/>
                        <stop offset="100%" style="stop-color:#312e81;stop-opacity:0.85"/>
                    </linearGradient>
                    <linearGradient id="dash-card" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:rgba(255,255,255,0.14)"/>
                        <stop offset="100%" style="stop-color:rgba(255,255,255,0.05)"/>
                    </linearGradient>
                    <linearGradient id="dash-accent" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#4f46e5"/>
                        <stop offset="100%" style="stop-color:#7c3aed"/>
                    </linearGradient>
                </defs>
                <rect width="480" height="320" rx="24" fill="url(#dash-board-bg)" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
                <rect x="24" y="24" width="432" height="48" rx="12" fill="url(#dash-card)"/>
                <circle cx="52" cy="48" r="10" fill="url(#dash-accent)"/>
                <rect x="72" y="42" width="140" height="8" rx="4" fill="rgba(255,255,255,0.35)"/>
                <rect x="72" y="54" width="100" height="5" rx="2.5" fill="rgba(255,255,255,0.15)"/>
                <rect x="360" y="40" width="80" height="16" rx="8" fill="rgba(79,70,229,0.3)"/>
                <rect x="24" y="88" width="200" height="208" rx="16" fill="url(#dash-card)"/>
                <rect x="44" y="112" width="100" height="8" rx="4" fill="rgba(255,255,255,0.4)"/>
                <rect x="44" y="132" width="160" height="4" rx="2" fill="rgba(255,255,255,0.12)"/>
                <rect x="44" y="156" width="14" height="14" rx="4" fill="url(#dash-accent)"/>
                <rect x="66" y="160" width="120" height="5" rx="2.5" fill="rgba(255,255,255,0.25)"/>
                <rect x="44" y="184" width="14" height="14" rx="4" fill="url(#dash-accent)" opacity="0.7"/>
                <rect x="66" y="188" width="130" height="5" rx="2.5" fill="rgba(255,255,255,0.25)"/>
                <rect x="44" y="212" width="14" height="14" rx="4" fill="url(#dash-accent)" opacity="0.5"/>
                <rect x="66" y="216" width="110" height="5" rx="2.5" fill="rgba(255,255,255,0.25)"/>
                <rect x="44" y="240" width="14" height="14" rx="4" fill="rgba(255,255,255,0.15)"/>
                <rect x="66" y="244" width="125" height="5" rx="2.5" fill="rgba(255,255,255,0.25)"/>
                <rect x="240" y="88" width="216" height="120" rx="16" fill="url(#dash-card)"/>
                <rect x="264" y="116" width="120" height="8" rx="4" fill="rgba(255,255,255,0.35)"/>
                <rect x="264" y="134" width="168" height="4" rx="2" fill="rgba(255,255,255,0.12)"/>
                <rect x="264" y="146" width="150" height="4" rx="2" fill="rgba(255,255,255,0.12)"/>
                <rect x="264" y="158" width="140" height="4" rx="2" fill="rgba(255,255,255,0.12)"/>
                <rect x="264" y="180" width="90" height="10" rx="5" fill="url(#dash-accent)"/>
                <rect x="264" y="180" width="60" height="10" rx="5" fill="rgba(255,255,255,0.1)"/>
                <rect x="240" y="224" width="216" height="72" rx="16" fill="url(#dash-card)"/>
                <circle cx="290" cy="260" r="28" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="6"/>
                <circle cx="290" cy="260" r="28" fill="none" stroke="url(#dash-accent)" stroke-width="6" stroke-dasharray="110 176" stroke-linecap="round"/>
                <text x="290" y="256" font-size="16" font-weight="700" fill="white" text-anchor="middle" font-family="system-ui,sans-serif">68%</text>
                <text x="290" y="272" font-size="8" fill="rgba(255,255,255,0.4)" text-anchor="middle" font-family="system-ui,sans-serif">完成度</text>
                <rect x="350" y="246" width="90" height="8" rx="4" fill="rgba(255,255,255,0.12)"/>
                <rect x="350" y="258" width="70" height="6" rx="3" fill="rgba(255,255,255,0.08)"/>
                <rect x="350" y="270" width="80" height="6" rx="3" fill="rgba(255,255,255,0.08)"/>
            </svg>
        </div>
    </div>
</div>
""")

# 跳转锚点占位
st.markdown("<div id='workspace-anchor'></div>", unsafe_allow_html=True)

# ============================================================
# 三步流程
# ============================================================
st.html("""
<div class="steps-section">
    <div class="steps-header">
        <div class="steps-title">三步生成培训方案</div>
        <div class="steps-subtitle">从输入到输出，全程自动化智能化</div>
    </div>
    <div class="steps-container">
        <div class="step-card">
            <div class="step-number">1</div>
            <div class="step-name">输入产品信息</div>
            <div class="step-desc">填写产品名称、核心功能与目标人群</div>
        </div>
        <div class="step-arrow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </div>
        <div class="step-card">
            <div class="step-number">2</div>
            <div class="step-name">选择培训场景</div>
            <div class="step-desc">指定对象、时长与输出模块</div>
        </div>
        <div class="step-arrow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </div>
        <div class="step-card">
            <div class="step-number">3</div>
            <div class="step-name">一键生成输出</div>
            <div class="step-desc">获得大纲、PPT、试题等全套材料</div>
        </div>
    </div>
</div>
""")

# ============================================================
# 功能模块展示 - 左右交替布局（拆分成 5 次独立渲染，避免大 HTML 字符串被截断）
# ============================================================
st.html("""
<div class="features-section" id="features">
    <div class="features-header">
        <div class="features-title">覆盖全链路培训需求</div>
        <div class="features-subtitle">从课程规划到效果评估，一站式生成完整培训方案</div>
    </div>
""")

st.html(f"""
<div class="feature-row">
    <div class="feature-content">
        <div class="feature-tag">智能生成</div>
        <div class="feature-name">课程大纲自动构建</div>
        <div class="feature-desc">基于产品特性自动生成结构化课程目录，包含学习目标、知识模块和课时分配，让培训体系清晰可控。</div>
    </div>
    <div class="feature-preview">
        <img src="data:image/png;base64,{FEATURE_IMAGES['outline']}" alt="课程大纲自动构建">
    </div>
</div>
""")

st.html(f"""
<div class="feature-row reverse">
    <div class="feature-content">
        <div class="feature-tag">一键输出</div>
        <div class="feature-name">培训 PPT 即开即用</div>
        <div class="feature-desc">自动生成结构完整、版式专业的演示文稿，包含封面、目录、内容页和总结，可直接用于现场培训。</div>
    </div>
    <div class="feature-preview">
        <img src="data:image/png;base64,{FEATURE_IMAGES['ppt']}" alt="培训 PPT 即开即用">
    </div>
</div>
""")

st.html(f"""
<div class="feature-row">
    <div class="feature-content">
        <div class="feature-tag">多维度</div>
        <div class="feature-name">智能考核与评估</div>
        <div class="feature-desc">生成多类型考核题目，支持自动评分和成绩分析，帮助培训管理者科学评估培训效果。</div>
    </div>
    <div class="feature-preview">
        <img src="data:image/png;base64,{FEATURE_IMAGES['assessment']}" alt="智能考核与评估">
    </div>
</div>
""")

st.html(f"""
<div class="feature-row reverse">
    <div class="feature-content">
        <div class="feature-tag">实战导向</div>
        <div class="feature-name">实操场景化练习</div>
        <div class="feature-desc">根据产品使用场景生成实战案例与操作练习，让学员在模拟环境中快速掌握核心功能。</div>
    </div>
    <div class="feature-preview">
        <img src="data:image/png;base64,{FEATURE_IMAGES['practice']}" alt="实操场景化练习">
    </div>
</div>
""")

st.html("</div>")

# ============================================================
# 生成工作区（左右分栏）
# ============================================================
if st.session_state.scroll_to_workspace:
    st.markdown("""
    <div style="background: rgba(79, 70, 229, 0.12); border: 1px solid rgba(129, 140, 248, 0.25); border-radius: 8px; padding: 0.75rem 1rem; margin: 1rem 0; color: #c7d2fe; font-size: 0.9rem; text-align: center;">
        已跳转到工作区，请填写下方信息开始生成培训方案
    </div>
    <script>
        setTimeout(function() {
            var el = document.getElementById('workspace');
            if (el) el.scrollIntoView({behavior: 'smooth', block: 'start'});
        }, 200);
    </script>
    """, unsafe_allow_html=True)
    st.session_state.scroll_to_workspace = False

st.markdown("""
<div class="workspace-section" id="workspace">
    <div class="workspace-header">
        <div class="workspace-title">开始生成您的培训方案</div>
        <div class="workspace-subtitle">填写培训信息，一键生成完整培训材料</div>
    </div>
    <div class="workspace-grid">
""", unsafe_allow_html=True)

# 检查 API Key
if not st.session_state.api_key:
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: rgba(255,255,255,0.5); background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; margin: 1rem 0;">
        <p style="font-size: 1.1rem; margin-bottom: 0.5rem; color: rgba(255,255,255,0.85); font-weight: 600;">⚠️ API Key 未配置</p>
        <p style="font-size: 0.85rem; color: rgba(255,255,255,0.45);">请在 Streamlit Cloud 后台 Settings → Secrets 中配置 DEEPSEEK_API_KEY</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 底部页脚
    st.markdown("""
    <div class="footer-section">
        <div class="footer-brand">🎓 AI培训设计器</div>
        <div class="footer-tagline">让每一位产品培训师精准有方</div>
        <div class="footer-links">
            <a href="#top">回到顶部</a>
            <a href="#features">功能介绍</a>
            <a href="#workspace">立即开始</a>
        </div>
        <div class="footer-bottom">
            <div class="footer-copyright">© 2026 AI培训设计器</div>
            <div class="footer-copyright">v5.3 | 由 ChelseaPYC 构建</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

left_col, right_col = st.columns([1, 1])

with left_col:
    # 左侧输入面板
    st.markdown("""
    <div class="input-panel">
        <div class="input-panel-title"><span class="icon">📝</span> 培训信息</div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="form-label">产品名称</div>', unsafe_allow_html=True)
    product_name = st.text_input(
        "",
        value=st.session_state.product_name,
        placeholder="例如 WorkBuddy 智能设计助手",
        label_visibility="collapsed"
    )
    st.markdown('<div class="form-hint">输入需要设计培训方案的产品名称</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="form-label" style="margin-top: 1rem;">产品简介</div>', unsafe_allow_html=True)
    product_doc = st.text_area(
        "",
        value=st.session_state.product_doc,
        height=100,
        placeholder="简要描述产品的核心功能和定位",
        label_visibility="collapsed"
    )
    st.markdown('<div class="form-hint">简要描述产品的核心功能和定位</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="form-label" style="margin-top: 1rem;">培训对象</div>', unsafe_allow_html=True)
    training_roles = st.multiselect(
        "",
        ["实施工程师", "运维工程师", "技术支持", "销售", "客户成功", "售前工程师", "市场", "行政", "财务"],
        default=st.session_state.training_roles,
        placeholder="例如：销售团队、新员工、合作伙伴",
        label_visibility="collapsed"
    )
    
    st.markdown('<div class="form-label" style="margin-top: 1rem;">期望培训时长</div>', unsafe_allow_html=True)
    training_days = st.select_slider(
        "",
        options=list(range(1, 11)),
        value=min(st.session_state.training_days, 10),
        label_visibility="collapsed"
    )
    st.markdown(f'<div class="form-hint">当前选择：{training_days} 天（最长 10 天）</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="form-label" style="margin-top: 1rem;">产品类型</div>', unsafe_allow_html=True)
    product_type = st.selectbox(
        "",
        ["软件", "硬件", "SaaS", "平台", "其他"],
        index=["软件", "硬件", "SaaS", "平台", "其他"].index(st.session_state.product_type),
        label_visibility="collapsed"
    )
    
    # 保存当前输入
    st.session_state.product_name = product_name
    st.session_state.product_type = product_type
    st.session_state.training_roles = training_roles
    st.session_state.training_days = training_days
    st.session_state.product_doc = product_doc
    
    # 生成按钮
    st.markdown("<div style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
    generate_clicked = st.button(
        "生成培训材料",
        use_container_width=True,
        type="primary",
        disabled=st.session_state.is_generating
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    if generate_clicked:
        if not product_name:
            st.error("❌ 请输入产品名称")
            st.stop()
        elif not training_roles:
            st.error("❌ 请选择培训对象")
            st.stop()
        else:
            st.session_state.is_generating = True
            st.session_state.generation_complete = False
            st.session_state.generated_content = {}
            st.rerun()

with right_col:
    # 右侧预览面板
    st.markdown("""
    <div class="preview-panel">
        <div class="preview-panel-title"><span class="icon">👁️</span> 生成预览</div>
    """, unsafe_allow_html=True)
    
    # 生成过程
    if st.session_state.is_generating and not st.session_state.generation_complete:
        modules_to_generate = [k for k, v in st.session_state.module_selection.items() if v]
        total_modules = len(modules_to_generate)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, module in enumerate(modules_to_generate):
            progress = int(((i + 1) / total_modules) * 100)
            progress_bar.progress(progress)
            status_text.markdown(f"<div style='color: rgba(255,255,255,0.55); font-size: 0.85rem;'>正在生成：{MODULE_LABELS[module]} ({i+1}/{total_modules})</div>", unsafe_allow_html=True)
            
            prompt = build_prompt(
                module,
                product_name,
                product_type,
                training_roles,
                training_days,
                product_doc
            )
            
            content = call_deepseek(prompt, st.session_state.api_key)
            st.session_state.generated_content[module] = content
            time.sleep(0.5)
        
        progress_bar.progress(100)
        status_text.markdown("<div style='color: #22c55e; font-size: 0.85rem;'>✅ 所有内容生成完成！</div>", unsafe_allow_html=True)
        st.session_state.generation_complete = True
        st.session_state.is_generating = False
        time.sleep(1)
        st.rerun()
    
    # 显示模块预览卡片
    elif st.session_state.generation_complete:
        modules_with_content = [k for k in st.session_state.module_selection.keys() if st.session_state.module_selection[k] and k in st.session_state.generated_content]
        
        for module in modules_with_content:
            st.markdown(f"""
            <div class="preview-card selected">
                <div class="preview-icon">{MODULE_ICONS[module]}</div>
                <div class="preview-info">
                    <div class="preview-name">{MODULE_LABELS[module]}</div>
                    <div class="preview-desc">{MODULE_DESCRIPTIONS[module]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 下载按钮
        all_content = f"# {product_name} - 培训设计方案\n\n"
        all_content += f"生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        all_content += f"培训周期：{training_days} 天\n\n"
        all_content += "---\n\n"
        
        for module in modules_with_content:
            all_content += f"# {MODULE_LABELS[module]}\n\n"
            all_content += st.session_state.generated_content[module]
            all_content += "\n\n---\n\n"
        
        st.download_button(
            label="📥 下载完整方案",
            data=all_content,
            file_name=f"{product_name}_培训方案.md",
            mime="text/markdown",
            use_container_width=True
        )
    else:
        # 默认预览状态
        for module in ["blueprint", "materials", "assessment", "hands_on"]:
            is_selected = st.session_state.module_selection.get(module, True)
            card_class = "selected" if is_selected else ""
            st.markdown(f"""
            <div class="preview-card {card_class}">
                <div class="preview-icon">{MODULE_ICONS[module]}</div>
                <div class="preview-info">
                    <div class="preview-name">{MODULE_LABELS[module]}</div>
                    <div class="preview-desc">{MODULE_DESCRIPTIONS[module]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div></div>", unsafe_allow_html=True)

# ============================================================
# 生成结果展示
# ============================================================
if st.session_state.generation_complete:
    st.markdown("""
    <div class="results-section">
        <div class="features-title">生成结果</div>
    </div>
    """, unsafe_allow_html=True)
    
    modules_with_content = [k for k in st.session_state.module_selection.keys() if st.session_state.module_selection[k] and k in st.session_state.generated_content]
    
    if modules_with_content:
        tabs = st.tabs([MODULE_LABELS[m] for m in modules_with_content])
        
        for i, (tab, module) in enumerate(zip(tabs, modules_with_content)):
            with tab:
                content = st.session_state.generated_content[module]
                st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                st.markdown(content)
                st.markdown("</div>", unsafe_allow_html=True)

                st.download_button(
                    label=f"📥 下载 {MODULE_LABELS[module]}",
                    data=content,
                    file_name=f"{product_name}_{module}.md",
                    mime="text/markdown",
                    use_container_width=True
                )

# ============================================================
# 页脚
# ============================================================
st.markdown("""
<div class="footer-section">
    <div class="footer-brand">🎓 AI培训设计器</div>
    <div class="footer-tagline">让每一位产品培训师精准有方</div>
    <div class="footer-links">
        <a href="#top">回到顶部</a>
        <a href="#features">功能介绍</a>
        <a href="#workspace">立即开始</a>
    </div>
        <div class="footer-bottom">
            <div class="footer-copyright">© 2026 AI培训设计器</div>
            <div class="footer-copyright">v5.3 | 由 ChelseaPYC 构建</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
