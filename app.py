import streamlit as st
import requests
import json
import time

# ============================================================
# 配置区
# ============================================================
DEFAULT_API_KEY = st.secrets.get("DEEPSEEK_API_KEY", "")

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
    "transfer": "分阶段",
    "evaluation": "持续性"
}

# ============================================================
# 注入设计师 CSS（Streamlit 全页面样式系统）
# ============================================================

st.markdown("""
<style>
/* ================================================
   智能培训设计器 - Blue-Purple Theme
   Ported from designer HTML to Streamlit
   ================================================ */

.stApp { background: #080B14; }

/* Hide Streamlit UI */
header[data-testid="stHeader"] { display: none; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
.stDeployButton { display: none; }
.stApp > header { display: none; }
section[data-testid="stSidebar"] { display: none; }

.block-container { padding: 0 !important; max-width: 100% !important; }
.main .block-container { padding-top: 0 !important; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #080B14; }
::-webkit-scrollbar-thumb { background: rgba(108, 99, 255, 0.3); border-radius: 3px; }

/* Buttons */
.stButton > button {
    width: 100%; padding: 16px 32px !important;
    font-size: 1rem !important; font-weight: 600 !important;
    border-radius: 10px !important; border: none !important;
    background: linear-gradient(135deg, #6C63FF 0%, #4A7CF6 100%) !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 24px rgba(108, 99, 255, 0.35) !important;
    margin-top: 1rem !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 40px rgba(108, 99, 255, 0.55) !important;
    filter: brightness(1.1) !important;
}
.stButton > button:disabled { opacity: 0.7 !important; cursor: not-allowed !important; transform: none !important; }

/* Inputs */
.stTextInput input, .stTextArea textarea {
    background: #13172B !important; border: 1.5px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important; color: #F0F2FA !important;
    padding: 13px 16px !important; font-size: 0.9375rem !important;
}
.stTextInput input:hover, .stTextArea textarea:hover { border-color: rgba(255, 255, 255, 0.15) !important; }
.stTextInput input:focus, .stTextArea textarea:focus {
    background: #181E38 !important; border-color: #6C63FF !important;
    box-shadow: 0 0 0 4px rgba(108, 99, 255, 0.12) !important;
}
.stTextArea textarea { min-height: 90px !important; }

/* Multiselect */
.stMultiSelect [data-baseweb="tag"] {
    background: rgba(108, 99, 255, 0.12) !important;
    border: 1px solid rgba(108, 99, 255, 0.2) !important; color: #6C63FF !important;
}
.stMultiSelect [data-baseweb="input"] {
    background: #13172B !important; border: 1.5px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important; color: #F0F2FA !important;
}

/* Select */
.stSelectbox [data-baseweb="select"] > div {
    background: #13172B !important; border: 1.5px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important; color: #9BA0B8 !important;
}

/* Slider */
[data-testid="stThumbValue"] { background: linear-gradient(135deg, #6C63FF 0%, #4A7CF6 100%) !important; color: #FFFFFF !important; }
div[data-baseweb="slider"] div[data-testid="stThumbValue"] { background: linear-gradient(135deg, #6C63FF 0%, #4A7CF6 100%) !important; }
[data-baseweb="slider"] div[class*="sliderHandle"] {
    background: #FFFFFF !important; border: 2.5px solid #6C63FF !important;
    box-shadow: 0 0 16px rgba(108, 99, 255, 0.35) !important;
}
[data-baseweb="slider"] div[class*="sliderTrack"] { background: linear-gradient(90deg, #6C63FF 0%, #4A7CF6 100%) !important; }

/* Tabs */
.stTabs [data-baseweb="tab"] { color: #9BA0B8 !important; font-weight: 500 !important; }
.stTabs [aria-selected="true"] { color: #6C63FF !important; border-bottom-color: #6C63FF !important; }

/* Progress */
.stProgress > div > div { background: linear-gradient(135deg, #6C63FF 0%, #4A7CF6 100%) !important; }

/* Download */
.stDownloadButton > button {
    background: rgba(108, 99, 255, 0.1) !important; border: 1.5px solid rgba(108, 99, 255, 0.2) !important;
    color: #6C63FF !important; font-weight: 500 !important;
}
.stDownloadButton > button:hover { background: rgba(108, 99, 255, 0.18) !important; }

/* ================================================
   智能培训设计器 - 企业培训智能化平台
   Blue-Purple Theme · 蓝紫科技风
   Designed by UI Designer
   ================================================ */

/* ================================================
   DESIGN TOKENS
   ================================================ */

:root {
  /* === Background Colors (Dark Theme) === */
  --c-bg-page:           #080B14;
  --c-bg-page-alt:       #0C0F1A;
  --c-bg-section:        #0D1020;
  --c-bg-card:           #111527;
  --c-bg-card-hover:     #181D36;
  --c-bg-card-glass:     rgba(17, 21, 39, 0.7);
  --c-bg-input:          #13172B;
  --c-bg-input-focus:    #181E38;
  --c-bg-mockup:         #0E1224;
  --c-bg-mockup-panel:   #141A32;

  /* === Text Colors === */
  --c-text-primary:      #F0F2FA;
  --c-text-secondary:    #9BA0B8;
  --c-text-muted:        #696E85;
  --c-text-dim:          #4A4F66;

  /* === Accent — 蓝紫色系 (Blue-Purple) === */
  --c-accent-primary:    #6C63FF;   /* 蓝紫色 */
  --c-accent-blue:       #4A7CF6;   /* 亮蓝 */
  --c-accent-cyan:       #00C7E6;   /* 青色点缀 */
  --c-accent-pink:       #E870A0;   /* 粉色点缀（低使用率） */

  /* === Gradients === */
  --c-gradient-primary:  linear-gradient(135deg, #6C63FF 0%, #4A7CF6 100%);
  --c-gradient-wide:     linear-gradient(135deg, #6C63FF 0%, #4A7CF6 40%, #00C7E6 100%);
  --c-gradient-card:     linear-gradient(180deg, rgba(108, 99, 255, 0.06) 0%, transparent 100%);

  /* === Glows === */
  --c-glow-primary:      rgba(108, 99, 255, 0.35);
  --c-glow-strong:       rgba(108, 99, 255, 0.55);
  --c-glow-blue:         rgba(74, 124, 246, 0.25);

  /* === Border Colors === */
  --c-border-default:    rgba(255, 255, 255, 0.06);
  --c-border-subtle:     rgba(255, 255, 255, 0.04);
  --c-border-hover:      rgba(255, 255, 255, 0.12);
  --c-border-input:      rgba(255, 255, 255, 0.1);
  --c-border-accent:     rgba(108, 99, 255, 0.3);
  --c-border-accent-hover: rgba(108, 99, 255, 0.5);

  /* === Typography === */
  --ff-sans: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;

  /* === Spacing === */
  --sp-xs:    0.5rem;   /* 8px */
  --sp-sm:    1rem;     /* 16px */
  --sp-md:    1.5rem;   /* 24px */
  --sp-lg:    2rem;     /* 32px */
  --sp-xl:    3rem;     /* 48px */
  --sp-2xl:   4rem;     /* 64px */
  --sp-3xl:   6rem;     /* 96px */
  --sp-4xl:   8rem;     /* 128px */

  /* === Radius === */
  --r-sm:  6px;
  --r-md:  10px;
  --r-lg:  14px;
  --r-xl:  20px;
  --r-2xl: 24px;
  --r-full: 9999px;

  /* === Transitions === */
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
  --t-fast: 180ms var(--ease-out);
  --t-norm: 350ms var(--ease-out);
  --t-slow: 500ms var(--ease-out);

  /* === Layout === */
  --container-max:     1200px;
  --container-narrow:  960px;
  --nav-height:        64px;
}

/* ================================================
   RESET & BASE
   ================================================ */

*, *::before, *::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  scroll-behavior: smooth;
}

body {
  font-family: var(--ff-sans);
  color: var(--c-text-primary);
  background: var(--c-bg-page);
  line-height: 1.7;
  overflow-x: hidden;
}

img { max-width: 100%; display: block; }
button { font-family: inherit; cursor: pointer; border: none; outline: none; }
input, textarea, select { font-family: inherit; color: var(--c-text-primary); }
a { color: inherit; text-decoration: none; }
::placeholder { color: var(--c-text-muted); }

/* ================================================
   GLOBAL DECORATIONS — 背景纹理
   ================================================ */

body::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    radial-gradient(circle at 20% 30%, rgba(108, 99, 255, 0.04) 0%, transparent 50%),
    radial-gradient(circle at 80% 60%, rgba(74, 124, 246, 0.03) 0%, transparent 50%),
    radial-gradient(circle at 50% 90%, rgba(0, 199, 230, 0.02) 0%, transparent 40%);
  pointer-events: none;
  z-index: 0;
}

/* Subtle grid pattern overlay on dark sections */
.section-grid-overlay {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.015) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.015) 1px, transparent 1px);
  background-size: 60px 60px;
  pointer-events: none;
  z-index: 0;
}

/* ================================================
   NAVIGATION BAR
   ================================================ */

.nav-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--nav-height);
  z-index: 1000;
  transition: all var(--t-norm);
  padding: 0 var(--sp-md);
  display: flex;
  align-items: center;
}

.nav-bar.scrolled {
  background: rgba(8, 11, 20, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--c-border-default);
  box-shadow: 0 1px 20px rgba(0, 0, 0, 0.3);
}

.nav-inner {
  max-width: var(--container-max);
  width: 100%;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-logo-icon {
  width: 32px;
  height: 32px;
  border-radius: var(--r-md);
  background: var(--c-gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 16px var(--c-glow-primary);
}

.nav-logo-text {
  font-size: 1.0625rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--c-text-primary);
}

.nav-links {
  display: flex;
  align-items: center;
  gap: var(--sp-lg);
}

.nav-link {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--c-text-secondary);
  transition: color var(--t-fast);
  position: relative;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  right: 0;
  height: 2px;
  border-radius: var(--r-full);
  background: var(--c-gradient-primary);
  transform: scaleX(0);
  transition: transform var(--t-fast);
}

.nav-link:hover {
  color: var(--c-text-primary);
}

.nav-link:hover::after {
  transform: scaleX(1);
}

.nav-cta {
  padding: 10px 22px;
  font-size: 0.875rem;
  font-weight: 600;
  border-radius: var(--r-md);
  background: var(--c-gradient-primary);
  color: #FFFFFF;
  transition: all var(--t-fast);
  box-shadow: 0 2px 16px var(--c-glow-primary);
}

.nav-cta:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 24px var(--c-glow-strong);
  filter: brightness(1.1);
}

/* ================================================
   HERO SECTION
   ================================================ */

.hero-section {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  padding: calc(var(--nav-height) + var(--sp-4xl)) var(--sp-md) var(--sp-3xl);
  background: var(--c-bg-page);
  overflow: hidden;
  z-index: 1;
}

.hero-section .section-grid-overlay {
  opacity: 0.6;
}

/* Multi-layer glow system */
.hero-section::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 70% 50% at 25% 35%, rgba(108, 99, 255, 0.2) 0%, transparent 55%),
    radial-gradient(ellipse 60% 40% at 75% 65%, rgba(74, 124, 246, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse 40% 30% at 55% 50%, rgba(0, 199, 230, 0.06) 0%, transparent 45%);
  pointer-events: none;
}

/* Large ambient glow orb */
.hero-glow {
  position: absolute;
  top: 45%;
  left: 55%;
  transform: translate(-50%, -50%);
  width: 650px;
  height: 650px;
  background: radial-gradient(circle, rgba(108, 99, 255, 0.13) 0%, transparent 60%);
  pointer-events: none;
  filter: blur(60px);
  animation: heroGlowPulse 6s ease-in-out infinite;
}

@keyframes heroGlowPulse {
  0%, 100% { opacity: 0.7; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 1; transform: translate(-50%, -50%) scale(1.08); }
}

/* Decorative geometric lines */
.hero-geo {
  position: absolute;
  top: 20%;
  right: 8%;
  width: 200px;
  height: 200px;
  border: 1px solid rgba(108, 99, 255, 0.08);
  border-radius: var(--r-2xl);
  transform: rotate(12deg);
  pointer-events: none;
  animation: geoFloat 8s ease-in-out infinite;
}

.hero-geo::before {
  content: '';
  position: absolute;
  top: 20px;
  left: 20px;
  right: 20px;
  bottom: 20px;
  border: 1px solid rgba(74, 124, 246, 0.06);
  border-radius: var(--r-lg);
}

@keyframes geoFloat {
  0%, 100% { transform: rotate(12deg) translateY(0); }
  50% { transform: rotate(14deg) translateY(-12px); }
}

.hero-container {
  position: relative;
  z-index: 2;
  max-width: var(--container-max);
  width: 100%;
  margin: 0 auto;
}

.hero-tag {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--c-text-secondary);
  letter-spacing: 0.03em;
  margin-bottom: var(--sp-lg);
  padding: 6px 16px 6px 6px;
  border-radius: var(--r-full);
  background: rgba(108, 99, 255, 0.08);
  border: 1px solid rgba(108, 99, 255, 0.15);
}

.hero-tag-icon {
  width: 22px;
  height: 22px;
  border-radius: var(--r-full);
  background: var(--c-gradient-primary);
  box-shadow: 0 0 14px var(--c-glow-primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-title {
  font-size: clamp(2.75rem, 7vw, 5rem);
  font-weight: 900;
  line-height: 1.08;
  letter-spacing: -0.035em;
  color: var(--c-text-primary);
  margin-bottom: var(--sp-md);
  max-width: 700px;
}

.hero-title em {
  font-style: normal;
  background: var(--c-gradient-wide);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.125rem;
  line-height: 1.8;
  color: var(--c-text-secondary);
  max-width: 540px;
  margin-bottom: var(--sp-xl);
}

.hero-actions {
  display: flex;
  gap: var(--sp-sm);
  flex-wrap: wrap;
}

/* ================================================
   BUTTONS
   ================================================ */

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 14px 32px;
  font-size: 0.9375rem;
  font-weight: 600;
  border-radius: var(--r-md);
  border: 1.5px solid transparent;
  transition: all var(--t-fast);
  text-decoration: none;
  user-select: none;
  white-space: nowrap;
}

.btn-primary {
  background: var(--c-gradient-primary);
  color: #FFFFFF;
  border-color: transparent;
  box-shadow: 0 4px 24px var(--c-glow-primary);
  position: relative;
  overflow: hidden;
}

.btn-primary::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, transparent 0%, rgba(255, 255, 255, 0.1) 50%, transparent 100%);
  transform: translateX(-100%);
  transition: transform 0.6s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 36px var(--c-glow-strong);
}

.btn-primary:hover::after {
  transform: translateX(100%);
}

.btn-outline {
  background: transparent;
  color: var(--c-text-primary);
  border-color: rgba(255, 255, 255, 0.18);
}

.btn-outline:hover {
  border-color: rgba(255, 255, 255, 0.35);
  background: rgba(255, 255, 255, 0.04);
  transform: translateY(-1px);
}

/* Generate button */
.btn-generate {
  width: 100%;
  padding: 16px 32px;
  background: var(--c-gradient-primary);
  color: #FFFFFF;
  font-size: 1rem;
  font-weight: 600;
  border-radius: var(--r-md);
  border: none;
  transition: all var(--t-fast);
  cursor: pointer;
  box-shadow: 0 4px 24px var(--c-glow-primary);
  margin-top: var(--sp-sm);
  position: relative;
  overflow: hidden;
}

.btn-generate::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, transparent 0%, rgba(255, 255, 255, 0.12) 50%, transparent 100%);
  transform: translateX(-100%);
  transition: transform 0.6s ease;
}

.btn-generate:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 40px var(--c-glow-strong);
}

.btn-generate:hover::after {
  transform: translateX(100%);
}

.btn-generate:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

/* ================================================
   SECTION HEADINGS
   ================================================ */

.section-heading-wrap {
  position: relative;
  padding-left: 16px;
  margin-bottom: var(--sp-2xl);
}

.section-heading-wrap::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0.3rem;
  bottom: 0.3rem;
  width: 4px;
  border-radius: var(--r-full);
  background: var(--c-gradient-primary);
  box-shadow: 0 0 16px var(--c-glow-primary);
}

.section-heading-lg {
  font-size: clamp(1.75rem, 3.5vw, 2.25rem);
  font-weight: 800;
  letter-spacing: -0.025em;
  color: var(--c-text-primary);
  margin-bottom: var(--sp-xs);
}

.section-desc {
  font-size: 0.9375rem;
  color: var(--c-text-secondary);
  line-height: 1.6;
}

/* ================================================
   GRADIENT DIVIDER
   ================================================ */

.gradient-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, rgba(108, 99, 255, 0.3) 30%, rgba(74, 124, 246, 0.3) 70%, transparent 100%);
  border: none;
  margin: 0;
}

/* ================================================
   STEPS SECTION
   ================================================ */

.steps-section {
  position: relative;
  background: var(--c-bg-section);
  padding: var(--sp-4xl) var(--sp-md);
  z-index: 1;
}

.container-narrow {
  max-width: var(--container-narrow);
  margin: 0 auto;
  position: relative;
  z-index: 2;
}

.steps-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--sp-lg);
}

.step-card {
  position: relative;
  background: var(--c-bg-card);
  border: 1px solid var(--c-border-default);
  border-radius: var(--r-xl);
  padding: var(--sp-xl) var(--sp-lg);
  text-align: center;
  transition: all var(--t-norm);
  overflow: hidden;
}

.step-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--c-gradient-card);
  opacity: 0;
  transition: opacity var(--t-norm);
}

.step-card:hover {
  background: var(--c-bg-card-hover);
  border-color: var(--c-border-accent);
  transform: translateY(-6px);
  box-shadow: 0 20px 48px rgba(0, 0, 0, 0.4), 0 0 40px rgba(108, 99, 255, 0.08);
}

.step-card:hover::before {
  opacity: 1;
}

.step-number {
  position: relative;
  z-index: 1;
  width: 48px;
  height: 48px;
  border-radius: var(--r-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  font-weight: 800;
  color: #FFFFFF;
  background: var(--c-gradient-primary);
  margin: 0 auto var(--sp-md);
  box-shadow: 0 4px 20px var(--c-glow-primary);
}

.step-title {
  position: relative;
  z-index: 1;
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--c-text-primary);
  margin-bottom: var(--sp-xs);
}

.step-desc {
  position: relative;
  z-index: 1;
  font-size: 0.875rem;
  line-height: 1.6;
  color: var(--c-text-secondary);
}

/* Connection lines between steps (desktop only) */
@media (min-width: 769px) {
  .steps-grid {
    position: relative;
  }

  .steps-grid::before {
    content: '';
    position: absolute;
    top: 44px;
    left: 22%;
    right: 22%;
    height: 1px;
    background: linear-gradient(90deg, rgba(108, 99, 255, 0.2), rgba(74, 124, 246, 0.2), rgba(108, 99, 255, 0.2));
    z-index: 0;
    opacity: 0.5;
  }
}

/* ================================================
   FEATURES SECTION
   ================================================ */

.features-section {
  position: relative;
  background: var(--c-bg-page);
  padding: var(--sp-4xl) var(--sp-md);
  z-index: 1;
}

.container-wide {
  max-width: var(--container-max);
  margin: 0 auto;
  position: relative;
  z-index: 2;
}

/* Feature Row Card */
.feature-wrapper {
  position: relative;
  padding: var(--sp-xl) 0;
  border-bottom: 1px solid var(--c-border-subtle);
}

.feature-wrapper:last-child {
  border-bottom: none;
}

.feature-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--sp-3xl);
  align-items: center;
}

.feature-row-reverse .feature-img-col {
  order: 2;
}

.feature-row-reverse .feature-text-col {
  order: 1;
}

.feature-text-col,
.feature-img-col {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* ---- Feature Number Watermark ---- */
.feature-number {
  position: absolute;
  top: 0;
  font-size: clamp(5rem, 10vw, 9rem);
  font-weight: 900;
  line-height: 0.82;
  letter-spacing: -0.05em;
  color: rgba(108, 99, 255, 0.035);
  pointer-events: none;
  z-index: 0;
  user-select: none;
}

.feature-wrapper:nth-child(odd) .feature-number {
  right: 6%;
}

.feature-wrapper:nth-child(even) .feature-number {
  left: 6%;
}

/* ---- Feature Text Column ---- */
.feature-text-col {
  position: relative;
  z-index: 1;
}

.feature-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  padding: 6px 14px;
  border-radius: var(--r-full);
  margin-bottom: var(--sp-md);
  background: rgba(108, 99, 255, 0.1);
  color: var(--c-accent-primary);
  border: 1px solid rgba(108, 99, 255, 0.18);
}

.feature-title {
  font-size: clamp(1.5rem, 2.4vw, 1.875rem);
  font-weight: 800;
  letter-spacing: -0.025em;
  color: var(--c-text-primary);
  margin-bottom: var(--sp-sm);
  line-height: 1.25;
}

.feature-desc {
  font-size: 0.9375rem;
  line-height: 1.85;
  color: var(--c-text-secondary);
  max-width: 460px;
}

/* ---- Mockup Column ---- */
.feature-img-col {
  position: relative;
  z-index: 1;
}

/* Mockup Outer Glow Ring */
.feature-mockup-wrap {
  position: relative;
  z-index: 1;
}

.feature-mockup-wrap::before {
  content: '';
  position: absolute;
  inset: -8px;
  border-radius: calc(var(--r-xl) + 6px);
  background: linear-gradient(135deg, rgba(108, 99, 255, 0.08), rgba(74, 124, 246, 0.04), transparent 60%);
  opacity: 0;
  transition: opacity var(--t-norm);
  pointer-events: none;
  z-index: -1;
  filter: blur(12px);
}

.feature-mockup-wrap:hover::before {
  opacity: 1;
}

/* Feature Mockup */
.feature-mockup {
  background: var(--c-bg-mockup);
  border: 1px solid var(--c-border-default);
  border-radius: var(--r-xl);
  padding: 14px;
  position: relative;
  overflow: hidden;
  transition: all var(--t-norm);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.feature-mockup:hover {
  border-color: var(--c-border-accent);
  box-shadow: 0 16px 56px rgba(0, 0, 0, 0.4), 0 0 56px rgba(108, 99, 255, 0.1);
  transform: translateY(-3px);
}

.mockup-header {
  display: flex;
  gap: 7px;
  margin-bottom: var(--sp-sm);
  padding-left: 4px;
}

.mockup-dot {
  width: 9px;
  height: 9px;
  border-radius: var(--r-full);
}

.mockup-dot:nth-child(1) { background: #FF5F57; }
.mockup-dot:nth-child(2) { background: #FFBD2E; }
.mockup-dot:nth-child(3) { background: #28CA41; }

.mockup-body {
  background: var(--c-bg-mockup-panel);
  border-radius: var(--r-lg);
  min-height: 280px;
  display: flex;
  gap: var(--sp-sm);
  padding: var(--sp-sm);
  border: 1px solid var(--c-border-subtle);
}

/* ---- Inter-Feature Connector ---- */
.feature-connector {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--sp-sm) 0;
  gap: 0;
}

.feature-connector-line {
  width: 1px;
  height: 36px;
  background: linear-gradient(180deg, rgba(108, 99, 255, 0.25), transparent);
}

.feature-connector-dot {
  width: 7px;
  height: 7px;
  border-radius: var(--r-full);
  background: rgba(108, 99, 255, 0.2);
  box-shadow: 0 0 10px rgba(108, 99, 255, 0.15);
}


/* === Course Outline Mockup === */
.mockup-sidebar {
  width: 32%;
  padding: var(--sp-sm);
  border-right: 1px solid var(--c-border-subtle);
}

.mockup-line {
  height: 8px;
  border-radius: var(--r-full);
  background: rgba(255, 255, 255, 0.06);
  margin-bottom: 12px;
  width: 80%;
}

.mockup-line.short {
  width: 50%;
}

.mockup-main {
  flex: 1;
  padding: var(--sp-sm);
}

.mockup-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--c-text-primary);
  margin-bottom: var(--sp-sm);
}

.mockup-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mockup-list-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--r-md);
  background: rgba(255, 255, 255, 0.03);
  font-size: 0.75rem;
  color: var(--c-text-secondary);
  border: 1px solid transparent;
  transition: all var(--t-fast);
}

.mockup-list-item.active {
  background: rgba(108, 99, 255, 0.12);
  color: var(--c-accent-primary);
  border: 1px solid rgba(108, 99, 255, 0.2);
  box-shadow: 0 0 16px rgba(108, 99, 255, 0.1);
}

.mockup-num {
  width: 20px;
  height: 20px;
  border-radius: var(--r-full);
  background: rgba(255, 255, 255, 0.06);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.625rem;
  font-weight: 700;
  flex-shrink: 0;
}

.mockup-list-item.active .mockup-num {
  background: var(--c-gradient-primary);
  color: #FFFFFF;
}

.mockup-button {
  margin-top: var(--sp-sm);
  padding: 10px 16px;
  border-radius: var(--r-md);
  background: var(--c-gradient-primary);
  color: #FFFFFF;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-block;
  box-shadow: 0 4px 14px var(--c-glow-primary);
}

/* === PPT Mockup (Redesigned) === */
.ppt-body {
  flex-direction: row;
  padding: 0;
  gap: 0;
  overflow: hidden;
}

/* Left: Slide Navigator */
.ppt-nav {
  width: 56px;
  padding: var(--sp-sm) 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-right: 1px solid var(--c-border-subtle);
  background: rgba(255, 255, 255, 0.015);
  align-items: center;
}

.ppt-nav-item {
  width: 100%;
  aspect-ratio: 4 / 3;
  border-radius: var(--r-sm);
  background: rgba(255, 255, 255, 0.04);
  border: 1.5px solid transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.625rem;
  font-weight: 600;
  color: var(--c-text-dim);
  cursor: pointer;
  transition: all var(--t-fast);
}

.ppt-nav-item:hover {
  background: rgba(255, 255, 255, 0.08);
  color: var(--c-text-secondary);
}

.ppt-nav-item.active {
  background: rgba(108, 99, 255, 0.12);
  border-color: rgba(108, 99, 255, 0.4);
  color: var(--c-accent-primary);
  box-shadow: 0 0 12px rgba(108, 99, 255, 0.1);
}

/* Right: Main Slide Preview */
.ppt-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 10px;
  gap: 8px;
}

.ppt-main-tabs {
  display: flex;
  gap: 4px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--c-border-subtle);
}

.ppt-main-tab {
  font-size: 0.625rem;
  font-weight: 500;
  padding: 4px 12px;
  border-radius: var(--r-sm);
  color: var(--c-text-muted);
  transition: all var(--t-fast);
  cursor: pointer;
}

.ppt-main-tab.active {
  background: rgba(108, 99, 255, 0.12);
  color: var(--c-accent-primary);
  font-weight: 600;
}

/* Slide Preview Canvas */
.ppt-slide-preview {
  flex: 1;
  background: rgba(255, 255, 255, 0.03);
  border-radius: var(--r-md);
  border: 1px solid var(--c-border-subtle);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.ppt-slide-topbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: rgba(108, 99, 255, 0.08);
  border-bottom: 1px solid rgba(108, 99, 255, 0.12);
}

.ppt-slide-section-num {
  width: 26px;
  height: 26px;
  border-radius: var(--r-sm);
  background: var(--c-gradient-primary);
  color: #FFFFFF;
  font-size: 0.6875rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ppt-slide-section-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--c-text-primary);
}

.ppt-slide-canvas {
  flex: 1;
  display: flex;
  padding: 14px;
  gap: 14px;
}

.ppt-canvas-col {
  flex: 1.2;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ppt-feat-block {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--r-md);
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid transparent;
  transition: all var(--t-fast);
}

.ppt-feat-block:nth-child(2) {
  background: rgba(108, 99, 255, 0.08);
  border-color: rgba(108, 99, 255, 0.2);
}

.ppt-feat-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: var(--r-md);
  background: rgba(108, 99, 255, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ppt-feat-icon {
  width: 16px;
  height: 16px;
  border-radius: var(--r-sm);
  background: var(--c-accent-primary);
  opacity: 0.7;
}

.ppt-feat-block:nth-child(2) .ppt-feat-icon {
  opacity: 1;
  box-shadow: 0 0 8px var(--c-glow-primary);
}

.ppt-feat-name {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--c-text-primary);
  margin-bottom: 2px;
}

.ppt-feat-desc {
  font-size: 0.625rem;
  color: var(--c-text-muted);
  line-height: 1.4;
}

/* Visual Area — Chart + Ring */
.ppt-canvas-visual {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 4px;
}

.ppt-visual-chart {
  display: flex;
  align-items: flex-end;
  gap: 5px;
  height: 64px;
  width: 100%;
  justify-content: center;
}

.ppt-visual-bar {
  width: 12px;
  border-radius: var(--r-full) var(--r-full) 0 0;
  background: rgba(255, 255, 255, 0.08);
  transition: all var(--t-slow);
}

.ppt-visual-bar.active {
  background: var(--c-gradient-primary);
  box-shadow: 0 0 10px rgba(108, 99, 255, 0.3);
}

.ppt-visual-ring {
  width: 60px;
  height: 60px;
  border-radius: var(--r-full);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ppt-ring-track {
  position: absolute;
  inset: 0;
  border-radius: var(--r-full);
  background: conic-gradient(var(--c-accent-primary) 0deg, var(--c-accent-primary) 280deg, rgba(255, 255, 255, 0.05) 280deg);
  -webkit-mask: radial-gradient(transparent 62%, black 63%);
  mask: radial-gradient(transparent 62%, black 63%);
}

.ppt-ring-value {
  font-size: 0.8125rem;
  font-weight: 700;
  color: var(--c-text-primary);
  z-index: 1;
}

.ppt-slide-footer {
  padding: 8px 14px;
  border-top: 1px solid var(--c-border-subtle);
  font-size: 0.5625rem;
  color: var(--c-text-dim);
  text-align: center;
  letter-spacing: 0.02em;
}

/* === Dashboard Mockup === */
.dashboard-body {
  flex-direction: column;
  gap: var(--sp-sm);
}

.dashboard-row {
  display: flex;
  gap: var(--sp-sm);
}

.dashboard-card {
  flex: 1;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--c-border-subtle);
  border-radius: var(--r-md);
  padding: var(--sp-sm);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 96px;
  transition: all var(--t-fast);
}

.dashboard-card.wide {
  flex: 2;
}

.dashboard-label {
  font-size: 0.625rem;
  color: var(--c-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 600;
}

.dashboard-ring {
  width: 52px;
  height: 52px;
  border-radius: var(--r-full);
  background: conic-gradient(var(--c-accent-primary) 0deg, var(--c-accent-primary) 270deg, rgba(255, 255, 255, 0.04) 270deg);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.dashboard-ring::after {
  content: '';
  position: absolute;
  inset: 4px;
  border-radius: var(--r-full);
  background: var(--c-bg-mockup-panel);
}

.dashboard-ring span {
  position: relative;
  z-index: 1;
  font-size: 0.8125rem;
  font-weight: 700;
  color: var(--c-text-primary);
}

.dashboard-chart {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  height: 50px;
  width: 100%;
  justify-content: center;
  padding: 0 10px;
}

.dashboard-chart .bar {
  width: 8px;
  border-radius: var(--r-full);
  background: var(--c-gradient-primary);
  transition: height var(--t-slow);
}

/* === Practice Mockup === */
.practice-body {
  padding: 0;
  gap: 0;
  overflow: hidden;
}

.practice-sidebar {
  width: 40%;
  padding: var(--sp-md);
  border-right: 1px solid var(--c-border-subtle);
  background: rgba(255, 255, 255, 0.015);
}

.practice-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--c-text-primary);
  margin-bottom: var(--sp-sm);
}

.practice-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.75rem;
  color: var(--c-text-secondary);
  padding: 8px 0;
  transition: color var(--t-fast);
}

.practice-item.active {
  color: var(--c-accent-primary);
}

.practice-dot {
  width: 7px;
  height: 7px;
  border-radius: var(--r-full);
  background: var(--c-text-dim);
  flex-shrink: 0;
}

.practice-item.active .practice-dot {
  background: var(--c-accent-primary);
  box-shadow: 0 0 8px var(--c-glow-primary);
}

.practice-main {
  flex: 1;
  padding: var(--sp-md);
}

.checklist-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--c-text-primary);
  margin-bottom: var(--sp-sm);
}

.checklist-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.75rem;
  color: var(--c-text-secondary);
  padding: 7px 0;
}

.check {
  width: 16px;
  height: 16px;
  border-radius: var(--r-sm);
  border: 1.5px solid var(--c-accent-primary);
  position: relative;
  flex-shrink: 0;
  background: rgba(108, 99, 255, 0.08);
}

.check::after {
  content: '';
  position: absolute;
  left: 4px;
  top: 5px;
  width: 5px;
  height: 3px;
  border-left: 2px solid var(--c-accent-primary);
  border-bottom: 2px solid var(--c-accent-primary);
  transform: rotate(-45deg);
}

/* ================================================
   GENERATOR SECTION
   ================================================ */

.generator-section {
  position: relative;
  background: var(--c-bg-section);
  padding: var(--sp-4xl) var(--sp-md);
  z-index: 1;
}

.container-generator {
  max-width: var(--container-max);
  margin: 0 auto;
  position: relative;
  z-index: 2;
}

.generator-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--sp-2xl);
  align-items: start;
}

.panel-heading {
  display: flex;
  align-items: center;
  gap: var(--sp-sm);
  margin-bottom: var(--sp-lg);
}

.panel-icon {
  width: 22px;
  height: 22px;
  border-radius: var(--r-sm);
  background: var(--c-gradient-primary);
  box-shadow: 0 0 14px var(--c-glow-primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.panel-heading h3 {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--c-text-primary);
  letter-spacing: -0.01em;
}

/* Form Panel */
.form-panel {
  background: var(--c-bg-card-glass);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--c-border-default);
  border-radius: var(--r-xl);
  padding: var(--sp-xl);
}

.form-group {
  margin-bottom: var(--sp-md);
}

.form-label {
  display: block;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--c-text-primary);
  margin-bottom: var(--sp-xs);
}

.form-input {
  width: 100%;
  padding: 13px 16px;
  font-size: 0.9375rem;
  color: var(--c-text-primary);
  background: var(--c-bg-input);
  border: 1.5px solid var(--c-border-input);
  border-radius: var(--r-md);
  transition: all var(--t-fast);
  outline: none;
}

.form-input:hover {
  border-color: rgba(255, 255, 255, 0.15);
}

.form-input:focus {
  background: var(--c-bg-input-focus);
  border-color: var(--c-accent-primary);
  box-shadow: 0 0 0 4px rgba(108, 99, 255, 0.12), 0 0 20px rgba(108, 99, 255, 0.08);
}

.form-textarea {
  resize: vertical;
  min-height: 90px;
  line-height: 1.5;
}

.form-hint {
  font-size: 0.75rem;
  color: var(--c-text-muted);
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* Select Dropdown */
.select-wrapper {
  position: relative;
}

.form-select {
  appearance: none;
  -webkit-appearance: none;
  cursor: pointer;
  padding-right: 44px;
  color: var(--c-text-secondary);
}

.form-select option {
  background: var(--c-bg-card);
  color: var(--c-text-primary);
}

.select-arrow {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--c-text-muted);
  pointer-events: none;
  transition: transform var(--t-fast);
}

.select-wrapper:hover .select-arrow {
  color: var(--c-accent-primary);
}

/* Range Slider */
.slider-wrap {
  position: relative;
  padding: 12px 0;
}

.form-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 5px;
  background: transparent;
  border-radius: var(--r-full);
  outline: none;
  position: relative;
  z-index: 2;
}

.slider-track {
  position: absolute;
  left: 0;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  height: 5px;
  border-radius: var(--r-full);
  background: linear-gradient(90deg, var(--c-accent-primary) 0%, var(--c-accent-primary) 30%, rgba(255, 255, 255, 0.06) 30%);
  z-index: 1;
}

.form-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: var(--r-full);
  background: #FFFFFF;
  border: 2.5px solid var(--c-accent-primary);
  cursor: pointer;
  box-shadow: 0 0 16px var(--c-glow-primary), 0 2px 8px rgba(0, 0, 0, 0.3);
  transition: all var(--t-fast);
}

.form-slider::-webkit-slider-thumb:hover {
  transform: scale(1.2);
  box-shadow: 0 0 24px var(--c-glow-strong), 0 4px 12px rgba(0, 0, 0, 0.4);
}

.form-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: var(--r-full);
  background: #FFFFFF;
  border: 2.5px solid var(--c-accent-primary);
  cursor: pointer;
  box-shadow: 0 0 16px var(--c-glow-primary);
}

.slider-info {
  font-size: 0.75rem;
  color: var(--c-text-muted);
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.slider-info strong {
  color: var(--c-accent-primary);
  font-weight: 600;
  font-size: 0.8125rem;
}

/* Preview Panel */
.preview-panel {
  background: var(--c-bg-card-glass);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--c-border-default);
  border-radius: var(--r-xl);
  padding: var(--sp-xl);
  position: sticky;
  top: calc(var(--nav-height) + 2rem);
  transition: border-color var(--t-norm);
}

.preview-list {
  display: flex;
  flex-direction: column;
  gap: var(--sp-sm);
}

.preview-item {
  display: flex;
  align-items: center;
  gap: var(--sp-sm);
  padding: 16px;
  background: var(--c-bg-input);
  border: 1.5px solid var(--c-border-input);
  border-radius: var(--r-md);
  transition: all var(--t-fast);
  cursor: pointer;
}

.preview-item:hover {
  background: var(--c-bg-input-focus);
  border-color: var(--c-border-accent);
  transform: translateX(6px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.preview-item.selected {
  border-color: var(--c-accent-primary);
  background: rgba(108, 99, 255, 0.08);
  box-shadow: 0 0 24px rgba(108, 99, 255, 0.12);
}

.preview-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--r-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: rgba(108, 99, 255, 0.1);
  color: var(--c-accent-primary);
  transition: all var(--t-fast);
}

.preview-item:hover .preview-icon,
.preview-item.selected .preview-icon {
  background: rgba(108, 99, 255, 0.18);
  box-shadow: 0 0 16px rgba(108, 99, 255, 0.2);
}

.preview-info h4 {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--c-text-primary);
  margin-bottom: 3px;
}

.preview-info p {
  font-size: 0.75rem;
  color: var(--c-text-muted);
}

/* ================================================
   FOOTER
   ================================================ */

.footer {
  position: relative;
  background: var(--c-bg-page);
  padding: var(--sp-2xl) var(--sp-md);
  border-top: 1px solid var(--c-border-default);
  z-index: 1;
}

.footer-inner {
  max-width: var(--container-max);
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--sp-md);
}

.footer-brand {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.footer-logo-text {
  font-size: 1.0625rem;
  font-weight: 700;
  color: var(--c-text-primary);
  letter-spacing: -0.01em;
}

.footer-slogan {
  font-size: 0.8125rem;
  color: var(--c-text-muted);
  padding-left: 0;
}

.footer-links {
  display: flex;
  gap: var(--sp-lg);
  align-items: center;
}

.footer-links a {
  font-size: 0.875rem;
  color: var(--c-text-secondary);
  transition: color var(--t-fast);
}

.footer-links a:hover {
  color: var(--c-text-primary);
}

.footer-divider {
  width: 4px;
  height: 4px;
  border-radius: var(--r-full);
  background: var(--c-text-dim);
  opacity: 0.4;
}

/* ================================================
   SCROLL ANIMATIONS (Reveal on Scroll)
   ================================================ */

/* .reveal removed for Streamlit compatibility */

/* .reveal.visible removed for Streamlit compatibility */

/* .reveal-delay removed for Streamlit compatibility */
/* .reveal-delay removed for Streamlit compatibility */
/* .reveal-delay removed for Streamlit compatibility */
/* .reveal-delay removed for Streamlit compatibility */

/* ================================================
   RESPONSIVE DESIGN
   ================================================ */

@media (max-width: 1024px) {
  .steps-grid {
    grid-template-columns: 1fr;
    max-width: 440px;
    margin-left: auto;
    margin-right: auto;
  }

  .steps-grid::before {
    display: none;
  }

  .feature-row,
  .feature-row-reverse {
    grid-template-columns: 1fr;
    gap: var(--sp-xl);
  }

  .feature-row .feature-img-col,
  .feature-row-reverse .feature-img-col,
  .feature-row .feature-text-col,
  .feature-row-reverse .feature-text-col {
    order: 0;
  }

  .feature-img-col {
    order: -1 !important;
  }

  .feature-number {
    font-size: 5rem;
    opacity: 0.025;
    right: 12px !important;
    left: auto !important;
  }

  .feature-connector {
    display: none;
  }

  .feature-mockup-wrap {
    max-width: 560px;
    margin: 0 auto;
  }

  .feature-mockup {
    order: -1;
    max-width: 100%;
  }

  .feature-desc {
    max-width: 100%;
  }

  .generator-grid {
    grid-template-columns: 1fr;
  }

  .preview-panel {
    position: static;
  }

  .nav-links {
    display: none;
  }
}

@media (max-width: 768px) {
  :root {
    --nav-height: 56px;
  }

  .hero-section {
    min-height: auto;
    padding: calc(var(--nav-height) + var(--sp-3xl)) var(--sp-md) var(--sp-2xl);
  }

  .hero-title {
    font-size: 2.25rem;
  }

  .hero-geo {
    display: none;
  }

  .steps-section,
  .features-section,
  .generator-section {
    padding: var(--sp-2xl) var(--sp-md);
  }

  .section-heading-wrap {
    margin-bottom: var(--sp-xl);
  }

  .footer-inner {
    flex-direction: column;
    text-align: center;
  }

  .footer-links {
    gap: var(--sp-md);
  }

  .feature-row {
    margin-top: var(--sp-2xl);
  }
}

@media (max-width: 480px) {
  .btn {
    padding: 12px 24px;
    font-size: 0.875rem;
    width: 100%;
  }

  .hero-actions {
    flex-direction: column;
  }

  .hero-tag {
    font-size: 0.75rem;
  }

  .feature-mockup {
    padding: 10px;
  }

  .mockup-body {
    min-height: 200px;
  }

  .form-panel,
  .preview-panel {
    padding: var(--sp-md);
  }

  .step-card {
    padding: var(--sp-lg);
  }
}

/* Streamlit column overrides for generator grid */
.generator-grid [data-testid="stHorizontalBlock"] {
  gap: var(--sp-2xl) !important;
}
.generator-grid [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
  padding: 0 !important;
}
</style>

""", unsafe_allow_html=True)

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

