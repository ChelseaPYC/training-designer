import streamlit as st
import requests
import json
import time

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="AI+培训设计器 v3.1",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 常量定义
# ============================================================
MODULE_KEY_MAP = {
    3: "blueprint",
    4: "hands_on",
    5: "assessment",
    6: "materials",
    7: "transfer",
    8: "evaluation"
}

MODULE_LABELS = {
    "blueprint": "📋 培训蓝图",
    "hands_on": "🔧 实操任务",
    "assessment": "🎯 考核系统",
    "materials": "📑 培训素材",
    "transfer": "🔄 学习迁移",
    "evaluation": "📊 效果评估"
}

MODULE_DESCRIPTIONS = {
    "blueprint": "产品定位+模块全景+场景串讲+术语+问答+考核",
    "hands_on": "根据岗位等级自动判断L3/L2/L1",
    "assessment": "场景分析+实操演练+模拟答辩",
    "materials": "PPT大纲+讲师手册+练习册+速查卡",
    "transfer": "30天计划，70-20-10模型",
    "evaluation": "Kirkpatrick四级：满意度→前后测→行为→ROI"
}

STEP_NAMES = [
    "产品校验", "培训参数", "自适应判断", "培训蓝图",
    "实操任务", "考核系统", "培训素材", "学习迁移", "效果评估"
]

STEP_ICONS = ["📝", "🎯", "🧠", "📋", "🔧", "🎯", "📑", "🔄", "📊"]

