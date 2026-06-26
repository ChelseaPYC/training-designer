import streamlit as st
import requests
import json
import time

# ============================================================
# 配置区：默认 API Key（可选，填入后用户无需手动设置）
# ============================================================
DEFAULT_API_KEY = "sk-7eb19602fcd34af48bb2763db71dba1c"  # 在此填入你的 DeepSeek API Key，例如："sk-xxx..."

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="AI+培训设计器",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# 常量定义
# ============================================================
MODULE_LABELS = {
    "blueprint": "📋 培训蓝图",
    "hands_on": "🔧 实操任务",
    "assessment": "🎯 考核系统",
    "materials": "📑 培训素材",
    "transfer": "🔄 学习迁移",
    "evaluation": "📊 效果评估"
}

MODULE_DESCRIPTIONS = {
    "blueprint": "产品定位 · 模块全景 · 场景串讲 · 术语 · FAQ",
    "hands_on": "L3/L2/L1 分级实操任务设计",
    "assessment": "场景分析 · 实操演练 · 模拟答辩",
    "materials": "PPT大纲 · 讲师手册 · 练习册 · 速查卡",
    "transfer": "30天在岗实践，70-20-10模型",
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

# ============================================================
# 自定义 CSS 样式 - 现代 SaaS 风格
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* ===== 全局基础 ===== */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    .main .block-container {
        padding: 0 2rem 3rem 2rem;
        max-width: 1200px;
    }
    
    /* ===== 顶部导航栏 ===== */
    .nav-bar {
        background: white;
        border-bottom: 1px solid #e5e7eb;
        padding: 0.75rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: -1rem -2rem 2rem -2rem;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .nav-brand {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1e293b;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .nav-badge {
        background: #dbeafe;
        color: #1d4ed8;
        font-size: 0.65rem;
        font-weight: 600;
        padding: 0.15rem 0.5rem;
        border-radius: 999px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* ===== 设置按钮 ===== */
    .settings-btn {
        background: transparent;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
        cursor: pointer;
        font-size: 1rem;
        transition: all 0.2s;
        color: #64748b;
    }
    .settings-btn:hover {
        background: #f1f5f9;
        border-color: #cbd5e1;
    }
    
    /* ===== Hero 区域 ===== */
    .hero-section {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero-title {
        font-size: 2.25rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
        position: relative;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: rgba(255,255,255,0.7);
        font-weight: 400;
        position: relative;
    }
    
    /* ===== 卡片基础 ===== */
    .card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1.5rem;
        transition: all 0.2s;
    }
    .card:hover {
        border-color: #cbd5e1;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }
    
    /* ===== 输入区域 ===== */
    .form-label {
        font-size: 0.875rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 0.5rem;
    }
    
    .form-hint {
        font-size: 0.75rem;
        color: #9ca3af;
        margin-top: 0.25rem;
    }
    
    /* ===== 模块卡片 ===== */
    .module-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
    }
    
    .module-item {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.25rem;
        cursor: pointer;
        transition: all 0.2s;
        position: relative;
    }
    .module-item:hover {
        border-color: #3b82f6;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.12);
    }
    .module-item.selected {
        border-color: #3b82f6;
        background: #eff6ff;
    }
    .module-item.required {
        border-color: #3b82f6;
        background: #eff6ff;
    }
    .module-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .module-name {
        font-size: 0.95rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.25rem;
    }
    .module-desc {
        font-size: 0.75rem;
        color: #6b7280;
        line-height: 1.4;
    }
    .module-check {
        position: absolute;
        top: 0.75rem;
        right: 0.75rem;
        color: #3b82f6;
        font-size: 1.25rem;
    }
    
    /* ===== 生成按钮 ===== */
    .generate-btn {
        background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem 2rem !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        width: 100% !important;
        transition: all 0.3s !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3) !important;
    }
    .generate-btn:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4) !important;
    }
    .generate-btn:disabled {
        opacity: 0.6 !important;
        cursor: not-allowed !important;
    }
    
    /* ===== 进度条 ===== */
    .progress-container {
        background: #f3f4f6;
        border-radius: 999px;
        height: 8px;
        overflow: hidden;
        margin: 1rem 0;
    }
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #2563eb, #3b82f6);
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
    
    /* ===== 设置弹窗 ===== */
    .settings-panel {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    }
    
    /* ===== 隐藏 Streamlit 默认元素 ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* ===== 响应式 ===== */
    @media (max-width: 768px) {
        .module-grid {
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
    # 优先使用默认 API Key，否则为空
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

# ============================================================
# 顶部导航栏（含设置按钮）
# ============================================================
cols = st.columns([1, 4, 1])
with cols[0]:
    st.markdown("""
    <div class="nav-brand">
        <span>🎓</span>
        <span>AI培训设计器</span>
        <span class="nav-badge">v4.1</span>
    </div>
    """, unsafe_allow_html=True)

with cols[2]:
    # 设置按钮
    api_status = "✅" if st.session_state.api_key else "⚠️"
    if st.button(f"⚙️ {api_status}", key="settings_toggle", help="API Key 设置"):
        st.session_state.show_settings = not st.session_state.show_settings
        st.rerun()

# 设置面板（条件显示）
if st.session_state.show_settings:
    with st.container():
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div class="settings-panel">
                <h3>⚙️ API Key 设置</h3>
                <p style="color: #6b7280; font-size: 0.875rem;">设置后无需重复输入，当前会话内有效</p>
            </div>
            """, unsafe_allow_html=True)
            
            api_key_input = st.text_input(
                "DeepSeek API Key",
                type="password",
                value=st.session_state.api_key,
                placeholder="sk-...",
                help="填入你的 DeepSeek API Key",
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
# 主页面
# ============================================================

# Hero 区域
st.markdown("""
<div class="hero-section">
    <div class="hero-title">🎓 AI+培训设计器</div>
    <div class="hero-subtitle">基于方法论的智能培训内容生成工具 · 一次性生成完整培训方案</div>
</div>
""", unsafe_allow_html=True)

# 检查 API Key
if not st.session_state.api_key:
    st.warning("⚠️ 请在右上角 ⚙️ 设置 DeepSeek API Key")
    st.stop()

# 输入区域 - 使用卡片布局
st.markdown("## 📝 培训项目信息")

with st.container():
    # 基本信息卡片
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("<div class='form-label'>产品名称</div>", unsafe_allow_html=True)
        product_name = st.text_input(
            "",
            value=st.session_state.product_name,
            placeholder="例如：腾讯云服务器、企业微信、钛虎机器人控制器",
            label_visibility="collapsed"
        )
        st.markdown("<div class='form-hint'>输入需要设计培训方案的产品名称</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='form-label' style='margin-top: 1rem;'>产品类型</div>", unsafe_allow_html=True)
        product_type = st.selectbox(
            "",
            ["软件", "硬件", "SaaS", "平台", "其他"],
            index=["软件", "硬件", "SaaS", "平台", "其他"].index(st.session_state.product_type),
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("<div class='form-label'>培训周期</div>", unsafe_allow_html=True)
        training_days = st.select_slider(
            "",
            options=list(range(1, 31)),
            value=st.session_state.training_days,
            label_visibility="collapsed"
        )
        st.markdown(f"<div class='form-hint'>当前选择：{training_days} 天</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='form-label' style='margin-top: 1rem;'>培训对象</div>", unsafe_allow_html=True)
        training_roles = st.multiselect(
            "",
            ["实施工程师", "运维工程师", "技术支持", "销售", "客户成功", "售前工程师", "市场", "行政", "财务"],
            default=st.session_state.training_roles,
            placeholder="选择培训对象...",
            label_visibility="collapsed"
        )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 产品文档卡片
    st.markdown("<div class='card' style='margin-top: 1rem;'>", unsafe_allow_html=True)
    st.markdown("<div class='form-label'>产品文档（可选）</div>", unsafe_allow_html=True)
    product_doc = st.text_area(
        "",
        value=st.session_state.product_doc,
        height=120,
        placeholder="粘贴产品介绍、功能说明或用户手册内容，AI 将更好地理解你的产品...",
        label_visibility="collapsed"
    )
    st.markdown("<div class='form-hint'>提供产品文档可显著提升生成内容的质量和准确性</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# 保存当前输入
st.session_state.product_name = product_name
st.session_state.product_type = product_type
st.session_state.training_roles = training_roles
st.session_state.training_days = training_days
st.session_state.product_doc = product_doc

# 模块选择区域
st.markdown("## 🎯 选择输出模块")

# 使用 Streamlit 的 checkbox 但美化显示
module_cols = st.columns(3)

modules = ["blueprint", "hands_on", "assessment", "materials", "transfer", "evaluation"]
module_values = {}

for i, module in enumerate(modules):
    with module_cols[i % 3]:
        is_required = module == "blueprint"
        default_value = st.session_state.module_selection.get(module, True)
        
        if is_required:
            # 必选模块，显示选中但禁用
            module_values[module] = st.checkbox(
                f"{MODULE_ICONS[module]} {MODULE_LABELS[module].split(' ')[1]}（必选）",
                value=True,
                disabled=True,
                help=MODULE_DESCRIPTIONS[module],
                key=f"module_{module}"
            )
            # 强制设为 True
            module_values[module] = True
        else:
            module_values[module] = st.checkbox(
                f"{MODULE_ICONS[module]} {MODULE_LABELS[module].split(' ')[1]}",
                value=default_value,
                help=MODULE_DESCRIPTIONS[module],
                key=f"module_{module}"
            )

# 更新模块选择
st.session_state.module_selection = module_values

selected_count = sum(module_values.values())
st.markdown(f"<p style='color: #6b7280; font-size: 0.875rem; margin-top: 0.5rem;'>已选择 {selected_count} 个模块，预计生成时间约 {selected_count * 1.5:.0f} 秒</p>", unsafe_allow_html=True)

# 生成按钮区域
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_clicked = st.button(
        "🚀 开始生成培训方案",
        use_container_width=True,
        type="primary",
        disabled=st.session_state.is_generating
    )
    
    if generate_clicked:
        # 验证输入
        if not product_name:
            st.error("❌ 请输入产品名称")
            st.stop()
        elif not training_roles:
            st.error("❌ 请选择培训对象")
            st.stop()
        else:
            # 开始生成
            st.session_state.is_generating = True
            st.session_state.generation_complete = False
            st.session_state.generated_content = {}
            st.rerun()

# 生成过程显示
if st.session_state.is_generating and not st.session_state.generation_complete:
    # 计算需要生成的模块
    modules_to_generate = [k for k, v in st.session_state.module_selection.items() if v]
    total_modules = len(modules_to_generate)
    
    st.markdown("---")
    st.markdown("### ⏳ 正在生成培训方案...")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 逐个生成模块
    for i, module in enumerate(modules_to_generate):
        # 更新状态
        progress = int(((i + 1) / total_modules) * 100)
        progress_bar.progress(progress)
        status_text.markdown(f"**正在生成：** {MODULE_LABELS[module]} ({i+1}/{total_modules})")
        
        # 构建提示词
        prompt = build_prompt(
            module,
            product_name,
            product_type,
            training_roles,
            training_days,
            product_doc
        )
        
        # 调用 API
        content = call_deepseek(prompt, st.session_state.api_key)
        
        # 保存结果
        st.session_state.generated_content[module] = content
        
        # 短暂延迟
        time.sleep(0.5)
    
    # 生成完成
    progress_bar.progress(100)
    status_text.markdown("**✅ 所有内容生成完成！**")
    st.session_state.generation_complete = True
    st.session_state.is_generating = False
    
    time.sleep(1)
    st.rerun()

# 显示生成结果
if st.session_state.generation_complete:
    st.markdown("---")
    st.markdown("## 📊 生成结果")
    
    modules_with_content = [k for k in st.session_state.module_selection.keys() if st.session_state.module_selection[k] and k in st.session_state.generated_content]
    
    if modules_with_content:
        # 创建标签页
        tabs = st.tabs([MODULE_LABELS[m] for m in modules_with_content])
        
        for i, (tab, module) in enumerate(zip(tabs, modules_with_content)):
            with tab:
                content = st.session_state.generated_content[module]
                
                # 使用卡片样式显示内容
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown(content)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # 下载按钮
                st.download_button(
                    label=f"📥 下载 {MODULE_LABELS[module]}",
                    data=content,
                    file_name=f"{product_name}_{module}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
        
        # 一键下载全部
        st.markdown("---")
        st.markdown("### 📦 完整方案下载")
        
        all_content = f"# {product_name} - 培训设计方案\n\n"
        all_content += f"生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        all_content += f"培训周期：{training_days} 天\n\n"
        all_content += "---\n\n"
        
        for module in modules_with_content:
            all_content += f"# {MODULE_LABELS[module]}\n\n"
            all_content += st.session_state.generated_content[module]
            all_content += "\n\n---\n\n"
        
        st.download_button(
            label="📥 下载完整培训方案（Markdown）",
            data=all_content,
            file_name=f"{product_name}_培训方案_完整版.md",
            mime="text/markdown",
            use_container_width=True
        )
    else:
        st.warning("没有生成任何内容，请检查模块选择。")

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #9ca3af; padding: 2rem; font-size: 0.875rem;'>
    <p>🎓 AI+培训设计器 v4.1 | 基于方法论的智能培训内容生成工具</p>
</div>
""", unsafe_allow_html=True)
