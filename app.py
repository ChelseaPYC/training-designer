import streamlit as st
import requests
import json
import time

# ============================================================
# 配置区：默认 API Key（可选，填入后用户无需手动设置）
# ============================================================
DEFAULT_API_KEY = ""  # 用户使用时手动输入，不要硬编码到代码中

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
    
    .main .block-container {
        padding: 0 1rem 2rem 1rem;
        max-width: 100%;
    }
    
    /* ===== 隐藏 Streamlit 默认元素 ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header {visibility: hidden;}
    
    /* ===== 顶部导航栏 ===== */
    .nav-bar {
        background: #0a0e1a;
        padding: 0.75rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: -1rem -1rem 0 -1rem;
        position: sticky;
        top: 0;
        z-index: 100;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .nav-brand {
        font-size: 1rem;
        font-weight: 500;
        color: white;
        letter-spacing: 0.05em;
    }
    .nav-btn {
        background: transparent;
        border: 1px solid rgba(255,255,255,0.2);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 6px;
        font-size: 0.8rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    .nav-btn:hover {
        background: rgba(255,255,255,0.1);
        border-color: rgba(255,255,255,0.3);
    }
    
    /* ===== Hero 区域 ===== */
    .hero-section {
        background: linear-gradient(135deg, #0a0e1a 0%, #121933 50%, #0a0e1a 100%);
        padding: 3rem 2rem 3.5rem 2rem;
        color: white;
        text-align: left;
        position: relative;
        overflow: hidden;
        margin: 0 -1rem;
    }
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 50%;
        height: 100%;
        background: radial-gradient(circle at 80% 50%, rgba(59, 130, 246, 0.08) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        max-width: 1200px;
        margin: 0 auto;
        position: relative;
        gap: 3rem;
    }
    .hero-content {
        flex: 1;
        min-width: 0;
    }
    .hero-graphic {
        flex: 0 0 320px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 1rem;
        line-height: 1.3;
        color: white;
        position: relative;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: rgba(255,255,255,0.55);
        font-weight: 400;
        line-height: 1.7;
        max-width: 500px;
        position: relative;
    }
    .hero-buttons {
        margin-top: 1.5rem;
        display: flex;
        gap: 1rem;
        position: relative;
    }
    .hero-btn-primary {
        background: #1e3a5f;
        color: white;
        padding: 0.8rem 2rem;
        border-radius: 8px;
        font-size: 0.95rem;
        font-weight: 500;
        border: none;
        cursor: pointer;
        transition: all 0.2s;
    }
    .hero-btn-primary:hover {
        background: #2563eb;
    }
    .hero-btn-secondary {
        background: transparent;
        color: rgba(255,255,255,0.7);
        padding: 0.8rem 2rem;
        border-radius: 8px;
        font-size: 0.95rem;
        font-weight: 500;
        border: 1px solid rgba(255,255,255,0.2);
        cursor: pointer;
        transition: all 0.2s;
    }
    .hero-btn-secondary:hover {
        border-color: rgba(255,255,255,0.4);
        color: white;
    }
    
    /* ===== Hero 区域 Streamlit 按钮覆盖 ===== */
    .hero-section + div .stButton > button[kind="primary"] {
        background: #1e3a5f !important;
        color: white !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        border-radius: 8px !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
    }
    .hero-section + div .stButton > button[kind="primary"]:hover {
        background: #2563eb !important;
    }
    .hero-section + div .stButton > button[kind="secondary"] {
        background: transparent !important;
        color: rgba(255,255,255,0.7) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        padding: 0.8rem 2rem !important;
        border-radius: 8px !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
    }
    .hero-section + div .stButton > button[kind="secondary"]:hover {
        border-color: rgba(255,255,255,0.4) !important;
        color: white !important;
    }
    
    /* ===== 三步流程 ===== */
    .steps-section {
        background: #0a0e1a;
        padding: 2.5rem 2rem;
        margin: 0 -1rem;
    }
    .steps-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: white;
        margin-bottom: 0.5rem;
    }
    .steps-subtitle {
        font-size: 0.85rem;
        color: rgba(255,255,255,0.45);
        margin-bottom: 2rem;
    }
    .step-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 1.5rem;
        height: 100%;
    }
    .step-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        background: rgba(59, 130, 246, 0.2);
        color: #3b82f6;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .step-name {
        font-size: 1rem;
        font-weight: 600;
        color: white;
        margin-bottom: 0.5rem;
    }
    .step-desc {
        font-size: 0.8rem;
        color: rgba(255,255,255,0.45);
        line-height: 1.6;
    }
    
    /* ===== 功能模块展示 - 左右交替布局 ===== */
    .features-section {
        background: white;
        padding: 4rem 2rem;
        margin: 0 -1rem;
    }
    .features-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    .features-subtitle {
        font-size: 0.85rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .feature-row {
        display: flex;
        align-items: center;
        gap: 3rem;
        margin-bottom: 3rem;
    }
    .feature-content {
        flex: 1;
    }
    .feature-tag {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .feature-tag.orange {
        background: #fef3c7;
        color: #92400e;
    }
    .feature-tag.blue {
        background: #dbeafe;
        color: #1e40af;
    }
    .feature-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
    }
    .feature-desc {
        font-size: 0.85rem;
        color: #6b7280;
    }
    .feature-preview {
        flex: 1;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 0;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }
    .workspace-section {
        background: #0a0e1a;
        padding: 2.5rem 2rem;
        margin: 0 -1rem;
        min-height: 600px;
    }
    .workspace-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: white;
        margin-bottom: 2rem;
    }
    
    /* 左侧输入区 */
    .input-panel {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        height: 100%;
    }
    .input-panel-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #f1f5f9;
    }
    .form-label {
        font-size: 0.8rem;
        font-weight: 500;
        color: #374151;
        margin-bottom: 0.5rem;
    }
    .form-input {
        margin-bottom: 1.5rem;
    }
    .form-hint {
        font-size: 0.75rem;
        color: #9ca3af;
        margin-top: 0.25rem;
    }
    .generate-btn {
        background: #1e293b !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        width: 100% !important;
        cursor: pointer !important;
        transition: all 0.2s !important;
    }
    .generate-btn:hover {
        background: #334155 !important;
    }
    
    /* 右侧预览区 */
    .preview-panel {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 2rem;
        height: 100%;
    }
    .preview-panel-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: white;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .preview-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        transition: all 0.2s;
    }
    .preview-card:hover {
        background: rgba(255,255,255,0.06);
    }
    .preview-card.selected {
        border-color: #3b82f6;
        background: rgba(59, 130, 246, 0.08);
    }
    .preview-icon {
        font-size: 1.25rem;
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(59, 130, 246, 0.15);
        border-radius: 8px;
    }
    .preview-info {
        flex: 1;
    }
    .preview-name {
        font-size: 0.9rem;
        font-weight: 500;
        color: white;
        margin-bottom: 0.2rem;
    }
    .preview-desc {
        font-size: 0.75rem;
        color: rgba(255,255,255,0.4);
    }
    
    /* ===== 结果展示区 ===== */
    .results-section {
        background: white;
        padding: 3rem 2rem;
        margin: 0 -1rem;
    }
    .result-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* ===== 页脚 ===== */
    .footer-section {
        background: #0a0e1a;
        padding: 2.5rem 2rem 2rem 2rem;
        margin: 0 -1rem;
        border-top: 1px solid rgba(255,255,255,0.05);
    }
    .footer-brand {
        font-size: 1.1rem;
        font-weight: 600;
        color: white;
        margin-bottom: 0.5rem;
    }
    .footer-tagline {
        font-size: 0.8rem;
        color: rgba(255,255,255,0.4);
        margin-bottom: 2rem;
    }
    .footer-links {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
    }
    .footer-links a {
        color: rgba(255,255,255,0.45);
        font-size: 0.8rem;
        text-decoration: none;
        transition: color 0.2s;
    }
    .footer-links a:hover {
        color: #3b82f6;
    }
    .footer-column-title {
        display: none;
    }
    .footer-link {
        display: none;
    }
    .footer-bottom {
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(255,255,255,0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .footer-copyright {
        font-size: 0.75rem;
        color: rgba(255,255,255,0.25);
    }
    
    /* ===== 设置弹窗 ===== */
    .settings-overlay {
        background: rgba(0,0,0,0.5);
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 200;
    }
    .settings-panel {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
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
        background: linear-gradient(90deg, #3b82f6, #60a5fa);
        border-radius: 999px;
        transition: width 0.5s ease;
    }
    
    /* ===== 标签页 ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        background: #f8fafc;
        padding: 0.5rem;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        font-size: 0.9rem;
    }
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #1e3a5f !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
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
nav_cols = st.columns([6, 1])
with nav_cols[0]:
    st.markdown('<div class="nav-brand">企业培训智能化平台</div>', unsafe_allow_html=True)
with nav_cols[1]:
    api_status = "✅" if st.session_state.api_key else "⚠️"
    if st.button(f"⚙️ 设置", key="settings_toggle", help="API Key 设置"):
        st.session_state.show_settings = not st.session_state.show_settings
        st.rerun()

# 设置面板（条件显示）
if st.session_state.show_settings:
    with st.container():
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 20px 60px rgba(0,0,0,0.2);">
                <h3 style="margin-bottom: 0.5rem;">⚙️ API Key 设置</h3>
                <p style="color: #6b7280; font-size: 0.875rem; margin-bottom: 1.5rem;">设置后无需重复输入，当前会话内有效</p>
            </div>
            """, unsafe_allow_html=True)
            
            api_key_input = st.text_input(
                "DeepSeek API Key",
                type="password",
                value=st.session_state.api_key,
                placeholder="sk-...",
                label_visibility="collapsed"
            )
            
            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.button("💾 保存", use_container_width=True, type="primary"):
                    if api_key_input:
                        st.session_state.api_key = api_key_input
                        st.session_state.show_settings = False
                        st.success("✅ 已保存")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("请输入 API Key")
            with col_cancel:
                if st.button("取消", use_container_width=True):
                    st.session_state.show_settings = False
                    st.rerun()
        st.markdown("---")

# ============================================================
# Hero 区域 - 配图 + 跳转按钮
# ============================================================
st.markdown("""
<div class="hero-section">
    <div class="hero-container">
        <div class="hero-content">
            <div class="hero-title">从产品到培训，<br>一步到位</div>
            <div class="hero-subtitle">只需输入产品信息，描述核心功能与场景，即可自动生成全套培训方案，从蓝图到1V1点评，让产品培训事半功倍。</div>
        </div>
        <div class="hero-graphic">
            <svg viewBox="0 0 320 240" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:320px;">
                <defs>
                    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#1e3a5f;stop-opacity:0.4"/>
                        <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:0.1"/>
                    </linearGradient>
                    <linearGradient id="card-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#1e293b;stop-opacity:0.8"/>
                        <stop offset="100%" style="stop-color:#0f172a;stop-opacity:0.9"/>
                    </linearGradient>
                </defs>
                <rect width="320" height="240" rx="16" fill="url(#bg-grad)" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>
                <rect x="20" y="20" width="130" height="90" rx="10" fill="url(#card-grad)" stroke="rgba(255,255,255,0.06)" stroke-width="1"/>
                <circle cx="45" cy="45" r="8" fill="#3b82f6" opacity="0.8"/>
                <rect x="60" y="40" width="75" height="6" rx="3" fill="rgba(255,255,255,0.2)"/>
                <rect x="60" y="52" width="55" height="4" rx="2" fill="rgba(255,255,255,0.12)"/>
                <rect x="35" y="70" width="90" height="4" rx="2" fill="rgba(255,255,255,0.1)"/>
                <rect x="35" y="80" width="70" height="4" rx="2" fill="rgba(255,255,255,0.1)"/>
                <rect x="20" y="130" width="130" height="90" rx="10" fill="url(#card-grad)" stroke="rgba(255,255,255,0.06)" stroke-width="1"/>
                <rect x="35" y="150" width="100" height="40" rx="6" fill="rgba(59,130,246,0.15)" stroke="rgba(59,130,246,0.3)" stroke-width="1" stroke-dasharray="4,4"/>
                <text x="85" y="175" font-size="12" fill="#3b82f6" text-anchor="middle" font-family="sans-serif">AI 生成中...</text>
                <rect x="170" y="20" width="130" height="130" rx="10" fill="url(#card-grad)" stroke="rgba(255,255,255,0.06)" stroke-width="1"/>
                <circle cx="210" cy="55" r="12" fill="#f59e0b" opacity="0.7"/>
                <rect x="230" y="48" width="55" height="5" rx="2.5" fill="rgba(255,255,255,0.2)"/>
                <rect x="230" y="58" width="40" height="4" rx="2" fill="rgba(255,255,255,0.12)"/>
                <rect x="185" y="85" width="100" height="4" rx="2" fill="rgba(255,255,255,0.1)"/>
                <rect x="185" y="95" width="80" height="4" rx="2" fill="rgba(255,255,255,0.1)"/>
                <rect x="185" y="105" width="90" height="4" rx="2" fill="rgba(255,255,255,0.1)"/>
                <rect x="170" y="170" width="130" height="50" rx="10" fill="url(#card-grad)" stroke="rgba(255,255,255,0.06)" stroke-width="1"/>
                <rect x="185" y="185" width="100" height="8" rx="4" fill="rgba(34,197,94,0.3)"/>
                <rect x="185" y="185" width="70" height="8" rx="4" fill="rgba(34,197,94,0.6)"/>
                <text x="260" y="205" font-size="10" fill="rgba(255,255,255,0.4)" text-anchor="middle" font-family="sans-serif">75% 完成</text>
            </svg>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 立即体验按钮 - 点击后滚动到工作区
hero_cols = st.columns([3, 1])
with hero_cols[0]:
    if st.button("立即体验", key="hero_cta", type="primary", use_container_width=False):
        st.session_state.scroll_to_workspace = True
        st.rerun()
with hero_cols[1]:
    st.button("了解流程", key="hero_secondary", type="secondary", use_container_width=False, disabled=True)

# 跳转锚点占位
st.markdown("<div id='workspace-anchor'></div>", unsafe_allow_html=True)

# ============================================================
# 三步流程
# ============================================================
st.markdown("""
<div class="steps-section">
    <div class="steps-title">三步生成培训方案</div>
    <div class="steps-subtitle">从输入到输出，全程自动化智能化</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="step-card">
        <div class="step-number">1</div>
        <div class="step-name">输入产品信息</div>
        <div class="step-desc">填写产品名称、核心功能简介，让 AI 了解你的产品</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="step-card">
        <div class="step-number">2</div>
        <div class="step-name">选择培训场景</div>
        <div class="step-desc">指定培训对象和期望时长，系统智能匹配最优培训方案</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="step-card">
        <div class="step-number">3</div>
        <div class="step-name">一键生成输出</div>
        <div class="step-desc">即刻获得大纲、PPT、试题等全套培训材料，即刻投入使用</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 功能模块展示 - 左右交替布局
# ============================================================
st.markdown("""
<div class="features-section">
    <div style="text-align:center;margin-bottom:1rem;">
        <div class="features-title">覆盖全链路培训需求</div>
        <div class="features-subtitle">从规划到考核，为您生成体系化的完整培训方案</div>
    </div>

    <!-- Row 1: 课程大纲自动构建 - 文字左，SVG右 -->
    <div class="feature-row">
        <div class="feature-content">
            <div class="feature-tag blue">智能生成</div>
            <div class="feature-name">课程大纲自动构建</div>
            <div class="feature-desc">基于产品特性自动生成结构化课程目录，包含学习目标、知识模块和课时分配。</div>
        </div>
        <div class="feature-preview">
            <svg viewBox="0 0 280 180" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <filter id="fs1"><feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.08"/></filter>
                </defs>
                <rect x="10" y="8" width="260" height="164" rx="12" fill="white" filter="url(#fs1)"/>
                <rect x="10" y="8" width="260" height="6" rx="3" fill="#1e3a5f"/>
                <circle cx="32" cy="38" r="5" fill="#3b82f6"/>
                <rect x="44" y="34" width="150" height="7" rx="3.5" fill="#1e293b"/>
                <rect x="44" y="45" width="100" height="4" rx="2" fill="#94a3b8"/>
                <circle cx="32" cy="65" r="5" fill="#3b82f6"/>
                <rect x="44" y="61" width="180" height="7" rx="3.5" fill="#374151"/>
                <rect x="44" y="72" width="120" height="4" rx="2" fill="#94a3b8"/>
                <circle cx="32" cy="92" r="5" fill="#3b82f6"/>
                <rect x="44" y="88" width="160" height="7" rx="3.5" fill="#374151"/>
                <rect x="44" y="99" width="90" height="4" rx="2" fill="#94a3b8"/>
                <rect x="28" y="125" width="224" height="10" rx="5" fill="#f1f5f9"/>
                <rect x="28" y="125" width="150" height="10" rx="5" fill="#3b82f6"/>
                <text x="190" y="153" font-size="9" fill="#64748b" text-anchor="middle" font-family="system-ui,sans-serif">模块完成 65%</text>
            </svg>
        </div>
    </div>

    <!-- Row 2: 培训 PPT 即开即用 - SVG左，文字右 -->
    <div class="feature-row">
        <div class="feature-preview">
            <svg viewBox="0 0 280 180" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <filter id="fs2"><feDropShadow dx="0" dy="2" stdDeviation="4" flood-opacity="0.1"/></filter>
                </defs>
                <rect x="20" y="20" width="245" height="140" rx="9" fill="#fef3c7" stroke="#fcd34d" stroke-width="1" transform="rotate(-3,142,90)"/>
                <rect x="15" y="15" width="245" height="140" rx="9" fill="white" filter="url(#fs2)"/>
                <rect x="15" y="15" width="245" height="32" rx="9" fill="#fef3c7"/>
                <rect x="15" y="37" width="245" height="10" fill="#fef3c7"/>
                <rect x="28" y="23" width="130" height="7" rx="3.5" fill="#f59e0b"/>
                <circle cx="36" cy="60" r="4" fill="#e5e7eb"/>
                <rect x="47" y="57" width="140" height="5" rx="2.5" fill="#4b5563"/>
                <circle cx="36" cy="76" r="4" fill="#e5e7eb"/>
                <rect x="47" y="73" width="155" height="5" rx="2.5" fill="#4b5563"/>
                <rect x="47" y="82" width="100" height="3" rx="1.5" fill="#9ca3af"/>
                <circle cx="36" cy="96" r="4" fill="#f59e0b"/>
                <rect x="47" y="93" width="125" height="5" rx="2.5" fill="#f59e0b"/>
                <rect x="160" y="125" width="90" height="7" rx="3.5" fill="#e5e7eb"/>
            </svg>
        </div>
        <div class="feature-content">
            <div class="feature-tag orange">一键输出</div>
            <div class="feature-name">培训 PPT 即开即用</div>
            <div class="feature-desc">自动生成结构完整、版式专业的演示文稿，包含封面、目录、内容页和总结。</div>
        </div>
    </div>

    <!-- Row 3: 智能考核与评估 - 文字左，SVG右 -->
    <div class="feature-row">
        <div class="feature-content">
            <div class="feature-tag blue">多维度</div>
            <div class="feature-name">智能考核与评估</div>
            <div class="feature-desc">生成多类型考核题目，支持自动评分和成绩分析，帮助评估培训效果。</div>
        </div>
        <div class="feature-preview">
            <svg viewBox="0 0 280 180" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <filter id="fs3"><feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.08"/></filter>
                </defs>
                <rect x="10" y="8" width="260" height="164" rx="12" fill="white" filter="url(#fs3)"/>
                <circle cx="28" cy="28" r="14" fill="#fef2f2" stroke="#fecaca" stroke-width="1"/>
                <text x="28" y="33" font-size="12" font-weight="bold" fill="#ef4444" text-anchor="middle" font-family="system-ui,sans-serif">?</text>
                <rect x="50" y="22" width="170" height="6" rx="3" fill="#374151"/>
                <rect x="50" y="33" width="110" height="6" rx="3" fill="#4b5563"/>
                <circle cx="36" cy="60" r="6" fill="white" stroke="#d1d5db" stroke-width="1.5"/>
                <rect x="50" y="57" width="150" height="5" rx="2.5" fill="#6b7280"/>
                <circle cx="36" cy="78" r="6" fill="white" stroke="#d1d5db" stroke-width="1.5"/>
                <rect x="50" y="75" width="165" height="5" rx="2.5" fill="#6b7280"/>
                <circle cx="36" cy="96" r="6" fill="#ef4444" stroke="#ef4444" stroke-width="1.5"/>
                <circle cx="36" cy="96" r="3" fill="white"/>
                <rect x="50" y="93" width="130" height="5" rx="2.5" fill="#ef4444"/>
                <circle cx="36" cy="114" r="6" fill="white" stroke="#d1d5db" stroke-width="1.5"/>
                <rect x="50" y="111" width="110" height="5" rx="2.5" fill="#6b7280"/>
                <rect x="190" y="130" width="58" height="24" rx="12" fill="#ef4444" opacity="0.85"/>
                <text x="219" y="146" font-size="11" font-weight="600" fill="white" text-anchor="middle" font-family="system-ui,sans-serif">4 / 4</text>
                <rect x="28" y="152" width="224" height="5" rx="2.5" fill="#f1f5f9"/>
                <rect x="28" y="152" width="224" height="5" rx="2.5" fill="#22c55e"/>
            </svg>
        </div>
    </div>

    <!-- Row 4: 实操场景化练习 - SVG左，文字右 -->
    <div class="feature-row">
        <div class="feature-preview">
            <svg viewBox="0 0 280 180" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <filter id="fs4"><feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.08"/></filter>
                </defs>
                <rect x="10" y="8" width="260" height="164" rx="12" fill="white" filter="url(#fs4)"/>
                <circle cx="236" cy="28" r="18" fill="#ecfdf5" stroke="#bbf7d0" stroke-width="1.5"/>
                <circle cx="236" cy="28" r="11" fill="white" stroke="#86efac" stroke-width="1"/>
                <circle cx="236" cy="28" r="5" fill="#22c55e"/>
                <line x1="236" y1="10" x2="236" y2="46" stroke="#22c55e" stroke-width="0.8" opacity="0.3"/>
                <line x1="218" y1="28" x2="254" y2="28" stroke="#22c55e" stroke-width="0.8" opacity="0.3"/>
                <rect x="28" y="26" width="18" height="18" rx="4" fill="#22c55e"/>
                <polyline points="34,33 37,36 40,32" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <rect x="56" y="28" width="120" height="6" rx="3" fill="#374151"/>
                <rect x="56" y="38" width="70" height="4" rx="2" fill="#94a3b8"/>
                <rect x="28" y="58" width="18" height="18" rx="4" fill="#22c55e"/>
                <polyline points="34,65 37,68 40,64" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <rect x="56" y="60" width="140" height="6" rx="3" fill="#374151"/>
                <rect x="56" y="70" width="90" height="4" rx="2" fill="#94a3b8"/>
                <rect x="28" y="90" width="18" height="18" rx="4" fill="#22c55e"/>
                <polyline points="34,97 37,100 40,96" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <rect x="56" y="92" width="115" height="6" rx="3" fill="#374151"/>
                <rect x="56" y="102" width="80" height="4" rx="2" fill="#94a3b8"/>
                <rect x="28" y="122" width="18" height="18" rx="4" fill="white" stroke="#d1d5db" stroke-width="1.5"/>
                <rect x="56" y="124" width="145" height="6" rx="3" fill="#d1d5db"/>
                <rect x="56" y="134" width="95" height="4" rx="2" fill="#e5e7eb"/>
            </svg>
        </div>
        <div class="feature-content">
            <div class="feature-tag orange">实战导向</div>
            <div class="feature-name">实操场景化练习</div>
            <div class="feature-desc">根据产品使用场景生成实战案例与操作练习，让学员在模拟环境中掌握核心功能。</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 生成工作区（左右分栏）
# ============================================================
if st.session_state.scroll_to_workspace:
    st.markdown("""
    <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; padding: 0.75rem 1rem; margin: 1rem 0; color: #3b82f6; font-size: 0.9rem; text-align: center;">
        已跳转到工作区，请填写下方信息开始生成培训方案
    </div>
    """, unsafe_allow_html=True)
    st.session_state.scroll_to_workspace = False

st.markdown("""
<div class="workspace-section" id="workspace">
    <div class="workspace-title">开始生成您的培训方案</div>
</div>
""", unsafe_allow_html=True)

# 检查 API Key
if not st.session_state.api_key:
    st.markdown("""
    <div style="text-align: center; padding: 3rem; color: rgba(255,255,255,0.5);">
        <p style="font-size: 1.1rem; margin-bottom: 1rem;">⚠️ 请先点击右上角「⚙️ 设置」配置 DeepSeek API Key</p>
        <p style="font-size: 0.85rem; color: rgba(255,255,255,0.3);">设置一次后，当前会话内无需重复输入</p>
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
            <a href="https://github.com/ChelseaPYC/training-designer" target="_blank">开源仓库</a>
        </div>
        <div class="footer-bottom">
            <div class="footer-copyright">© 2026 AI培训设计器</div>
            <div class="footer-copyright">v4.3 | 由 ChelseaPYC 构建</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

left_col, right_col = st.columns([1, 1])

with left_col:
    # 左侧输入面板
    st.markdown("""
    <div class="input-panel">
        <div class="input-panel-title">培训信息</div>
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
        options=list(range(1, 31)),
        value=st.session_state.training_days,
        label_visibility="collapsed"
    )
    st.markdown(f'<div class="form-hint">当前选择：{training_days} 天</div>', unsafe_allow_html=True)
    
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
        <div class="preview-panel-title">生成预览</div>
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
            status_text.markdown(f"<div style='color: rgba(255,255,255,0.6); font-size: 0.85rem;'>正在生成：{MODULE_LABELS[module]} ({i+1}/{total_modules})</div>", unsafe_allow_html=True)
            
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
        status_text.markdown("<div style='color: #3b82f6; font-size: 0.85rem;'>✅ 所有内容生成完成！</div>", unsafe_allow_html=True)
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
                st.markdown(f"<div class='result-card'>{content}</div>", unsafe_allow_html=True)
                
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
        <a href="https://github.com/ChelseaPYC/training-designer" target="_blank">开源仓库</a>
    </div>
    <div class="footer-bottom">
        <div class="footer-copyright">© 2026 AI培训设计器</div>
        <div class="footer-copyright">v4.3 | 由 ChelseaPYC 构建</div>
    </div>
</div>
""", unsafe_allow_html=True)