st.markdown("""<div id="top"></div>""", unsafe_allow_html=True)


st.markdown("""
<nav class="nav-bar scrolled" style="position: relative; margin-bottom: 24px;">
    <div class="nav-inner">
        <div class="nav-brand">
            <div class="nav-logo-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="12,2 22,8.5 22,15.5 12,22 2,15.5 2,8.5"/>
                </svg>
            </div>
            <span class="nav-logo-text">智能培训设计器</span>
        </div>
        <div class="nav-links">
            <a href="#features" class="nav-link">功能介绍</a>
        </div>
    </div>
</nav>
""", unsafe_allow_html=True)



st.markdown("""
<section class="hero-section" style="min-height: auto; padding: 3rem 1.5rem 4rem;">
    <div class="section-grid-overlay"></div>
    <div class="hero-glow"></div>
    <div class="hero-geo"></div>
    <div class="hero-container">
        <div class="hero-tag">
            <span class="hero-tag-icon">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20,6 9,17 4,12"/>
                </svg>
            </span>
            <span>企业培训智能化平台</span>
        </div>
        <h1 class="hero-title">
            从产品到培训，<br><em>一步到位</em>
        </h1>
        <p class="hero-subtitle">
            只需输入产品信息，描述核心功能与场景，即可自动生成全套培训方案。从课程蓝图到1V1点评，让产品培训事半功倍。
        </p>
        <div class="hero-actions">
            <a href="#generator" class="btn btn-primary">立即体验</a>
            <a href="#features" class="btn btn-outline">了解功能</a>
        </div>
    </div>
</section>
""", unsafe_allow_html=True)



