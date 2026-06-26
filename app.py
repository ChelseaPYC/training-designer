import streamlit as st
import requests
import json
import time

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
    * {
        font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    body, .stApp {
        background: #0a0e17 !important;
        color: white;
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
        font-size: 1.1rem;
        font-weight: 700;
        background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 0.05em;
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
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 27, 75, 0.6) 50%, rgba(15, 23, 42, 0.95) 100%);
        padding: 2.5rem 2rem 3rem 2rem;
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
        top: 0;
        right: 0;
        width: 60%;
        height: 100%;
        background: radial-gradient(circle at 80% 30%, rgba(129, 140, 248, 0.15) 0%, transparent 60%);
        pointer-events: none;
    }
    .hero-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        max-width: 1200px;
        margin: 0 auto;
        position: relative;
        gap: 2.5rem;
    }
    .hero-content {
        flex: 1;
        min-width: 0;
    }
    .hero-graphic {
        flex: 0 0 360px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .hero-title {
        font-size: 2.6rem;
        font-weight: 700;
        margin-bottom: 1rem;
        line-height: 1.25;
        color: white;
        position: relative;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: rgba(199, 210, 254, 0.75);
        font-weight: 400;
        line-height: 1.7;
        max-width: 480px;
        position: relative;
    }
    .hero-buttons {
        margin-top: 1.5rem;
        display: flex;
        gap: 1rem;
        position: relative;
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
        background: rgba(10, 14, 23, 0.6);
        padding: 1.5rem 2rem;
        margin: 0 -1rem;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .steps-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        max-width: 1200px;
        margin: 0 auto 1.25rem auto;
    }
    .steps-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: white;
    }
    .steps-subtitle {
        font-size: 0.8rem;
        color: rgba(255,255,255,0.45);
    }
    .steps-container {
        display: flex;
        gap: 1rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    .step-card {
        flex: 1;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1.25rem;
        transition: all 0.2s;
    }
    .step-card:hover {
        background: rgba(255,255,255,0.07);
        border-color: rgba(129, 140, 248, 0.25);
    }
    .step-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 26px;
        height: 26px;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    .step-name {
        font-size: 0.95rem;
        font-weight: 600;
        color: white;
        margin-bottom: 0.3rem;
    }
    .step-desc {
        font-size: 0.75rem;
        color: rgba(255,255,255,0.5);
        line-height: 1.5;
    }
    
    /* ===== 功能模块展示 - 左右交替布局 ===== */
    .features-section {
        background: rgba(10, 14, 23, 0.4);
        padding: 2.5rem 2rem;
        margin: 0 -1rem;
    }
    .features-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: white;
        margin-bottom: 0.5rem;
    }
    .features-subtitle {
        font-size: 0.85rem;
        color: rgba(255,255,255,0.5);
        margin-bottom: 2rem;
    }
    .feature-row {
        display: flex;
        align-items: center;
        gap: 2.5rem;
        margin-bottom: 1.5rem;
        max-width: 1200px;
        margin-left: auto;
        margin-right: auto;
    }
    .feature-content {
        flex: 1;
    }
    .feature-tag {
        display: inline-block;
        padding: 0.25rem 0.7rem;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }
    .feature-tag.orange {
        background: rgba(192, 132, 252, 0.15);
        color: #e9d5ff;
    }
    .feature-tag.blue {
        background: rgba(129, 140, 248, 0.15);
        color: #c7d2fe;
    }
    .feature-name {
        font-size: 1.15rem;
        font-weight: 600;
        color: white;
        margin-bottom: 0.4rem;
    }
    .feature-desc {
        font-size: 0.85rem;
        color: rgba(255,255,255,0.55);
        line-height: 1.6;
    }
    .feature-preview {
        flex: 1;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1.5rem;
        min-height: 180px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }
    
    /* ===== 工作区 ===== */
    .workspace-section {
        background: rgba(10, 14, 23, 0.8);
        padding: 2rem 2rem;
        margin: 0 -1rem;
        min-height: auto;
        border-top: 1px solid rgba(255,255,255,0.05);
    }
    .workspace-header {
        max-width: 1200px;
        margin: 0 auto 1.5rem auto;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .workspace-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: white;
    }
    .workspace-subtitle {
        font-size: 0.8rem;
        color: rgba(255,255,255,0.45);
    }
    
    /* 左侧输入区 */
    .input-panel {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1.5rem;
        height: 100%;
    }
    .input-panel-title {
        font-size: 1rem;
        font-weight: 600;
        color: white;
        margin-bottom: 1.25rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .form-label {
        font-size: 0.78rem;
        font-weight: 500;
        color: rgba(255,255,255,0.75);
        margin-bottom: 0.4rem;
    }
    .form-input {
        margin-bottom: 1rem;
    }
    .form-hint {
        font-size: 0.72rem;
        color: rgba(255,255,255,0.35);
        margin-top: 0.2rem;
    }
    .generate-btn {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.85rem !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        width: 100% !important;
        cursor: pointer !important;
        transition: all 0.2s !important;
        box-shadow: 0 4px 16px rgba(79, 70, 229, 0.35) !important;
    }
    .generate-btn:hover {
        background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%) !important;
        box-shadow: 0 6px 22px rgba(79, 70, 229, 0.45) !important;
    }
    
    /* 右侧预览区 */
    .preview-panel {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1.5rem;
        height: 100%;
    }
    .preview-panel-title {
        font-size: 1rem;
        font-weight: 600;
        color: white;
        margin-bottom: 1.25rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        display: flex;
        align-items: center;
        gap: 0.5rem;
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
    .stSlider > div > div {
        background: rgba(255,255,255,0.1) !important;
    }
    .stSlider [role="slider"] {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        border: 2px solid #0a0e17 !important;
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
    @media (max-width: 768px) {
        .feature-row {
            flex-direction: column;
            gap: 1rem;
        }
        .hero-container {
            flex-direction: column;
        }
        .hero-graphic {
            display: none;
        }
        .steps-container {
            flex-direction: column;
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
    st.markdown('<div class="nav-brand">企业培训智能化平台</div>', unsafe_allow_html=True)

# ============================================================
# Hero 区域 - 配图 + 跳转按钮
# ============================================================
st.markdown("""
<div class="hero-section">
    <div class="hero-container">
        <div class="hero-content">
            <div class="hero-title">从产品到培训，<br>一步到位</div>
            <div class="hero-subtitle">只需输入产品信息，描述核心功能与场景，即可自动生成全套培训方案，从蓝图到1V1点评，让产品培训事半功倍。</div>
            <div class="hero-buttons">
                <a href="#workspace" class="hero-btn-primary">立即体验</a>
                <a href="#features" class="hero-btn-secondary">了解功能</a>
            </div>
        </div>
        <div class="hero-graphic">
            <svg viewBox="0 0 380 260" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:380px;filter:drop-shadow(0 25px 50px rgba(0,0,0,0.4));">
                <defs>
                    <linearGradient id="hero-bg" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#1e1b4b;stop-opacity:0.9"/>
                        <stop offset="100%" style="stop-color:#312e81;stop-opacity:0.8"/>
                    </linearGradient>
                    <linearGradient id="hero-card" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:rgba(255,255,255,0.12)"/>
                        <stop offset="100%" style="stop-color:rgba(255,255,255,0.05)"/>
                    </linearGradient>
                    <linearGradient id="hero-accent" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#818cf8"/>
                        <stop offset="100%" style="stop-color:#c084fc"/>
                    </linearGradient>
                </defs>
                <rect width="380" height="260" rx="20" fill="url(#hero-bg)" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
                
                <!-- 顶部状态栏 -->
                <rect x="20" y="20" width="340" height="40" rx="10" fill="url(#hero-card)"/>
                <circle cx="45" cy="40" r="8" fill="#4f46e5"/>
                <rect x="62" y="36" width="120" height="6" rx="3" fill="rgba(255,255,255,0.3)"/>
                <rect x="62" y="46" width="80" height="4" rx="2" fill="rgba(255,255,255,0.15)"/>
                <rect x="280" y="34" width="65" height="12" rx="6" fill="rgba(34,197,94,0.3)"/>
                
                <!-- 左侧课程大纲 -->
                <rect x="20" y="75" width="170" height="165" rx="12" fill="url(#hero-card)"/>
                <rect x="35" y="92" width="80" height="6" rx="3" fill="rgba(255,255,255,0.35)"/>
                <rect x="35" y="108" width="140" height="3" rx="1.5" fill="rgba(255,255,255,0.12)"/>
                <rect x="35" y="118" width="120" height="3" rx="1.5" fill="rgba(255,255,255,0.12)"/>
                <rect x="35" y="135" width="12" height="12" rx="3" fill="#4f46e5"/>
                <rect x="55" y="138" width="100" height="4" rx="2" fill="rgba(255,255,255,0.25)"/>
                <rect x="35" y="155" width="12" height="12" rx="3" fill="#22c55e"/>
                <rect x="55" y="158" width="110" height="4" rx="2" fill="rgba(255,255,255,0.25)"/>
                <rect x="35" y="175" width="12" height="12" rx="3" fill="#f59e0b"/>
                <rect x="55" y="178" width="90" height="4" rx="2" fill="rgba(255,255,255,0.25)"/>
                <rect x="35" y="195" width="12" height="12" rx="3" fill="rgba(255,255,255,0.15)"/>
                <rect x="55" y="198" width="105" height="4" rx="2" fill="rgba(255,255,255,0.25)"/>
                
                <!-- 右侧卡片 -->
                <rect x="205" y="75" width="155" height="95" rx="12" fill="url(#hero-card)"/>
                <circle cx="235" cy="105" r="14" fill="url(#hero-accent)" opacity="0.8"/>
                <rect x="258" y="98" width="85" height="6" rx="3" fill="rgba(255,255,255,0.3)"/>
                <rect x="258" y="110" width="60" height="4" rx="2" fill="rgba(255,255,255,0.15)"/>
                <rect x="220" y="135" width="125" height="4" rx="2" fill="rgba(255,255,255,0.1)"/>
                <rect x="220" y="145" width="100" height="4" rx="2" fill="rgba(255,255,255,0.1)"/>
                
                <!-- 底部进度 -->
                <rect x="205" y="185" width="155" height="55" rx="12" fill="url(#hero-card)"/>
                <rect x="220" y="202" width="100" height="5" rx="2.5" fill="rgba(255,255,255,0.1)"/>
                <rect x="220" y="202" width="75" height="5" rx="2.5" fill="url(#hero-accent)"/>
                <rect x="220" y="218" width="125" height="3" rx="1.5" fill="rgba(255,255,255,0.1)"/>
                <text x="340" y="222" font-size="11" fill="rgba(255,255,255,0.5)" text-anchor="end" font-family="system-ui,sans-serif">75%</text>
            </svg>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 跳转锚点占位
st.markdown("<div id='workspace-anchor'></div>", unsafe_allow_html=True)

# ============================================================
# 三步流程
# ============================================================
st.markdown("""
<div class="steps-section">
    <div class="steps-header">
        <div>
            <div class="steps-title">三步生成培训方案</div>
            <div class="steps-subtitle">从输入到输出，全程自动化智能化</div>
        </div>
    </div>
    <div class="steps-container">
        <div class="step-card">
            <div class="step-number">1</div>
            <div class="step-name">输入产品信息</div>
            <div class="step-desc">填写产品名称、核心功能简介</div>
        </div>
        <div class="step-card">
            <div class="step-number">2</div>
            <div class="step-name">选择培训场景</div>
            <div class="step-desc">指定对象和期望时长</div>
        </div>
        <div class="step-card">
            <div class="step-number">3</div>
            <div class="step-name">一键生成输出</div>
            <div class="step-desc">获得大纲、PPT、试题等材料</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 功能模块展示 - 左右交替布局
# ============================================================
st.html("""
<div class="features-section" id="features">
    <div style="text-align:center;margin-bottom:1.5rem;">
        <div class="features-title">覆盖全链路培训需求</div>
        <div class="features-subtitle">从规划到考核，为您生成体系化的完整培训方案</div>
    </div>

    <div class="feature-row">
        <div class="feature-content">
            <div class="feature-tag blue">智能生成</div>
            <div class="feature-name">课程大纲自动构建</div>
            <div class="feature-desc">基于产品特性自动生成结构化课程目录，包含学习目标、知识模块和课时分配。</div>
        </div>
        <div class="feature-preview">
            <svg viewBox="0 0 320 200" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:320px;">
                <defs>
                    <linearGradient id="outline-bg" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:rgba(129,140,248,0.15)"/>
                        <stop offset="100%" style="stop-color:rgba(192,132,252,0.08)"/>
                    </linearGradient>
                </defs>
                <rect x="10" y="10" width="300" height="180" rx="14" fill="url(#outline-bg)" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>
                <rect x="30" y="30" width="100" height="8" rx="4" fill="rgba(255,255,255,0.35)"/>
                <rect x="30" y="48" width="180" height="4" rx="2" fill="rgba(255,255,255,0.12)"/>
                
                <rect x="30" y="70" width="12" height="12" rx="3" fill="#4f46e5"/>
                <rect x="50" y="74" width="120" height="4" rx="2" fill="rgba(255,255,255,0.25)"/>
                <rect x="50" y="84" width="90" height="3" rx="1.5" fill="rgba(255,255,255,0.1)"/>
                
                <rect x="30" y="105" width="12" height="12" rx="3" fill="#22c55e"/>
                <rect x="50" y="109" width="130" height="4" rx="2" fill="rgba(255,255,255,0.25)"/>
                <rect x="50" y="119" width="100" height="3" rx="1.5" fill="rgba(255,255,255,0.1)"/>
                
                <rect x="30" y="140" width="12" height="12" rx="3" fill="#f59e0b"/>
                <rect x="50" y="144" width="110" height="4" rx="2" fill="rgba(255,255,255,0.25)"/>
                <rect x="50" y="154" width="80" height="3" rx="1.5" fill="rgba(255,255,255,0.1)"/>
                
                <rect x="200" y="90" width="90" height="50" rx="8" fill="rgba(255,255,255,0.05)" stroke="rgba(129,140,248,0.2)" stroke-width="1"/>
                <rect x="215" y="108" width="60" height="4" rx="2" fill="rgba(255,255,255,0.25)"/>
                <rect x="215" y="118" width="40" height="3" rx="1.5" fill="rgba(255,255,255,0.12)"/>
            </svg>
        </div>
    </div>

    <div class="feature-row">
        <div class="feature-preview">
            <svg viewBox="0 0 320 200" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:320px;">
                <defs>
                    <linearGradient id="ppt-bg" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:rgba(245,158,11,0.12)"/>
                        <stop offset="100%" style="stop-color:rgba(249,115,22,0.06)"/>
                    </linearGradient>
                </defs>
                <rect x="10" y="10" width="300" height="180" rx="14" fill="url(#ppt-bg)" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>
                
                <!-- 幻灯片列表 -->
                <rect x="25" y="35" width="50" height="35" rx="6" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
                <rect x="32" y="45" width="36" height="4" rx="2" fill="rgba(255,255,255,0.25)"/>
                <rect x="32" y="53" width="28" height="3" rx="1.5" fill="rgba(255,255,255,0.12)"/>
                
                <rect x="25" y="80" width="50" height="35" rx="6" fill="rgba(255,255,255,0.05)" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>
                <rect x="32" y="90" width="36" height="4" rx="2" fill="rgba(255,255,255,0.18)"/>
                
                <rect x="25" y="125" width="50" height="35" rx="6" fill="rgba(255,255,255,0.05)" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>
                <rect x="32" y="135" width="36" height="4" rx="2" fill="rgba(255,255,255,0.18)"/>
                
                <!-- 主幻灯片 -->
                <rect x="90" y="35" width="205" height="125" rx="10" fill="rgba(15,23,42,0.6)" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
                <rect x="110" y="55" width="120" height="6" rx="3" fill="rgba(255,255,255,0.35)"/>
                <rect x="110" y="70" width="165" height="3" rx="1.5" fill="rgba(255,255,255,0.12)"/>
                <rect x="110" y="80" width="150" height="3" rx="1.5" fill="rgba(255,255,255,0.12)"/>
                <rect x="110" y="90" width="140" height="3" rx="1.5" fill="rgba(255,255,255,0.12)"/>
                
                <rect x="110" y="110" width="80" height="30" rx="6" fill="rgba(79,70,229,0.25)"/>
                <circle cx="220" cy="125" r="15" fill="rgba(34,197,94,0.25)"/>
                <path d="M212,125 L218,131 L230,119" fill="none" stroke="#22c55e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <div class="feature-content">
            <div class="feature-tag orange">一键输出</div>
            <div class="feature-name">培训 PPT 即开即用</div>
            <div class="feature-desc">自动生成结构完整、版式专业的演示文稿，包含封面、目录、内容页和总结。</div>
        </div>
    </div>

    <div class="feature-row">
        <div class="feature-content">
            <div class="feature-tag blue">多维度</div>
            <div class="feature-name">智能考核与评估</div>
            <div class="feature-desc">生成多类型考核题目，支持自动评分和成绩分析，帮助评估培训效果。</div>
        </div>
        <div class="feature-preview">
            <svg viewBox="0 0 320 200" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:320px;">
                <defs>
                    <linearGradient id="dash-bg" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:rgba(34,197,94,0.1)"/>
                        <stop offset="100%" style="stop-color:rgba(59,130,246,0.08)"/>
                    </linearGradient>
                </defs>
                <rect x="10" y="10" width="300" height="180" rx="14" fill="url(#dash-bg)" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>
                
                <!-- 左侧分数 -->
                <circle cx="90" cy="95" r="50" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="8"/>
                <circle cx="90" cy="95" r="50" fill="none" stroke="url(#hero-accent)" stroke-width="8" stroke-dasharray="220 314" stroke-linecap="round"/>
                <text x="90" y="90" font-size="22" font-weight="700" fill="white" text-anchor="middle" font-family="system-ui,sans-serif">86</text>
                <text x="90" y="110" font-size="10" fill="rgba(255,255,255,0.4)" text-anchor="middle" font-family="system-ui,sans-serif">平均分</text>
                
                <!-- 右侧柱状图 -->
                <rect x="170" y="55" width="18" height="75" rx="4" fill="rgba(129,140,248,0.4)"/>
                <rect x="198" y="75" width="18" height="55" rx="4" fill="rgba(129,140,248,0.3)"/>
                <rect x="226" y="45" width="18" height="85" rx="4" fill="rgba(192,132,252,0.5)"/>
                <rect x="254" y="65" width="18" height="65" rx="4" fill="rgba(129,140,248,0.35)"/>
                
                <!-- 底部指标 -->
                <rect x="45" y="160" width="70" height="20" rx="6" fill="rgba(255,255,255,0.05)"/>
                <rect x="125" y="160" width="70" height="20" rx="6" fill="rgba(255,255,255,0.05)"/>
                <rect x="205" y="160" width="70" height="20" rx="6" fill="rgba(255,255,255,0.05)"/>
            </svg>
        </div>
    </div>

    <div class="feature-row">
        <div class="feature-preview">
            <svg viewBox="0 0 320 200" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:320px;">
                <defs>
                    <linearGradient id="practice-bg" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:rgba(59,130,246,0.12)"/>
                        <stop offset="100%" style="stop-color:rgba(99,102,241,0.06)"/>
                    </linearGradient>
                </defs>
                <rect x="10" y="10" width="300" height="180" rx="14" fill="url(#practice-bg)" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>
                
                <!-- 电脑屏幕 -->
                <rect x="55" y="35" width="210" height="120" rx="10" fill="rgba(15,23,42,0.7)" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
                <rect x="55" y="35" width="210" height="18" rx="10" fill="rgba(255,255,255,0.05)"/>
                <circle cx="70" cy="44" r="3" fill="#ef4444"/>
                <circle cx="82" cy="44" r="3" fill="#f59e0b"/>
                <circle cx="94" cy="44" r="3" fill="#22c55e"/>
                
                <!-- 屏幕内容 -->
                <rect x="75" y="65" width="60" height="40" rx="6" fill="rgba(79,70,229,0.2)"/>
                <rect x="85" y="78" width="40" height="3" rx="1.5" fill="rgba(255,255,255,0.25)"/>
                <rect x="85" y="86" width="30" height="3" rx="1.5" fill="rgba(255,255,255,0.12)"/>
                
                <rect x="150" y="65" width="95" height="4" rx="2" fill="rgba(255,255,255,0.15)"/>
                <rect x="150" y="75" width="85" height="4" rx="2" fill="rgba(255,255,255,0.15)"/>
                <rect x="150" y="85" width="95" height="4" rx="2" fill="rgba(255,255,255,0.15)"/>
                
                <rect x="75" y="120" width="170" height="20" rx="6" fill="rgba(34,197,94,0.15)"/>
                <rect x="85" y="128" width="100" height="4" rx="2" fill="rgba(255,255,255,0.25)"/>
                <circle cx="235" cy="130" r="6" fill="#22c55e"/>
                <polyline points="232,130 235,133 240,127" fill="none" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                
                <!-- 键盘底座 -->
                <rect x="110" y="160" width="100" height="8" rx="4" fill="rgba(255,255,255,0.1)"/>
            </svg>
        </div>
        <div class="feature-content">
            <div class="feature-tag orange">实战导向</div>
            <div class="feature-name">实操场景化练习</div>
            <div class="feature-desc">根据产品使用场景生成实战案例与操作练习，让学员在模拟环境中掌握核心功能。</div>
        </div>
    </div>
</div>
""")

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
        <div>
            <div class="workspace-title">开始生成您的培训方案</div>
            <div class="workspace-subtitle">填写左侧培训信息，右侧实时预览生成内容</div>
        </div>
    </div>
</div>
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
            <div class="footer-copyright">v4.8 | 由 ChelseaPYC 构建</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

left_col, right_col = st.columns([1, 1])

with left_col:
    # 左侧输入面板
    st.markdown("""
    <div class="input-panel">
        <div class="input-panel-title">📝 培训信息</div>
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
        <div class="preview-panel-title">👁️ 生成预览</div>
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
            <div class="footer-copyright">v4.8 | 由 ChelseaPYC 构建</div>
        </div>
    </div>
""", unsafe_allow_html=True)
