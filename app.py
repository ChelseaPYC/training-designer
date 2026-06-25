import streamlit as st
import requests
import json
import time

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="AI+培训设计器 v4.0",
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
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    .hero-container h1 {
        color: white;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .hero-container p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
    }
    
    /* ===== 输入区域样式 ===== */
    .input-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        border-left: 4px solid #667eea;
    }
    
    /* ===== 模块选择卡片 ===== */
    .module-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 2px solid #e0e0e0;
        transition: all 0.3s;
    }
    .module-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }
    .module-card.selected {
        border-color: #667eea;
        background: #f8f9ff;
    }
    
    /* ===== 生成按钮 ===== */
    .generate-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 3rem;
        border-radius: 10px;
        font-size: 1.2rem;
        font-weight: bold;
        border: none;
        cursor: pointer;
        width: 100%;
        margin-top: 1rem;
    }
    
    /* ===== 进度条样式 ===== */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* ===== 结果区域 ===== */
    .result-section {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        margin-top: 2rem;
        border: 1px solid #e0e0e0;
    }
    
    /* ===== 跳过提示 ===== */
    .skip-box {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #856404;
    }
    
    /* ===== 侧边栏样式 ===== */
    .css-1d391kg {
        background: #f8f9fa;
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

def build_prompt(module, product_name, product_type, training_roles, training_duration, product_doc=""):
    """根据模块类型和用户输入构建提示词"""
    
    base_info = f"""
产品名称：{product_name}
产品类型：{product_type}
培训对象：{', '.join(training_roles)}
培训时长：{training_duration}分钟
"""
    
    if product_doc:
        base_info += f"\n产品文档：\n{product_doc}"
    
    prompts = {
        "blueprint": f"""
{base_info}

请生成一份完整的产品培训蓝图，包含以下内容：

1. **产品定位**：核心价值主张、目标客户、竞争优势
2. **模块全景图**：产品功能模块结构（用Mermaid图或层级列表展示）
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

请生成一份30天学习迁移计划，基于70-20-10学习模型：

**70% 在岗实践**：
- 第一周：熟悉环境，完成基础配置
- 第二周：独立完成1个小任务
- 第三周：独立完成1个中等任务
- 第四周：能够指导他人

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
- 30天/60天/90天行为观察表
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
    st.session_state.api_key = ""
if "show_api" not in st.session_state:
    st.session_state.show_api = True
if "product_name" not in st.session_state:
    st.session_state.product_name = ""
if "product_type" not in st.session_state:
    st.session_state.product_type = "软件"
if "training_roles" not in st.session_state:
    st.session_state.training_roles = []
if "training_duration" not in st.session_state:
    st.session_state.training_duration = 60
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
if "generation_progress" not in st.session_state:
    st.session_state.generation_progress = 0
if "generation_status" not in st.session_state:
    st.session_state.generation_status = ""
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

# ============================================================
# 侧边栏：API Key 管理
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ 设置")
    
    # API Key 管理
    if not st.session_state.api_key or st.session_state.show_api:
        st.markdown("### 🔑 DeepSeek API Key")
        api_key_input = st.text_input(
            "输入你的 DeepSeek API Key",
            type="password",
            value=st.session_state.api_key,
            help="API Key 将安全保存在浏览器会话中，不会上传到服务器"
        )
        
        if st.button("💾 保存 API Key", use_container_width=True):
            if api_key_input:
                st.session_state.api_key = api_key_input
                st.session_state.show_api = False
                st.success("✅ API Key 已保存！")
                st.rerun()
            else:
                st.error("请输入 API Key")
    else:
        st.success("✅ API Key 已设置")
        if st.button("🔄 修改 API Key", use_container_width=True):
            st.session_state.show_api = True
            st.rerun()
    
    st.divider()
    
    # 使用说明
    st.markdown("### 📖 使用说明")
    st.markdown("""
    1. 在右侧填写产品信息
    2. 选择需要生成的模块
    3. 点击「开始生成」
    4. 等待所有内容生成完成
    5. 查看或下载生成结果
    """)

# ============================================================
# 主页面
# ============================================================

# 顶部Hero区域
st.markdown("""
<div class='hero-container'>
    <h1>🎓 AI+培训设计器 v4.0</h1>
    <p>基于方法论的智能培训内容生成工具 · 一次性生成所有选中模块</p>
</div>
""", unsafe_allow_html=True)

# 检查 API Key
if not st.session_state.api_key:
    st.warning("⚠️ 请先在左侧边栏设置 DeepSeek API Key")
    st.stop()

# 输入区域
with st.container():
    st.markdown("## 📝 填写产品信息")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 基本信息")
        
        product_name = st.text_input(
            "产品名称 *",
            value=st.session_state.product_name,
            placeholder="例如：腾讯云服务器、企业微信、钛虎机器人控制器",
            help="输入你要设计培训方案的产品名称"
        )
        
        product_type = st.selectbox(
            "产品类型 *",
            ["软件", "硬件", "SaaS", "平台", "其他"],
            index=["软件", "硬件", "SaaS", "平台", "其他"].index(st.session_state.product_type),
            help="选择产品类型，将影响培训内容的设计风格"
        )
        
        training_duration = st.slider(
            "培训时长（分钟）",
            min_value=30,
            max_value=480,
            value=st.session_state.training_duration,
            step=30,
            help="总培训时长，将影响每个模块的详细程度"
        )
    
    with col2:
        st.markdown("### 培训对象")
        
        training_roles = st.multiselect(
            "选择培训对象 *",
            ["实施工程师", "运维工程师", "技术支持", "销售", "客户成功", "售前工程师", "市场", "行政", "财务"],
            default=st.session_state.training_roles,
            help="选择所有需要参加培训的岗位，系统会根据岗位自动判断实操等级"
        )
        
        st.markdown("### 产品文档（可选）")
        product_doc = st.text_area(
            "粘贴产品介绍、功能说明或用户手册",
            value=st.session_state.product_doc,
            height=200,
            placeholder="将产品文档粘贴到这里，AI 会更好地理解你的产品...",
            help="可选，但建议提供，能显著提升生成质量"
        )

# 模块选择区域
st.markdown("## 🎯 选择输出模块")
st.markdown("培训蓝图是必选模块，其他模块可根据需要勾选：")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 📋 核心模块")
    blueprint = st.checkbox("📋 培训蓝图（必选）", value=True, disabled=True, help="包含产品定位、模块全景、场景串讲、术语表、FAQ")
    hands_on = st.checkbox("🔧 实操任务", value=st.session_state.module_selection["hands_on"], help="根据岗位等级自动生成L3/L2/L1实操任务")

with col2:
    st.markdown("#### 🎯 考核与素材")
    assessment = st.checkbox("🎯 考核系统", value=st.session_state.module_selection["assessment"], help="场景分析、实操演练、模拟答辩")
    materials = st.checkbox("📑 培训素材", value=st.session_state.module_selection["materials"], help="PPT大纲、讲师手册、练习册、速查卡")

with col3:
    st.markdown("#### 📊 评估与迁移")
    transfer = st.checkbox("🔄 学习迁移", value=st.session_state.module_selection["transfer"], help="30天在岗实践计划")
    evaluation = st.checkbox("📊 效果评估", value=st.session_state.module_selection["evaluation"], help="Kirkpatrick四级评估框架")

# 更新模块选择
st.session_state.module_selection = {
    "blueprint": True,  # 强制选中
    "hands_on": hands_on,
    "assessment": assessment,
    "materials": materials,
    "transfer": transfer,
    "evaluation": evaluation
}

# 显示选中模块的统计
selected_count = sum(st.session_state.module_selection.values())
st.info(f"已选择 {selected_count} 个模块，预计生成时间：约 {selected_count * 1.5:.0f} 秒")

# 保存当前输入
st.session_state.product_name = product_name
st.session_state.product_type = product_type
st.session_state.training_roles = training_roles
st.session_state.training_duration = training_duration
st.session_state.product_doc = product_doc

# 生成按钮
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 开始生成", use_container_width=True, type="primary", disabled=st.session_state.is_generating):
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
            
            # 计算需要生成的模块
            modules_to_generate = [k for k, v in st.session_state.module_selection.items() if v]
            total_modules = len(modules_to_generate)
            
            # 创建进度条
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 逐个生成模块
            for i, module in enumerate(modules_to_generate):
                # 更新状态
                progress = int((i / total_modules) * 100)
                progress_bar.progress(progress)
                status_text.markdown(f"**正在生成：** {MODULE_LABELS[module]}...")
                st.session_state.generation_progress = progress
                st.session_state.generation_status = f"正在生成 {MODULE_LABELS[module]}..."
                
                # 构建提示词
                prompt = build_prompt(
                    module,
                    product_name,
                    product_type,
                    training_roles,
                    training_duration,
                    product_doc
                )
                
                # 调用 API
                content = call_deepseek(prompt, st.session_state.api_key)
                
                # 保存结果
                st.session_state.generated_content[module] = content
                
                # 短暂延迟，避免 API 限流
                time.sleep(1)
            
            # 生成完成
            progress_bar.progress(100)
            status_text.markdown("**✅ 所有内容生成完成！**")
            st.session_state.generation_complete = True
            st.session_state.is_generating = False
            st.session_state.generation_progress = 100
            st.session_state.generation_status = "生成完成！"
            
            # 重新运行以更新界面
            st.rerun()

# 显示生成结果
if st.session_state.generation_complete:
    st.markdown("---")
    st.markdown("## 📊 生成结果")
    
    # 创建标签页显示不同模块
    modules_with_content = [k for k in st.session_state.module_selection.keys() if st.session_state.module_selection[k] and k in st.session_state.generated_content]
    
    if modules_with_content:
        tabs = st.tabs([MODULE_LABELS[m] for m in modules_with_content])
        
        for i, (tab, module) in enumerate(zip(tabs, modules_with_content)):
            with tab:
                content = st.session_state.generated_content[module]
                st.markdown(content)
                
                # 下载按钮
                st.download_button(
                    label=f"📥 下载 {MODULE_LABELS[module]}",
                    data=content,
                    file_name=f"{product_name}_{module}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
        
        # 全部下载（打包）
        st.markdown("---")
        st.markdown("### 📦 一键下载全部")
        
        # 合并所有内容
        all_content = f"# {product_name} - 培训设计方案\n\n"
        all_content += f"生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
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
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>🎓 AI+培训设计器 v4.0 | 基于方法论的智能培训内容生成工具</p>
    <p>Supported by WorkBuddy AI</p>
</div>
""", unsafe_allow_html=True)