st.markdown("""
<section class="steps-section" style="padding: 4rem 1.5rem;">
    <div class="section-grid-overlay"></div>
    <div class="container-wide">
        <div class="section-heading-wrap">
            <h2 class="section-heading-lg">三步生成培训方案</h2>
            <p class="section-desc">从输入到输出，全程自动化智能化</p>
        </div>
        <div class="steps-grid">
            <div class="step-card">
                <div class="step-number">1</div>
                <h3 class="step-title">输入产品信息</h3>
                <p class="step-desc">填写产品名称、核心功能与目标人群，AI 自动解析产品特性</p>
            </div>
            <div class="step-card">
                <div class="step-number">2</div>
                <h3 class="step-title">选择培训场景</h3>
                <p class="step-desc">指定培训对象、时长与输出模块，灵活适配不同需求</p>
            </div>
            <div class="step-card">
                <div class="step-number">3</div>
                <h3 class="step-title">一键生成输出</h3>
                <p class="step-desc">获得大纲、PPT、试题等全套材料，直接投入使用</p>
            </div>
        </div>
    </div>
</section>
<div class="gradient-divider"></div>
""", unsafe_allow_html=True)


st.markdown("""
<section class="features-section" id="features">
    <div class="container-wide">
        <div class="section-heading-wrap">
            <h2 class="section-heading-lg">覆盖全链路培训需求</h2>
            <p class="section-desc">从课程规划到效果评估，一站式生成完整培训方案</p>
        </div>
        <div class="feature-wrapper">
            <div class="feature-number">01</div>
            <div class="feature-row">
                <div class="feature-text-col">
                    <span class="feature-badge">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2L2 7l10 5 10-5-10-5z"/></svg>
                        智能生成
                    </span>
                    <h3 class="feature-title">课程大纲自动构建</h3>
                    <p class="feature-desc">基于产品特性自动生成结构化课程目录，包含学习目标、知识模块和课时分配，让培训体系清晰可控。</p>
                </div>
                <div class="feature-img-col">
                    <div class="feature-mockup-wrap">
                        <div class="feature-mockup">
                            <div class="mockup-header">
                                <span class="mockup-dot"></span>
                                <span class="mockup-dot"></span>
                                <span class="mockup-dot"></span>
                            </div>
                            <div class="mockup-body">
                                <div class="mockup-sidebar">
                                    <div class="mockup-line short"></div>
                                    <div class="mockup-line"></div>
                                    <div class="mockup-line"></div>
                                    <div class="mockup-line"></div>
                                    <div class="mockup-line short"></div>
                                </div>
                                <div class="mockup-main">
                                    <div class="mockup-title">Course Outline</div>
                                    <div class="mockup-list">
                                        <div class="mockup-list-item"><span class="mockup-num">1</span><span class="mockup-text">产品概述与核心价值</span></div>
                                        <div class="mockup-list-item"><span class="mockup-num">2</span><span class="mockup-text">核心功能模块讲解</span></div>
                                        <div class="mockup-list-item active"><span class="mockup-num">3</span><span class="mockup-text">实战场景演练</span></div>
                                        <div class="mockup-list-item"><span class="mockup-num">4</span><span class="mockup-text">考核与总结</span></div>
                                    </div>
                                    <div class="mockup-button">+ 添加课时</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="feature-connector">
            <div class="feature-connector-line"></div>
            <div class="feature-connector-dot"></div>
        </div>
        <div class="feature-wrapper">
            <div class="feature-number">02</div>
            <div class="feature-row feature-row-reverse">
                <div class="feature-img-col">
                    <div class="feature-mockup-wrap">
                        <div class="feature-mockup">
                            <div class="mockup-header">
                                <span class="mockup-dot"></span>
                                <span class="mockup-dot"></span>
                                <span class="mockup-dot"></span>
                            </div>
                            <div class="mockup-body ppt-body">
                                <div class="ppt-nav">
                                    <div class="ppt-nav-item"><span>1</span></div>
                                    <div class="ppt-nav-item active"><span>2</span></div>
                                    <div class="ppt-nav-item"><span>3</span></div>
                                    <div class="ppt-nav-item"><span>4</span></div>
                                    <div class="ppt-nav-item"><span>5</span></div>
                                </div>
                                <div class="ppt-main">
                                    <div class="ppt-main-tabs">
                                        <span class="ppt-main-tab active">幻灯片</span>
                                        <span class="ppt-main-tab">大纲</span>
                                    </div>
                                    <div class="ppt-slide-preview">
                                        <div class="ppt-slide-topbar">
                                            <span class="ppt-slide-section-num">02</span>
                                            <span class="ppt-slide-section-label">核心功能模块</span>
                                        </div>
                                        <div class="ppt-slide-canvas">
                                            <div class="ppt-canvas-col">
                                                <div class="ppt-feat-block">
                                                    <div class="ppt-feat-icon-wrap"><div class="ppt-feat-icon"></div></div>
                                                    <div class="ppt-feat-text">
                                                        <div class="ppt-feat-name">智能数据看板</div>
                                                        <div class="ppt-feat-desc">实时监控，自动生成分析</div>
                                                    </div>
                                                </div>
                                                <div class="ppt-feat-block">
                                                    <div class="ppt-feat-icon-wrap"><div class="ppt-feat-icon"></div></div>
                                                    <div class="ppt-feat-text">
                                                        <div class="ppt-feat-name">自动化工作流</div>
                                                        <div class="ppt-feat-desc">拖拽配置，零代码搭建</div>
                                                    </div>
                                                </div>
                                                <div class="ppt-feat-block">
                                                    <div class="ppt-feat-icon-wrap"><div class="ppt-feat-icon"></div></div>
                                                    <div class="ppt-feat-text">
                                                        <div class="ppt-feat-name">多端协同编辑</div>
                                                        <div class="ppt-feat-desc">PC / 移动端实时同步</div>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="ppt-canvas-visual">
                                                <div class="ppt-visual-chart">
                                                    <div class="ppt-visual-bar" style="height:40%"></div>
                                                    <div class="ppt-visual-bar" style="height:65%"></div>
                                                    <div class="ppt-visual-bar active" style="height:90%"></div>
                                                    <div class="ppt-visual-bar" style="height:55%"></div>
                                                    <div class="ppt-visual-bar" style="height:72%"></div>
                                                </div>
                                                <div class="ppt-visual-ring">
                                                    <div class="ppt-ring-track"></div>
                                                    <span class="ppt-ring-value">78%</span>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="ppt-slide-footer">企业培训智能化平台 · 产品认知培训</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="feature-text-col">
                    <span class="feature-badge">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="3" width="18" height="18" rx="2"/></svg>
                        一键输出
                    </span>
                    <h3 class="feature-title">培训 PPT 即开即用</h3>
                    <p class="feature-desc">自动生成结构完整、版式专业的演示文稿，包含封面、目录、内容页和总结，可直接用于现场培训。</p>
                </div>
            </div>
        </div>

        <div class="feature-connector">
            <div class="feature-connector-line"></div>
            <div class="feature-connector-dot"></div>
        </div>
        <div class="feature-wrapper">
            <div class="feature-number">03</div>
            <div class="feature-row">
                <div class="feature-text-col">
                    <span class="feature-badge">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
                        多维度
                    </span>
                    <h3 class="feature-title">智能考核与评估</h3>
                    <p class="feature-desc">生成多类型考核题目，支持自动评分和成绩分析，帮助培训管理者科学评估培训效果。</p>
                </div>
                <div class="feature-img-col">
                    <div class="feature-mockup-wrap">
                        <div class="feature-mockup">
                            <div class="mockup-header">
                                <span class="mockup-dot"></span>
                                <span class="mockup-dot"></span>
                                <span class="mockup-dot"></span>
                            </div>
                            <div class="mockup-body dashboard-body">
                                <div class="dashboard-row">
                                    <div class="dashboard-card">
                                        <div class="dashboard-label">学习进度</div>
                                        <div class="dashboard-ring"><span>75%</span></div>
                                    </div>
                                    <div class="dashboard-card">
                                        <div class="dashboard-label">考核得分</div>
                                        <div class="dashboard-ring"><span>82</span></div>
                                    </div>
                                    <div class="dashboard-card">
                                        <div class="dashboard-label">完成评估</div>
                                        <div class="dashboard-ring"><span>50%</span></div>
                                    </div>
                                </div>
                                <div class="dashboard-row">
                                    <div class="dashboard-card wide">
                                        <div class="dashboard-label">成绩趋势</div>
                                        <div class="dashboard-chart">
                                            <div class="bar" style="height:40%"></div>
                                            <div class="bar" style="height:55%"></div>
                                            <div class="bar" style="height:50%"></div>
                                            <div class="bar" style="height:75%"></div>
                                            <div class="bar" style="height:65%"></div>
                                            <div class="bar" style="height:90%"></div>
                                        </div>
                                    </div>
                                    <div class="dashboard-card">
                                        <div class="dashboard-label">通过率</div>
                                        <div class="dashboard-ring"><span>62%</span></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="feature-connector">
            <div class="feature-connector-line"></div>
            <div class="feature-connector-dot"></div>
        </div>
        <div class="feature-wrapper">
            <div class="feature-number">04</div>
            <div class="feature-row feature-row-reverse">
                <div class="feature-img-col">
                    <div class="feature-mockup-wrap">
                        <div class="feature-mockup">
                            <div class="mockup-header">
                                <span class="mockup-dot"></span>
                                <span class="mockup-dot"></span>
                                <span class="mockup-dot"></span>
                            </div>
                            <div class="mockup-body practice-body">
                                <div class="practice-sidebar">
                                    <div class="practice-title">实操模拟器</div>
                                    <div class="practice-item active"><span class="practice-dot"></span>交互操作</div>
                                    <div class="practice-item"><span class="practice-dot"></span>环境配置</div>
                                    <div class="practice-item"><span class="practice-dot"></span>应用启动</div>
                                    <div class="practice-item"><span class="practice-dot"></span>错误排查</div>
                                </div>
                                <div class="practice-main">
                                    <div class="checklist-title">操作清单</div>
                                    <div class="checklist-item"><span class="check"></span>配置运行环境</div>
                                    <div class="checklist-item"><span class="check"></span>安装依赖组件</div>
                                    <div class="checklist-item"><span class="check"></span>初始化系统参数</div>
                                    <div class="checklist-item"><span class="check"></span>验证运行状态</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="feature-text-col">
                    <span class="feature-badge">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14,2 14,8 20,8"/></svg>
                        实战导向
                    </span>
                    <h3 class="feature-title">实操场景化练习</h3>
                    <p class="feature-desc">根据产品使用场景生成实战案例与操作练习，让学员在模拟环境中快速掌握核心功能。</p>
                </div>
            </div>
        </div>
    </div>
</section>

""", unsafe_allow_html=True)