# ============================================================
# 自定义CSS样式
# ============================================================
st.markdown("""
<style>
    /* ===== 全局字体和背景 ===== */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    
    /* ===== 顶部Hero区域 ===== */
    .hero-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem 3rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 400;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.8rem;
    }
    
    /* ===== 进度条 ===== */
    .progress-container {
        background: #f0f2f6;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #e8ecf4;
    }
    .progress-bar-bg {
        background: #e8ecf4;
        border-radius: 8px;
        height: 10px;
        margin-top: 0.8rem;
        overflow: hidden;
    }
    .progress-bar-fill {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 100%;
        border-radius: 8px;
        transition: width 0.5s ease;
    }
    .progress-text {
        font-size: 0.9rem;
        color: #4a5568;
        font-weight: 600;
    }
    .step-indicators {
        display: flex;
        gap: 6px;
        margin-top: 0.6rem;
        flex-wrap: wrap;
    }
    .step-dot {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .step-dot-done {
        background: #48bb78;
        color: white;
    }
    .step-dot-active {
        background: #667eea;
        color: white;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3);
    }
    .step-dot-pending {
        background: #e2e8f0;
        color: #a0aec0;
    }
    .step-dot-skipped {
        background: #fee;
        color: #999;
        text-decoration: line-through;
    }
    
    /* ===== 步骤卡片 ===== */
    .step-card {
        background: white;
        border: 2px solid #e8ecf4;
        border-radius: 14px;
        padding: 0;
        margin-bottom: 1rem;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    .step-card-header {
        padding: 1.2rem 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .step-card-header-done {
        background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
    }
    .step-card-header-active {
        background: linear-gradient(135deg, #ebf4ff 0%, #bee3f8 100%);
    }
    .step-card-header-skipped {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
    }
    .step-number {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.1rem;
        flex-shrink: 0;
    }
    .step-number-done {
        background: #48bb78;
        color: white;
    }
    .step-number-active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .step-number-pending {
        background: #e2e8f0;
        color: #a0aec0;
    }
    .step-number-skipped {
        background: #fecaca;
        color: #991b1b;
    }
    .step-title-text {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1a202c;
    }
    .step-title-text-skipped {
        font-size: 1.15rem;
        font-weight: 700;
        color: #999;
    }
    .step-status-badge {
        margin-left: auto;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-completed {
        background: #c6f6d5;
        color: #22543d;
    }
    .badge-active {
        background: #bee3f8;
        color: #2a4365;
    }
    .badge-pending {
        background: #e2e8f0;
        color: #a0aec0;
    }
    .badge-skipped {
        background: #fecaca;
        color: #991b1b;
    }
    .step-card-body {
        padding: 1.2rem 1.5rem 1.5rem;
    }
    
    /* ===== 信息提示框 ===== */
    .info-box {
        background: linear-gradient(135deg, #ebf8ff 0%, #e0f2fe 100%);
        border-left: 5px solid #4299e1;
        padding: 14px 18px;
        border-radius: 0 12px 12px 0;
        margin: 12px 0;
        font-size: 0.95rem;
        color: #2c5282;
        line-height: 1.6;
    }
    .warning-box {
        background: linear-gradient(135deg, #fffff0 0%, #fefce8 100%);
        border-left: 5px solid #eab308;
        padding: 14px 18px;
        border-radius: 0 12px 12px 0;
        margin: 12px 0;
        font-size: 0.95rem;
        color: #713f12;
        line-height: 1.6;
    }
    .success-box {
        background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
        border-left: 5px solid #48bb78;
        padding: 14px 18px;
        border-radius: 0 12px 12px 0;
        margin: 12px 0;
        font-size: 0.95rem;
        color: #22543d;
        line-height: 1.6;
    }
    .skip-box {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border-left: 5px solid #ef4444;
        padding: 14px 18px;
        border-radius: 0 12px 12px 0;
        margin: 12px 0;
        font-size: 0.95rem;
        color: #991b1b;
        line-height: 1.6;
    }
    
    /* ===== 模块选择卡片 ===== */
    .module-card {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        transition: all 0.2s ease;
    }
    .module-card:hover {
        border-color: #667eea;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
    }
    .module-card-selected {
        border-color: #667eea;
        background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
    }
    
    /* ===== 结果展示卡片 ===== */
    .result-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    }
    .result-card h3 {
        color: #2d3748;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #edf2f7;
    }
    
    /* ===== 按钮美化 ===== */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.5rem 1.5rem !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }
    .stButton > button[data-baseweb="button"][kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    .stButton > button[data-baseweb="button"]:not([kind="primary"]) {
        background: #f7fafc !important;
        color: #4a5568 !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    /* ===== 输入框美化 ===== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 10px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 0.6rem 1rem !important;
        font-size: 0.95rem !important;
        transition: border-color 0.2s ease !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15) !important;
    }
    
    /* ===== 选择框美化 ===== */
    .stSelectbox > div > div {
        border-radius: 10px !important;
    }
    
    /* ===== Checkbox美化 ===== */
    .stCheckbox > label {
        font-weight: 500;
    }
    
    /* ===== 侧边栏美化 ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%) !important;
    }
    [data-testid="stSidebar"] .sidebar-content {
        padding: 1.5rem 1rem;
    }
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] .stMarkdown {
        color: #a0aec0 !important;
    }
    [data-testid="stSidebar"] .stTextInput > div > div > input {
        background: rgba(255,255,255,0.1) !important;
        border-color: rgba(255,255,255,0.2) !important;
        color: white !important;
        border-radius: 10px !important;
    }
    [data-testid="stSidebar"] .stTextInput > div > div > input::placeholder {
        color: rgba(255,255,255,0.4) !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.1) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.2) !important;
    }
    [data-testid="stSidebar"] .stSuccess {
        background: rgba(72, 187, 120, 0.2) !important;
        color: #9ae6b4 !important;
        border: 1px solid rgba(72, 187, 120, 0.3) !important;
    }
    [data-testid="stSidebar"] .stWarning {
        background: rgba(234, 179, 8, 0.2) !important;
        color: #fef08a !important;
        border: 1px solid rgba(234, 179, 8, 0.3) !important;
    }
    
    /* ===== Metric卡片美化 ===== */
    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    [data-testid="stMetric"] label {
        font-weight: 600 !important;
        color: #718096 !important;
        font-size: 0.85rem !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: #2d3748 !important;
    }
    
    /* ===== 分隔线美化 ===== */
    hr {
        border-color: #e2e8f0 !important;
        margin: 1.5rem 0 !important;
    }
    
    /* ===== Expander美化 ===== */
    .streamlit-expanderHeader {
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        color: #2d3748 !important;
        background: #f7fafc !important;
        border-radius: 10px !important;
    }
    .streamlit-expanderContent {
        border: 1px solid #e2e8f0 !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
        padding: 1rem 1.2rem !important;
    }
    
    /* ===== 完成页面美化 ===== */
    .completion-container {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 50%, #fefcbf 100%);
        border-radius: 20px;
        margin: 2rem 0;
        box-shadow: 0 10px 40px rgba(72, 187, 120, 0.2);
    }
    .completion-emoji {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    .completion-title {
        font-size: 2rem;
        font-weight: 800;
        color: #22543d;
        margin-bottom: 0.5rem;
    }
    .completion-subtitle {
        font-size: 1.1rem;
        color: #2f855a;
        margin-bottom: 2rem;
    }
    
    /* ===== 隐藏元素 ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ===== 动画 ===== */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .result-card, .step-card {
        animation: fadeIn 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 初始化 Session State
# ============================================================
def init_state():
    defaults = {
        "api_key": "",
        "show_api_input": False,
        "selected_modules": ["blueprint", "hands_on", "assessment", "materials", "transfer", "evaluation"],
        "step_completed": [False] * 9,
        "product_input": "",
        "product_validation": "",
        "product_type": "",
        "product_positioning": "",
        "core_modules": [],
        "target_users": "",
        "key_value": "",
        "uncertain_items": "",
        "validation_confirmed": False,
        "target_role": "",
        "training_duration": "1天",
        "experience_level": "新人（0-1年）",
        "prior_knowledge": "完全不了解该类产品",
        "team_size": "小组培训（3-8人）",
        "complexity": "中等",
        "complexity_reason": "",
        "scene_count": 3,
        "term_count": 8,
        "qa_count": 10,
        "assessment_types": [],
        "hands_on_level": "",
        "hands_on_level_desc": "",
        "blueprint": "",
        "hands_on_tasks": "",
        "assessment": "",
        "materials": "",
        "transfer_plan": "",
        "evaluation": "",
        "current_tab": 0,
        "generation_status": "idle",
        "error_msg": "",
        "adaptive_result": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ============================================================
# 辅助函数
# ============================================================
def get_selected_steps():
    """获取当前选中的步骤索引列表"""
    base = [0, 1, 2]
    gen = [i for i in range(3, 9) if MODULE_KEY_MAP[i] in st.session_state.selected_modules]
    return base + gen

def get_module_step_index(module_key):
    """获取模块对应的步骤索引"""
    for step, key in MODULE_KEY_MAP.items():
        if key == module_key:
            return step
    return None

def is_module_selected(module_key):
    """判断模块是否被选中"""
    return module_key in st.session_state.selected_modules

# ============================================================
# API 调用函数
# ============================================================
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

def call_ai(system_prompt, user_prompt, temperature=0.7, max_tokens=4000):
    """调用 DeepSeek API"""
    api_key = st.session_state.api_key
    if not api_key:
        return None, "请先输入 API Key"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        with st.spinner("🤖 AI 正在生成中，请稍候..."):
            resp = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"], None
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 401:
            return None, "⚠️ API Key 无效，请检查"
        elif resp.status_code == 429:
            return None, "⏳ 请求太频繁，请稍后再试"
        else:
            return None, f"❌ API 错误 ({resp.status_code}): {resp.text[:200]}"
    except Exception as e:
        return None, f"❌ 调用失败: {str(e)}"

# ============================================================
# System Prompt 常量
# ============================================================

SYS_PRODUCT_VALIDATION = """你是一位资深企业培训设计专家。你的任务是基于用户提供的产品信息（任意格式），提取结构化的产品理解，并请用户确认。

核心规则：
1. 如果产品信息不够完整，你必须明确标注"不确定项"，不得编造产品功能
2. 如果用户只提供了产品名称和简短描述，主动列出"我对这个产品的理解可能不完整，以下功能需要您确认"的清单
3. 如果AI完全不认识该产品，必须明确告知"我对该产品没有预置知识，以下理解全部基于您提供的信息"
4. 所有后续内容必须基于用户确认后的理解，不得自行补充未经确认的功能

输出格式：
```
【产品理解校验】
- 产品类型：（CRM/ERP/SaaS/数字人平台/AI工具/低代码平台/其他）
- 产品定位：（一句话概括产品是做什么的）
- 核心模块：（列出识别到的功能模块名称，5-15个）
- 目标用户：（谁会使用这个产品）
- 关键差异化价值：（2-3条产品独特卖点）
- 不确定项：（AI无法确认的功能/特性，列出待用户确认）
```"""

SYS_ADAPTIVE = """你是一位资深企业培训设计专家。基于已确认的产品信息和培训参数，进行自适应判断。

判断1：产品复杂度（根据模块数量、涉及角色、业务链路长度）
- 简单：<5个模块，1-2个角色，单步操作
- 中等：5-15个模块，3-5个角色，多步流程
- 复杂：>15个模块，>5个角色，跨部门全链路

判断2：考核方式选择（根据产品类型 × 目标岗位）
- 场景分析题：给出业务情境，判断用什么模块、如何组合
- 实操演练：给出明确任务，要求产出具体成果
- 模拟答辩：设定客户角色，准备由浅入深的客户提问

判断3：软件实操需求等级（根据目标岗位）
- L3 深度实操：实施顾问、运维、技术支持（需要独立配置系统、处理异常）
- L2 基础实操：销售、客户成功、售前（需要向客户演示核心功能）
- L1 无需实操：市场、行政、财务（只需理解产品价值）

输出格式：
```
【自适应判断结果】
- 产品复杂度：[简单/中等/复杂]
- 判断依据：[模块数量X个/角色X类/业务链路...]
- 场景数量：X个
- 术语数量：X个
- 问答数量：X条
- 考核方式：[场景分析/实操演练/模拟答辩，可多选]
- 实操等级：[L3/L2/L1]
- 实操等级说明：[为什么选这个等级]
```"""

SYS_BLUEPRINT = """你是一位资深企业培训设计专家，精通ADDIE培训设计模型、Bloom认知分类法和70-20-10学习法则。

核心原则：
1. 业务视角优先：所有内容从"业务问题→产品解法"角度展开
2. 禁止操作说明：不输出任何"点击""打开""选择菜单"类指引
3. 通俗易懂：避免堆砌技术术语，善用类比和例子
4. 结构化输出：能用表格/列表的地方优先用，避免大段散文
5. 岗位适配：场景案例、问答库的侧重点需匹配目标岗位

培训蓝图包含6个模块：
1. 产品定位与价值（100-500字，段落+分条）
2. 核心模块全景图（Markdown表格：模块名/一句话功能/业务价值）
3. 典型业务流程串讲（N个场景，每个含：场景名称/业务背景/产品如何支持/业务收益）
4. 关键术语表（N个术语，Markdown表格：术语/通俗解释）
5. 常见客户问答库（N条问答，格式：Q: / A:）
6. 考核系统（根据判断结果选择考核方式）

注意：根据受众画像（经验水平、先验知识、团队规模）调整内容深度和互动设计。"""

SYS_HANDS_ON = """你是一位资深企业培训设计专家。基于自适应判断的实操等级，为需要实操的岗位设计软件实操任务。

L3 深度实操（实施/运维/技术支持）设计规范：
- 每个任务以"独立上岗能完成的标准工作任务"为单元
- 包含：业务背景、环境准备、任务清单（含子任务/操作说明/预期结果）、干扰项设计（1-2个）、交付物、评分标准（5维度）、讲师参考答案
- 操作说明是业务层面的（如"创建XX审批流"），不是界面步骤（如"点击XX按钮"）

L2 基础实操（销售/客户成功/售前）设计规范：
- 每个任务以"能向客户演示核心价值"为单元
- 包含：业务背景、环境准备、演示任务清单（含步骤/价值点/客户反应）、演示话术提示（开场/价值/应对）、交付物、评分标准（4维度）

L1 无需实操：不输出实操任务，改为输出"产品价值速览卡"（一页纸：产品定位/3个核心价值/目标客户画像/2个标杆案例摘要）"""

SYS_ASSESSMENT = """你是一位资深企业培训设计专家。基于自适应判断结果，生成考核系统。

考核方式设计规范：

场景分析题：
- 给出真实业务情境（客户背景+需求/问题）
- 要求学员判断：用什么模块、如何组合、预期效果
- 参考答案按"模块选择→组合逻辑→业务效果"三段式
- 难度分级：初级（单模块）→中级（跨模块）→高级（全链路）

实操演练：
- 给出明确任务目标+初始条件
- 要求产出具体成果
- 评分标准：完成度+正确性+效率
- 设置1-2个干扰项（数据异常、权限不足等）

模拟答辩：
- 设定客户角色和背景（行业/规模/关注点）
- 准备3-5个由浅入深的客户提问
- 学员需结合产品价值回答，不得只讲功能
- 评估维度：业务理解、价值表达、应变能力、话术专业性
- 设置"追问"环节"""

SYS_MATERIALS = """你是一位资深企业培训设计专家。基于培训蓝图，生成4类可交付的培训素材。

素材1：PPT大纲
- 按蓝图模块顺序生成页面
- 每页：页码/标题/核心要点（3-5条）/配图建议
- 页面类型：封面/议程/价值主张/模块全景/场景串讲/互动/总结/考核

素材2：讲师手册
- 按PPT逐模块生成讲师指导
- 每个模块：教学目标/时间分配/讲述要点/互动提示/常见学员疑问预判/过渡语

素材3：学员练习册
- 按考核方式生成练习任务书
- 每个练习：任务背景/任务要求/产出标准/评分标准

素材4：快速参考卡
- 一页纸（A4）容量
- 核心术语速查+高频问答速查+模块价值速查"""

SYS_TRANSFER = """你是一位资深企业培训设计专家。基于培训蓝图，生成30天学习迁移计划，覆盖70-20-10模型。

70-20-10模型：
- 70% 岗位实践（on-the-job experience）
- 20% 社交学习（向他人学）
- 10% 正式学习（课堂/复习）

计划结构：
- 第一周（Day 1-7）：知识巩固期
- 第二周（Day 8-14）：初步应用期
- 第三周（Day 15-21）：深度应用期
- 第四周（Day 22-30）：巩固评估期

遗忘曲线对抗设计：Day 1/3/7/14/30的间隔复习
上级参与节点：培训前5分钟/Day 7检查/Day 15面谈/Day 30评估"""

SYS_EVALUATION = """你是一位资深企业培训设计专家。生成Kirkpatrick四级评估框架。

第一级（反应层）：满意度调查问卷
- 8-10题，5分制Likert量表
- 覆盖：内容相关性、理解度、讲师表现、实用性预期、开放题

第二级（学习层）：前测+后测
- 前测（培训前）：5道认知题，评估知识基线
- 后测（培训后）：同知识点应用题，评估掌握程度
- 对比分析：均分对比+分层分析+薄弱点识别

第三级（行为层）：行为观察清单
- 30天和60天两个观察点
- 4个观察项：产品价值表达、场景应用、客户问答应对、独立解决问题
- 1-5分制，由直属上级/导师填写

第四级（结果层）：ROI测算模板
- 4个指标：上岗周期、首次解决率、方案准确率、转化周期
- ROI计算公式和框架
- 注意事项：需3-6个月数据积累，建议先选1-2个指标试点"""

# ============================================================
# 侧边栏
# ============================================================
with st.sidebar:
    # --- 项目标题区 ---
    st.markdown("""
    <div style='text-align:center;margin-bottom:1.5rem;'>
        <div style='font-size:2.5rem;margin-bottom:0.3rem;'>🎓</div>
        <div style='font-size:1.3rem;font-weight:800;color:white;'>AI+培训设计器</div>
        <div style='font-size:0.85rem;color:#a0aec0;margin-top:0.2rem;'>v3.1 全生命周期版</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # --- 功能导航区 ---
    st.markdown("<div style='color:white;font-size:0.95rem;font-weight:700;margin-bottom:0.8rem;'>📍 功能导航</div>", unsafe_allow_html=True)
    
    selected_steps = get_selected_steps()
    for i in range(9):
        step_name = STEP_NAMES[i]
        step_icon = STEP_ICONS[i]
        is_selected = i in selected_steps
        
        if not is_selected:
            # 未选中的模块显示为跳过状态
            st.markdown(
                f"<div style='color:#718096;font-size:0.8rem;margin:3px 0;padding-left:4px;'>⛔ Step {i}: {step_name}（跳过）</div>",
                unsafe_allow_html=True
            )
            continue
        
        if st.session_state.step_completed[i]:
            icon = "✅"
            color = "#48bb78"
            status = "已完成"
        elif i == 0 or st.session_state.step_completed[i-1]:
            icon = "▶️"
            color = "#667eea"
            status = "进行中"
        else:
            icon = "🔒"
            color = "#a0aec0"
            status = "待开始"
        
        st.markdown(
            f"<div style='color:{color};font-size:0.85rem;margin:3px 0;padding-left:4px;'>{icon} Step {i}: {step_name}</div>",
            unsafe_allow_html=True
        )
    
    st.divider()
    
    # --- API 设置区（可折叠） ---
    with st.expander("🔑 API 设置", expanded=not st.session_state.api_key):
        if st.session_state.api_key and not st.session_state.show_api_input:
            # 已设置，显示状态和修改按钮
            st.success("✅ API Key 已设置")
            if st.button("✏️ 修改 API Key", use_container_width=True):
                st.session_state.show_api_input = True
                st.rerun()
        else:
            # 显示输入框
            api_key = st.text_input(
                "DeepSeek API Key",
                type="password",
                value=st.session_state.api_key,
                help="在 platform.deepseek.com 注册获取",
                label_visibility="collapsed",
                placeholder="在此粘贴 API Key"
            )
            if api_key != st.session_state.api_key:
                st.session_state.api_key = api_key
                if api_key:
                    st.session_state.show_api_input = False
                st.rerun()
            
            if st.session_state.api_key:
                st.success("✅ 已保存")
            else:
                st.info("💡 请输入 API Key 以使用生成功能")
            
            st.markdown("<div style='font-size:0.75rem;color:#a0aec0;'>数据仅保存在当前会话中，刷新页面后需重新输入</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # --- 模块选择快捷入口 ---
    with st.expander("📦 输出模块选择", expanded=False):
        st.markdown("<div style='font-size:0.85rem;color:#a0aec0;margin-bottom:0.5rem;'>随时修改要生成的模块</div>", unsafe_allow_html=True)
        for key in ["blueprint", "hands_on", "assessment", "materials", "transfer", "evaluation"]:
            label = MODULE_LABELS[key]
            checked = st.checkbox(label, value=(key in st.session_state.selected_modules), key=f"sidebar_module_{key}")
            if checked and key not in st.session_state.selected_modules:
                st.session_state.selected_modules.append(key)
            elif not checked and key in st.session_state.selected_modules:
                st.session_state.selected_modules.remove(key)
    
    st.divider()
    
    # --- 项目信息区 ---
    st.markdown("""
    <div style='font-size:0.75rem;color:#718096;text-align:center;'>
        <div style='margin-bottom:0.3rem;'>基于 ADDIE + Bloom + Kirkpatrick</div>
        <div style='margin-bottom:0.3rem;'>+ 70-20-10 方法论框架</div>
        <div style='margin-top:0.5rem;'>Made with ❤️ by ChelseaPYC</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # --- 重置按钮 ---
    if st.button("🔄 重置所有数据", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        init_state()
        st.rerun()

# ============================================================
# 主页面 - Hero区域
# ============================================================
selected_steps = get_selected_steps()
completed_count = sum(st.session_state.step_completed[i] for i in selected_steps)
total_selected = len(selected_steps)
progress_pct = int((completed_count / total_selected) * 100) if total_selected > 0 else 0

st.markdown(f"""
<div class='hero-container'>
    <div class='hero-title'>🎓 AI+培训设计器 v3.1</div>
    <div class='hero-subtitle'>全生命周期培训方案生成 · 基于 ADDIE + Bloom + Kirkpatrick + 70-20-10 方法论框架</div>
    <div class='hero-badge'>🚀 Powered by DeepSeek AI · 覆盖培训设计全流程</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 进度条
# ============================================================
step_labels = ["校验", "参数", "判断", "蓝图", "实操", "考核", "素材", "迁移", "评估"]
dots_html = ""
for i in range(9):
    if i not in selected_steps:
        dot_class = "step-dot step-dot-skipped"
        dot_text = "✕"
    elif st.session_state.step_completed[i]:
        dot_class = "step-dot step-dot-done"
        dot_text = "✓"
    elif i == 0 or st.session_state.step_completed[i-1]:
        dot_class = "step-dot step-dot-active"
        dot_text = str(i+1)
    else:
        dot_class = "step-dot step-dot-pending"
        dot_text = str(i+1)
    dots_html += f"<div class='{dot_class}'>{dot_text}</div>"

st.markdown(f"""
<div class='progress-container'>
    <div style='display:flex;justify-content:space-between;align-items:center;'>
        <div class='progress-text'>📊 完成进度：{completed_count} / {total_selected} 步骤</div>
        <div style='font-size:1.4rem;font-weight:800;color:#667eea;'>{progress_pct}%</div>
    </div>
    <div class='progress-bar-bg'>
        <div class='progress-bar-fill' style='width:{progress_pct}%;'></div>
    </div>
    <div class='step-indicators'>
        {dots_html}
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 使用说明
# ============================================================
with st.expander("📖 使用说明 & 方法论介绍", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        **🎯 本工具覆盖培训全生命周期 9 大步骤：**
        
        1. **产品理解校验** — AI提取结构化理解，确认后防幻觉
        2. **培训参数设置** — 岗位/时长/经验水平等6个维度
        3. **自适应判断** — AI自动判断复杂度、考核方式、实操等级
        4. **培训蓝图生成** — 产品定位→模块全景→场景串讲→术语→问答→考核
        5. **软件实操任务** — 条件触发：L3深度/L2基础/L1无需实操
        6. **考核系统生成** — 场景分析+实操演练+模拟答辩
        7. **培训素材生成** — PPT大纲+讲师手册+练习册+速查卡
        8. **学习迁移计划** — 30天计划，70-20-10模型
        9. **效果评估框架** — Kirkpatrick四级：满意度→前后测→行为→ROI
        """)
    with col_b:
        st.markdown("""
        **🧠 核心方法论框架：**
        
        - **ADDIE模型** — 分析→设计→开发→实施→评估
        - **Bloom分类法** — 记忆→理解→应用→分析→评价→创造
        - **Kirkpatrick四级** — 反应→学习→行为→结果
        - **70-20-10法则** — 70%实践+20%社交+10%正式学习
        - **防幻觉机制** — 产品理解校验，用户确认后才生成
        - **自适应规则** — 按产品复杂度自动调整生成策略
        """)

# ============================================================
# Step 0: 产品理解校验
# ============================================================
step0_expanded = not st.session_state.step_completed[0]
with st.expander("📝 Step 0: 产品理解校验（防幻觉）", expanded=step0_expanded):
    st.markdown("<div class='info-box'>💡 请先提供产品信息（任意格式：产品文档、简介、功能清单等）。AI会提取结构化理解并请你确认，<b>防止后续生成中出现编造的功能</b>。</div>", unsafe_allow_html=True)
    
    product_input = st.text_area(
        "粘贴产品信息",
        value=st.session_state.product_input,
        height=200,
        placeholder="请粘贴产品介绍、功能文档、官网描述等（支持任意格式，可混合）\n\n示例：\nXX产品是一款面向制造企业的智能仓储管理系统，核心功能包括入库管理、出库管理、库存盘点...",
        help="信息越详细，AI理解越准确",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🚀 提取产品理解", use_container_width=True, disabled=not product_input.strip()):
            if not st.session_state.api_key:
                st.error("请先在侧边栏设置 API Key")
            else:
                prompt = f"请基于以下产品信息，提取结构化的产品理解：\n\n{product_input}"
                result, error = call_ai(SYS_PRODUCT_VALIDATION, prompt)
                if error:
                    st.error(error)
                else:
                    st.session_state.product_input = product_input
                    st.session_state.product_validation = result
                    lines = result.split("\n")
                    for line in lines:
                        if "产品类型" in line:
                            val = line.split("：")[-1].strip() if "：" in line else ""
                            st.session_state.product_type = val
                        elif "产品定位" in line:
                            val = line.split("：")[-1].strip() if "：" in line else ""
                            st.session_state.product_positioning = val
                        elif "核心模块" in line and "不确定" not in line:
                            parts = line.split("：")[-1].split("、") if "：" in line else line.split(":")[-1].split(",")
                            st.session_state.core_modules = [m.strip() for m in parts if m.strip()]
                    st.rerun()
    
    if st.session_state.product_validation:
        st.markdown("---")
        st.subheader("🤖 AI 提取的产品理解")
        st.markdown(st.session_state.product_validation)
        
        st.markdown("<div class='warning-box'>⚠️ 请仔细检查上述理解是否正确，特别关注「不确定项」部分。如果理解有误，请修改上方的产品信息后重新提取。</div>", unsafe_allow_html=True)
        
        col_ok, col_next = st.columns([1, 2])
        with col_ok:
            confirm = st.checkbox("✅ 我已确认上述产品理解正确，可以基于此生成培训方案", value=st.session_state.validation_confirmed)
        with col_next:
            if confirm and not st.session_state.validation_confirmed:
                if st.button("➡️ 确认并进入下一步", use_container_width=True):
                    st.session_state.validation_confirmed = True
                    st.session_state.step_completed[0] = True
                    st.rerun()
            elif not confirm and st.session_state.validation_confirmed:
                st.session_state.validation_confirmed = False
                st.session_state.step_completed[0] = False
                st.rerun()

# ============================================================
# Step 1: 收集培训参数 + 选择输出模块
# ============================================================
step1_expanded = st.session_state.step_completed[0] and not st.session_state.step_completed[1]
with st.expander("🎯 Step 1: 收集培训参数", expanded=step1_expanded):
    if not st.session_state.step_completed[0]:
        st.info("请先完成 Step 0 产品理解校验")
    else:
        st.markdown("<div class='info-box'>⚙️ 设置培训的基本参数和输出模块，AI会根据这些参数调整内容深度、互动方式和生成范围。</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            target_role = st.selectbox(
                "🎯 目标岗位",
                ["销售", "售前顾问", "实施顾问", "实施工程师", "客服", "客户成功经理", 
                 "运维工程师", "技术支持", "产品经理", "市场专员", "行政", "财务", "人力资源", "其他"],
                index=0 if not st.session_state.target_role else ["销售", "售前顾问", "实施顾问", "实施工程师", "客服", "客户成功经理", "运维工程师", "技术支持", "产品经理", "市场专员", "行政", "财务", "人力资源", "其他"].index(st.session_state.target_role) if st.session_state.target_role in ["销售", "售前顾问", "实施顾问", "实施工程师", "客服", "客户成功经理", "运维工程师", "技术支持", "产品经理", "市场专员", "行政", "财务", "人力资源", "其他"] else 0
            )
            training_duration = st.selectbox(
                "⏱️ 培训时长",
                ["1天", "2天", "1周（5天）"],
                index=["1天", "2天", "1周（5天）"].index(st.session_state.training_duration)
            )
            experience_level = st.selectbox(
                "📊 经验水平",
                ["新人（0-1年）", "有经验（1-5年）", "资深（5年+）"],
                index=["新人（0-1年）", "有经验（1-5年）", "资深（5年+）"].index(st.session_state.experience_level)
            )
        with col2:
            prior_knowledge = st.selectbox(
                "🧠 先验知识",
                ["完全不了解该类产品", "了解同类竞品", "已熟悉本公司其他产品"],
                index=["完全不了解该类产品", "了解同类竞品", "已熟悉本公司其他产品"].index(st.session_state.prior_knowledge)
            )
            team_size = st.selectbox(
                "👥 团队规模",
                ["1对1培训", "小组培训（3-8人）", "批量培训（10人+）"],
                index=["1对1培训", "小组培训（3-8人）", "批量培训（10人+）"].index(st.session_state.team_size)
            )
        
        st.session_state.target_role = target_role
        st.session_state.training_duration = training_duration
        st.session_state.experience_level = experience_level
        st.session_state.prior_knowledge = prior_knowledge
        st.session_state.team_size = team_size
        
        # --- 模块选择区域 ---
        st.markdown("---")
        st.subheader("📦 选择输出模块")
        st.markdown("<div style='font-size:0.9rem;color:#666;'>请选择需要生成的内容模块，未选中的模块将被跳过。培训蓝图为必选项，因为其他模块依赖它。</div>", unsafe_allow_html=True)
        
        cols = st.columns(3)
        for i, key in enumerate(["blueprint", "hands_on", "assessment", "materials", "transfer", "evaluation"]):
            with cols[i % 3]:
                is_required = (key == "blueprint")
                label = MODULE_LABELS[key]
                desc = MODULE_DESCRIPTIONS[key]
                
                if is_required:
                    checked = st.checkbox(f"{label} *", value=True, disabled=True, key=f"module_{key}")
                    st.caption(f"{desc} （必选）")
                    if key not in st.session_state.selected_modules:
                        st.session_state.selected_modules.append(key)
                else:
                    current_val = key in st.session_state.selected_modules
                    checked = st.checkbox(label, value=current_val, key=f"module_{key}")
                    st.caption(desc)
                    if checked and key not in st.session_state.selected_modules:
                        st.session_state.selected_modules.append(key)
                    elif not checked and key in st.session_state.selected_modules:
                        st.session_state.selected_modules.remove(key)
        
        # 快捷操作按钮
        col_all, col_none, col_spacer = st.columns([1, 1, 4])
        with col_all:
            if st.button("☑️ 全选", use_container_width=True):
                st.session_state.selected_modules = ["blueprint", "hands_on", "assessment", "materials", "transfer", "evaluation"]
                st.rerun()
        with col_none:
            if st.button("⬜ 取消（保留蓝图）", use_container_width=True):
                st.session_state.selected_modules = ["blueprint"]
                st.rerun()
        
        st.markdown("---")
        col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
        with col_btn1:
            if st.button("✅ 确认参数并进入下一步", use_container_width=True):
                st.session_state.step_completed[1] = True
                st.rerun()

# ============================================================
# Step 2: 自适应判断
# ============================================================
step2_expanded = st.session_state.step_completed[1] and not st.session_state.step_completed[2]
with st.expander("🧠 Step 2: 自适应判断", expanded=step2_expanded):
    if not st.session_state.step_completed[1]:
        st.info("请先完成 Step 1 培训参数设置")
    else:
        st.markdown("<div class='info-box'>🧠 AI 根据产品信息和培训参数，自动判断复杂度、考核方式和实操等级。</div>", unsafe_allow_html=True)
        
        col_btn = st.columns([2, 2, 2])[0]
        with col_btn:
            if st.button("🚀 开始自适应判断", use_container_width=True):
                if not st.session_state.api_key:
                    st.error("请先在侧边栏设置 API Key")
                else:
                    product_info = f"""
产品信息：
{st.session_state.product_validation}

培训参数：
- 目标岗位：{st.session_state.target_role}
- 培训时长：{st.session_state.training_duration}
- 经验水平：{st.session_state.experience_level}
- 先验知识：{st.session_state.prior_knowledge}
- 团队规模：{st.session_state.team_size}
"""
                    result, error = call_ai(SYS_ADAPTIVE, product_info)
                    if error:
                        st.error(error)
                    else:
                        st.session_state.adaptive_result = result
                        lines = result.split("\n")
                        for line in lines:
                            if "产品复杂度" in line and "判断" not in line:
                                val = line.split("：")[-1].strip().replace("[", "").replace("]", "").replace("【", "").replace("】", "")
                                if "简单" in val:
                                    st.session_state.complexity = "简单"
                                elif "复杂" in val:
                                    st.session_state.complexity = "复杂"
                                else:
                                    st.session_state.complexity = "中等"
                            elif "场景数量" in line:
                                try:
                                    import re
                                    nums = re.findall(r'\d+', line)
                                    st.session_state.scene_count = int(nums[0]) if nums else 3
                                except:
                                    st.session_state.scene_count = 3
                            elif "术语数量" in line:
                                try:
                                    nums = re.findall(r'\d+', line)
                                    st.session_state.term_count = int(nums[0]) if nums else 8
                                except:
                                    st.session_state.term_count = 8
                            elif "问答数量" in line:
                                try:
                                    nums = re.findall(r'\d+', line)
                                    st.session_state.qa_count = int(nums[0]) if nums else 10
                                except:
                                    st.session_state.qa_count = 10
                            elif "实操等级" in line and "说明" not in line:
                                level = line.split("：")[-1].strip().replace("[", "").replace("]", "").replace("【", "").replace("】", "")
                                if "L3" in level or "深度" in level:
                                    st.session_state.hands_on_level = "L3"
                                elif "L2" in level or "基础" in level:
                                    st.session_state.hands_on_level = "L2"
                                elif "L1" in level or "无需" in level:
                                    st.session_state.hands_on_level = "L1"
                                else:
                                    st.session_state.hands_on_level = "L2"
                        st.rerun()
        
        if st.session_state.adaptive_result:
            st.markdown("---")
            st.markdown(st.session_state.adaptive_result)
            
            st.markdown("---")
            st.subheader("📊 关键判断摘要")
            cols = st.columns(4)
            with cols[0]:
                complexity_color = {"简单": "#48bb78", "中等": "#ed8936", "复杂": "#e53e3e"}.get(st.session_state.complexity, "#718096")
                st.markdown(f"""
                <div style='background:white;border-radius:12px;padding:1rem 1.2rem;border:1px solid #e2e8f0;box-shadow:0 2px 8px rgba(0,0,0,0.04);'>
                    <div style='font-size:0.85rem;color:#718096;font-weight:600;margin-bottom:0.3rem;'>产品复杂度</div>
                    <div style='font-size:1.5rem;font-weight:700;color:{complexity_color};'>{st.session_state.complexity}</div>
                </div>
                """, unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"""
                <div style='background:white;border-radius:12px;padding:1rem 1.2rem;border:1px solid #e2e8f0;box-shadow:0 2px 8px rgba(0,0,0,0.04);'>
                    <div style='font-size:0.85rem;color:#718096;font-weight:600;margin-bottom:0.3rem;'>场景数量</div>
                    <div style='font-size:1.5rem;font-weight:700;color:#2d3748;'>{st.session_state.scene_count} 个</div>
                </div>
                """, unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f"""
                <div style='background:white;border-radius:12px;padding:1rem 1.2rem;border:1px solid #e2e8f0;box-shadow:0 2px 8px rgba(0,0,0,0.04);'>
                    <div style='font-size:0.85rem;color:#718096;font-weight:600;margin-bottom:0.3rem;'>术语数量</div>
                    <div style='font-size:1.5rem;font-weight:700;color:#2d3748;'>{st.session_state.term_count} 个</div>
                </div>
                """, unsafe_allow_html=True)
            with cols[3]:
                level_map = {"L3": "深度实操", "L2": "基础实操", "L1": "无需实操"}
                level_color = {"L3": "#e53e3e", "L2": "#4299e1", "L1": "#48bb78"}.get(st.session_state.hands_on_level, "#718096")
                st.markdown(f"""
                <div style='background:white;border-radius:12px;padding:1rem 1.2rem;border:1px solid #e2e8f0;box-shadow:0 2px 8px rgba(0,0,0,0.04);'>
                    <div style='font-size:0.85rem;color:#718096;font-weight:600;margin-bottom:0.3rem;'>实操等级</div>
                    <div style='font-size:1.2rem;font-weight:700;color:{level_color};'>{level_map.get(st.session_state.hands_on_level, "基础实操")}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            if st.button("✅ 确认判断结果并进入下一步", use_container_width=True):
                st.session_state.step_completed[2] = True
                st.rerun()

# ============================================================
# Step 3: 生成培训蓝图（条件显示）
# ============================================================
step3_expanded = st.session_state.step_completed[2] and not st.session_state.step_completed[3] and is_module_selected("blueprint")
step3_collapsed = st.session_state.step_completed[3] and is_module_selected("blueprint")
with st.expander("📋 Step 3: 生成培训蓝图", expanded=(step3_expanded or step3_collapsed)):
    if not st.session_state.step_completed[2]:
        st.info("请先完成 Step 2 自适应判断")
    elif not is_module_selected("blueprint"):
        st.markdown("<div class='skip-box'>⛔ 此模块已跳过（未在模块选择中勾选）。如需生成，请返回 Step 1 勾选「培训蓝图」。</div>", unsafe_allow_html=True)
    else:
        col_btn = st.columns([2, 2, 2])[0]
        with col_btn:
            if st.button("🚀 生成培训蓝图", use_container_width=True, key="btn_blueprint"):
                if not st.session_state.api_key:
                    st.error("请先在侧边栏设置 API Key")
                else:
                    prompt = f"""
产品信息：
{st.session_state.product_validation}

培训参数：
- 目标岗位：{st.session_state.target_role}
- 培训时长：{st.session_state.training_duration}
- 经验水平：{st.session_state.experience_level}
- 先验知识：{st.session_state.prior_knowledge}
- 团队规模：{st.session_state.team_size}

自适应判断：
{st.session_state.adaptive_result}

请生成完整的培训蓝图（6个模块），严格按照以下格式输出：

# 第一部分：培训蓝图

## 一、产品定位与价值
...

## 二、核心模块全景图
| 模块名 | 一句话功能 | 业务价值 |
...

## 三、典型业务流程串讲
### 场景1：...
...

## 四、关键术语表
| 术语 | 通俗解释 |
...

## 五、常见客户问答库
**Q: ...**
A: ...

## 六、考核系统
### 场景分析题
...
### 实操演练
...
### 模拟答辩
...
"""
                    result, error = call_ai(SYS_BLUEPRINT, prompt, max_tokens=4000)
                    if error:
                        st.error(error)
                    else:
                        st.session_state.blueprint = result
                        st.rerun()
        
        if st.session_state.blueprint:
            st.markdown("---")
            st.markdown(st.session_state.blueprint)
            
            st.markdown("---")
            col_btn1, col_btn2 = st.columns([2, 1])
            with col_btn1:
                if st.button("✅ 确认蓝图并进入下一步", use_container_width=True, key="confirm_blueprint"):
                    st.session_state.step_completed[3] = True
                    st.rerun()

# ============================================================
# Step 4: 生成软件实操任务（条件显示）
# ============================================================
step4_expanded = st.session_state.step_completed[3] and not st.session_state.step_completed[4] and is_module_selected("hands_on")
step4_collapsed = st.session_state.step_completed[4] and is_module_selected("hands_on")
with st.expander("🔧 Step 4: 生成软件实操任务（条件触发）", expanded=(step4_expanded or step4_collapsed)):
    if not st.session_state.step_completed[3]:
        st.info("请先完成 Step 3 培训蓝图")
    elif not is_module_selected("hands_on"):
        st.markdown("<div class='skip-box'>⛔ 此模块已跳过（未在模块选择中勾选）。如需生成，请返回 Step 1 勾选「实操任务」，或在侧边栏快捷选择。</div>", unsafe_allow_html=True)
    else:
        level_map = {"L3": "深度实操", "L2": "基础实操", "L1": "无需实操"}
        level_name = level_map.get(st.session_state.hands_on_level, "基础实操")
        level_color = {"L3": "#e53e3e", "L2": "#4299e1", "L1": "#48bb78"}.get(st.session_state.hands_on_level, "#718096")
        
        st.markdown(f"<div class='info-box'>🎯 当前岗位「<b>{st.session_state.target_role}</b>」的实操等级为 <span style='color:{level_color};font-weight:700;'>{st.session_state.hands_on_level}（{level_name}）</span>。{'<b>将生成实操任务设计</b>。' if st.session_state.hands_on_level in ['L3', 'L2'] else '无需实操，<b>将生成产品价值速览卡</b>。'}</div>", unsafe_allow_html=True)
        
        col_btn = st.columns([2, 2, 2])[0]
        with col_btn:
            if st.button("🚀 生成实操任务", use_container_width=True, key="btn_hands_on"):
                if not st.session_state.api_key:
                    st.error("请先在侧边栏设置 API Key")
                else:
                    prompt = f"""
产品信息：
{st.session_state.product_validation}

培训参数：
- 目标岗位：{st.session_state.target_role}
- 培训时长：{st.session_state.training_duration}
- 经验水平：{st.session_state.experience_level}

实操等级：{st.session_state.hands_on_level}（{level_name}）

培训蓝图：
{st.session_state.blueprint}

请生成对应的实操任务设计（或产品价值速览卡）。
"""
                    result, error = call_ai(SYS_HANDS_ON, prompt, max_tokens=4000)
                    if error:
                        st.error(error)
                    else:
                        st.session_state.hands_on_tasks = result
                        st.rerun()
        
        if st.session_state.hands_on_tasks:
            st.markdown("---")
            st.markdown(st.session_state.hands_on_tasks)
            
            st.markdown("---")
            if st.button("✅ 确认并进入下一步", use_container_width=True, key="confirm_hands_on"):
                st.session_state.step_completed[4] = True
                st.rerun()

# ============================================================
# Step 5: 生成考核系统（条件显示）
# ============================================================
step5_expanded = st.session_state.step_completed[3] and not st.session_state.step_completed[5] and is_module_selected("assessment")
step5_collapsed = st.session_state.step_completed[5] and is_module_selected("assessment")
with st.expander("🎯 Step 5: 生成考核系统", expanded=(step5_expanded or step5_collapsed)):
    if not st.session_state.step_completed[3]:
        st.info("请先完成 Step 3 培训蓝图")
    elif not is_module_selected("assessment"):
        st.markdown("<div class='skip-box'>⛔ 此模块已跳过（未在模块选择中勾选）。如需生成，请返回 Step 1 勾选「考核系统」，或在侧边栏快捷选择。</div>", unsafe_allow_html=True)
    else:
        col_btn = st.columns([2, 2, 2])[0]
        with col_btn:
            if st.button("🚀 生成考核系统", use_container_width=True, key="btn_assessment"):
                if not st.session_state.api_key:
                    st.error("请先在侧边栏设置 API Key")
                else:
                    prompt = f"""
产品信息：
{st.session_state.product_validation}

培训参数：
- 目标岗位：{st.session_state.target_role}
- 培训时长：{st.session_state.training_duration}
- 经验水平：{st.session_state.experience_level}

自适应判断：
{st.session_state.adaptive_result}

培训蓝图：
{st.session_state.blueprint}

请生成完整的考核系统，包含场景分析题、实操演练、模拟答辩（根据自适应判断选择需要的方式）。
"""
                    result, error = call_ai(SYS_ASSESSMENT, prompt, max_tokens=4000)
                    if error:
                        st.error(error)
                    else:
                        st.session_state.assessment = result
                        st.rerun()
        
        if st.session_state.assessment:
            st.markdown("---")
            st.markdown(st.session_state.assessment)
            
            st.markdown("---")
            if st.button("✅ 确认并进入下一步", use_container_width=True, key="confirm_assessment"):
                st.session_state.step_completed[5] = True
                st.rerun()

# ============================================================
# Step 6: 生成培训素材（条件显示）
# ============================================================
step6_expanded = st.session_state.step_completed[3] and not st.session_state.step_completed[6] and is_module_selected("materials")
step6_collapsed = st.session_state.step_completed[6] and is_module_selected("materials")
with st.expander("📑 Step 6: 生成培训素材", expanded=(step6_expanded or step6_collapsed)):
    if not st.session_state.step_completed[3]:
        st.info("请先完成 Step 3 培训蓝图")
    elif not is_module_selected("materials"):
        st.markdown("<div class='skip-box'>⛔ 此模块已跳过（未在模块选择中勾选）。如需生成，请返回 Step 1 勾选「培训素材」，或在侧边栏快捷选择。</div>", unsafe_allow_html=True)
    else:
        col_btn = st.columns([2, 2, 2])[0]
        with col_btn:
            if st.button("🚀 生成培训素材", use_container_width=True, key="btn_materials"):
                if not st.session_state.api_key:
                    st.error("请先在侧边栏设置 API Key")
                else:
                    prompt = f"""
产品信息：
{st.session_state.product_validation}

培训参数：
- 目标岗位：{st.session_state.target_role}
- 培训时长：{st.session_state.training_duration}

培训蓝图：
{st.session_state.blueprint}

考核系统：
{st.session_state.assessment}

请生成4类培训素材：PPT大纲、讲师手册、学员练习册、快速参考卡。
"""
                    result, error = call_ai(SYS_MATERIALS, prompt, max_tokens=4000)
                    if error:
                        st.error(error)
                    else:
                        st.session_state.materials = result
                        st.rerun()
        
        if st.session_state.materials:
            st.markdown("---")
            st.markdown(st.session_state.materials)
            
            st.markdown("---")
            if st.button("✅ 确认并进入下一步", use_container_width=True, key="confirm_materials"):
                st.session_state.step_completed[6] = True
                st.rerun()

# ============================================================
# Step 7: 生成学习迁移计划（条件显示）
# ============================================================
step7_expanded = st.session_state.step_completed[3] and not st.session_state.step_completed[7] and is_module_selected("transfer")
step7_collapsed = st.session_state.step_completed[7] and is_module_selected("transfer")
with st.expander("🔄 Step 7: 生成学习迁移计划（30天）", expanded=(step7_expanded or step7_collapsed)):
    if not st.session_state.step_completed[3]:
        st.info("请先完成 Step 3 培训蓝图")
    elif not is_module_selected("transfer"):
        st.markdown("<div class='skip-box'>⛔ 此模块已跳过（未在模块选择中勾选）。如需生成，请返回 Step 1 勾选「学习迁移」，或在侧边栏快捷选择。</div>", unsafe_allow_html=True)
    else:
        col_btn = st.columns([2, 2, 2])[0]
        with col_btn:
            if st.button("🚀 生成学习迁移计划", use_container_width=True, key="btn_transfer"):
                if not st.session_state.api_key:
                    st.error("请先在侧边栏设置 API Key")
                else:
                    prompt = f"""
产品信息：
{st.session_state.product_validation}

培训参数：
- 目标岗位：{st.session_state.target_role}
- 培训时长：{st.session_state.training_duration}

培训蓝图：
{st.session_state.blueprint}

请生成30天学习迁移计划，包含70-20-10模型、遗忘曲线对抗设计和上级参与节点。
"""
                    result, error = call_ai(SYS_TRANSFER, prompt, max_tokens=4000)
                    if error:
                        st.error(error)
                    else:
                        st.session_state.transfer_plan = result
                        st.rerun()
        
        if st.session_state.transfer_plan:
            st.markdown("---")
            st.markdown(st.session_state.transfer_plan)
            
            st.markdown("---")
            if st.button("✅ 确认并进入下一步", use_container_width=True, key="confirm_transfer"):
                st.session_state.step_completed[7] = True
                st.rerun()

# ============================================================
# Step 8: 生成效果评估框架（条件显示）
# ============================================================
step8_expanded = st.session_state.step_completed[3] and not st.session_state.step_completed[8] and is_module_selected("evaluation")
step8_collapsed = st.session_state.step_completed[8] and is_module_selected("evaluation")
with st.expander("📊 Step 8: 生成效果评估框架（Kirkpatrick四级）", expanded=(step8_expanded or step8_collapsed)):
    if not st.session_state.step_completed[3]:
        st.info("请先完成 Step 3 培训蓝图")
    elif not is_module_selected("evaluation"):
        st.markdown("<div class='skip-box'>⛔ 此模块已跳过（未在模块选择中勾选）。如需生成，请返回 Step 1 勾选「效果评估」，或在侧边栏快捷选择。</div>", unsafe_allow_html=True)
    else:
        col_btn = st.columns([2, 2, 2])[0]
        with col_btn:
            if st.button("🚀 生成评估框架", use_container_width=True, key="btn_evaluation"):
                if not st.session_state.api_key:
                    st.error("请先在侧边栏设置 API Key")
                else:
                    prompt = f"""
产品信息：
{st.session_state.product_validation}

培训参数：
- 目标岗位：{st.session_state.target_role}
- 培训时长：{st.session_state.training_duration}

培训蓝图：
{st.session_state.blueprint}

考核系统：
{st.session_state.assessment}

请生成Kirkpatrick四级评估框架：满意度问卷、前测后测、行为观察清单、ROI测算模板。
"""
                    result, error = call_ai(SYS_EVALUATION, prompt, max_tokens=4000)
                    if error:
                        st.error(error)
                    else:
                        st.session_state.evaluation = result
                        st.rerun()
        
        if st.session_state.evaluation:
            st.markdown("---")
            st.markdown(st.session_state.evaluation)
            
            st.markdown("---")
            if st.button("🎉 完成全部生成！", use_container_width=True, key="confirm_evaluation"):
                st.session_state.step_completed[8] = True
                st.rerun()

# ============================================================
# 完成页
# ============================================================
# 判断是否所有选中的模块都已完成
all_selected_done = all(st.session_state.step_completed[i] for i in selected_steps)

if all_selected_done and len(selected_steps) > 0:
    st.markdown("""
    <div class='completion-container'>
        <div class='completion-emoji'>🎉</div>
        <div class='completion-title'>培训方案生成完成！</div>
        <div class='completion-subtitle'>所有选中的模块已生成，您可以下载完整方案或继续编辑</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 构建报告（只包含选中的模块）
    report_parts = [f"# {st.session_state.product_positioning or '产品'} 认知培训完整方案\n"]
    report_parts.append(f"**目标岗位**：{st.session_state.target_role}  |  **培训时长**：{st.session_state.training_duration}")
    report_parts.append(f"**经验水平**：{st.session_state.experience_level}  |  **先验知识**：{st.session_state.prior_knowledge}  |  **团队规模**：{st.session_state.team_size}")
    report_parts.append(f"**产品复杂度**：{st.session_state.complexity}  |  **实操等级**：{st.session_state.hands_on_level}")
    report_parts.append("")
    
    if is_module_selected("blueprint") and st.session_state.blueprint:
        report_parts.append("---")
        report_parts.append("# 第一部分：培训蓝图")
        report_parts.append("")
        report_parts.append(st.session_state.blueprint)
    
    if is_module_selected("hands_on") and st.session_state.hands_on_tasks:
        report_parts.append("---")
        report_parts.append("# 第二部分：软件实操任务")
        report_parts.append("")
        report_parts.append(st.session_state.hands_on_tasks)
    
    if is_module_selected("assessment") and st.session_state.assessment:
        report_parts.append("---")
        report_parts.append("# 第三部分：考核系统")
        report_parts.append("")
        report_parts.append(st.session_state.assessment)
    
    if is_module_selected("materials") and st.session_state.materials:
        report_parts.append("---")
        report_parts.append("# 第四部分：培训素材")
        report_parts.append("")
        report_parts.append(st.session_state.materials)
    
    if is_module_selected("transfer") and st.session_state.transfer_plan:
        report_parts.append("---")
        report_parts.append("# 第五部分：学习迁移计划（30天）")
        report_parts.append("")
        report_parts.append(st.session_state.transfer_plan)
    
    if is_module_selected("evaluation") and st.session_state.evaluation:
        report_parts.append("---")
        report_parts.append("# 第六部分：效果评估框架（Kirkpatrick四级）")
        report_parts.append("")
        report_parts.append(st.session_state.evaluation)
    
    report_parts.append("---")
    report_parts.append("> 本方案由 AI+培训设计器 v3.1 生成")
    report_parts.append("> 基于 ADDIE + Bloom + Kirkpatrick + 70-20-10 方法论框架")
    
    full_report = "\n".join(report_parts)
    
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            label="📥 下载完整方案（Markdown）",
            data=full_report,
            file_name=f"training_plan_{st.session_state.target_role}.md",
            mime="text/markdown",
            use_container_width=True
        )
    with col_dl2:
        st.download_button(
            label="📄 下载完整方案（文本）",
            data=full_report,
            file_name=f"training_plan_{st.session_state.target_role}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    st.markdown("---")
    st.markdown("### 📋 方案预览")
    st.markdown(full_report)