# ============================================================
# 生成工作区
# ============================================================
if st.session_state.get("scroll_to_workspace", False):
    st.session_state.scroll_to_workspace = False

# 检查 API Key
if not st.session_state.api_key:
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: rgba(255,255,255,0.5); background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; margin: 1rem 0;">
        <p style="font-size: 1.1rem; margin-bottom: 0.5rem; color: rgba(255,255,255,0.85); font-weight: 600;">API Key 未配置</p>
        <p style="font-size: 0.85rem; color: rgba(255,255,255,0.45);">请在 Streamlit Cloud 后台 Settings → Secrets 中配置 DEEPSEEK_API_KEY</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

st.markdown("""
<section class="generator-section" id="generator" style="padding: 4rem 1.5rem;">
    <div class="container-generator">
        <div class="section-heading-wrap">
            <h2 class="section-heading-lg">开始生成您的培训方案</h2>
            <p class="section-desc">填写培训信息，一键生成完整培训材料</p>
        </div>
        <div class="generator-grid">
""", unsafe_allow_html=True)

left_col, right_col = st.columns([1, 1])

with left_col:
    st.markdown("""
            <div class="form-panel">
                <div class="panel-heading">
                    <span class="panel-icon">
                        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3"><rect x="3" y="3" width="18" height="18" rx="2"/></svg>
                    </span>
                    <h3>培训信息</h3>
                </div>
""", unsafe_allow_html=True)

    st.markdown('<div class="form-group">', unsafe_allow_html=True)
    st.markdown('<label class="form-label">产品名称</label>', unsafe_allow_html=True)
    product_name = st.text_input(
        "",
        value=st.session_state.product_name,
        placeholder="例如：WorkBuddy 智能设计助手",
        label_visibility="collapsed"
    )
    st.markdown('<p class="form-hint">需要设计培训方案的产品名称</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="form-group">', unsafe_allow_html=True)
    st.markdown('<label class="form-label">产品简介</label>', unsafe_allow_html=True)
    product_doc = st.text_area(
        "",
        value=st.session_state.product_doc,
        height=100,
        placeholder="简要描述产品的核心功能和定位",
        label_visibility="collapsed"
    )
    st.markdown('<p class="form-hint">简要描述产品的核心功能和定位</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="form-group">', unsafe_allow_html=True)
    st.markdown('<label class="form-label">培训对象</label>', unsafe_allow_html=True)
    training_roles = st.multiselect(
        "",
        ["实施工程师", "运维工程师", "技术支持", "销售", "客户成功", "售前工程师", "市场", "行政", "财务"],
        default=st.session_state.training_roles,
        placeholder="例如：销售团队、新员工、合作伙伴",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="form-group">', unsafe_allow_html=True)
    st.markdown('<label class="form-label">期望培训时长</label>', unsafe_allow_html=True)
    training_days = st.select_slider(
        "",
        options=list(range(1, 11)),
        value=min(st.session_state.training_days, 10),
        label_visibility="collapsed"
    )
    st.markdown(f'<p class="form-hint">当前选择：<strong>{training_days} 天</strong>（最长 10 天）</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="form-group">', unsafe_allow_html=True)
    st.markdown('<label class="form-label">产品类型</label>', unsafe_allow_html=True)
    product_type_options = ["软件", "硬件", "SaaS", "平台", "其他"]
    product_type = st.selectbox(
        "",
        product_type_options,
        index=product_type_options.index(st.session_state.product_type) if st.session_state.product_type in product_type_options else 0,
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # 保存当前输入
    st.session_state.product_name = product_name
    st.session_state.product_type = product_type
    st.session_state.training_roles = training_roles
    st.session_state.training_days = training_days
    st.session_state.product_doc = product_doc

    st.markdown("<div style='margin-top: 0.5rem;'>", unsafe_allow_html=True)
    generate_clicked = st.button(
        "生成培训材料",
        use_container_width=True,
        type="primary",
        disabled=st.session_state.is_generating
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if generate_clicked:
        if not product_name:
            st.error("请输入产品名称")
            st.stop()
        elif not training_roles:
            st.error("请选择培训对象")
            st.stop()
        else:
            st.session_state.is_generating = True
            st.session_state.generation_complete = False
            st.session_state.generated_content = {}
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


with right_col:
    st.markdown("""
            <div class="preview-panel">
                <div class="panel-heading">
                    <span class="panel-icon">
                        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
                    </span>
                    <h3>生成预览</h3>
                </div>
                <div class="preview-list">
""", unsafe_allow_html=True)

    # SVG paths for preview icons (matching designer reference)
    PREVIEW_SVGS = {
        "blueprint": '<path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/>',
        "materials": '<rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="13" y1="8" x2="19" y2="8"/>',
        "assessment": '<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>',
        "hands_on": '<circle cx="12" cy="12" r="10"/><polygon points="10,8 16,12 10,16"/>'
    }

    # 默认预览状态
    if not st.session_state.is_generating and not st.session_state.generation_complete:
        for module in ["blueprint", "materials", "assessment", "hands_on"]:
            is_selected = st.session_state.module_selection.get(module, True)
            item_class = "selected" if is_selected else ""
            st.markdown(f"""
                    <div class="preview-item {item_class}">
                        <div class="preview-icon">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">{PREVIEW_SVGS[module]}</svg>
                        </div>
                        <div class="preview-info">
                            <h4>{MODULE_LABELS[module]}</h4>
                            <p>{MODULE_DESCRIPTIONS[module]}</p>
                        </div>
                    </div>
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
        status_text.markdown("<div style='color: #22c55e; font-size: 0.85rem;'> 所有内容生成完成！</div>", unsafe_allow_html=True)
        st.session_state.generation_complete = True
        st.session_state.is_generating = False
        time.sleep(1)
        st.rerun()

    # 生成完成后显示预览
    elif st.session_state.generation_complete:
        modules_with_content = [k for k in st.session_state.module_selection.keys() if st.session_state.module_selection[k] and k in st.session_state.generated_content]

        for module in modules_with_content:
            st.markdown(f"""
                    <div class="preview-item selected">
                        <div class="preview-icon">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">{PREVIEW_SVGS[module]}</svg>
                        </div>
                        <div class="preview-info">
                            <h4>{MODULE_LABELS[module]}</h4>
                            <p>{MODULE_DESCRIPTIONS[module]}</p>
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
            label="下载完整方案",
            data=all_content,
            file_name=f"{product_name}_培训方案.md",
            mime="text/markdown",
            use_container_width=True
        )

    st.markdown("""
                </div>
            </div>
""", unsafe_allow_html=True)

st.markdown("""
        </div>
    </div>
</section>
""", unsafe_allow_html=True)

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

# ============================================================
# 页脚
# ============================================================



st.markdown("""
<footer class="footer">
    <div class="footer-inner">
        <div class="footer-brand">
            <div class="footer-logo">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                    <defs>
                        <linearGradient id="ft-grad" x1="2" y1="2" x2="22" y2="22">
                            <stop offset="0%" stop-color="#6C63FF"/>
                            <stop offset="100%" stop-color="#4A7CF6"/>
                        </linearGradient>
                    </defs>
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="url(#ft-grad)"/>
                    <path d="M2 17L12 22L22 17" stroke="url(#ft-grad)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
                </svg>
                <span class="footer-logo-text">智能培训设计器</span>
            </div>
            <p class="footer-slogan">让每一次产品培训都精准有力</p>
        </div>
        <nav class="footer-links">
            <a href="#features">功能介绍</a>
            <span class="footer-divider"></span>
            <a href="#generator">立即开始</a>
        </nav>
    </div>
</footer>
""", unsafe_allow_html=True)
