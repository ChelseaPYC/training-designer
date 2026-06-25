import streamlit as st
import requests
import json

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
# 自定义CSS样式
# ============================================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .step-badge {
        display: inline-block;
        background: #3b82f6;
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 8px;
    }
    .step-badge-done {
        background: #10b981;
    }
    .info-box {
        background: #eff6ff;
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 8px 0;
    }
    .warning-box {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 8px 0;
    }
    .result-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 初始化 Session State
# ============================================================
def init_state():
    defaults = {
        # API
        "api_key": "",
        "api_valid": False,
        
        # 步骤完成状态
        "step_completed": [False] * 9,
        
        # Step 0: 产品理解校验
        "product_input": "",
        "product_validation": "",
        "product_type": "",
        "product_positioning": "",
        "core_modules": [],
        "target_users": "",
        "key_value": "",
        "uncertain_items": "",
        "validation_confirmed": False,
        
        # Step 1: 培训参数
        "target_role": "",
        "training_duration": "1天",
        "experience_level": "新人",
        "prior_knowledge": "完全不了解",
        "team_size": "小组培训（3-8人）",
        
        # Step 2: 自适应判断
        "complexity": "中等",
        "complexity_reason": "",
        "scene_count": 3,
        "term_count": 8,
        "qa_count": 10,
        "assessment_types": [],
        "hands_on_level": "",
        "hands_on_level_desc": "",
        
        # Step 3: 培训蓝图
        "blueprint": "",
        
        # Step 4: 实操任务
        "hands_on_tasks": "",
        
        # Step 5: 考核系统
        "assessment": "",
        
        # Step 6: 培训素材
        "materials": "",
        
        # Step 7: 学习迁移
        "transfer_plan": "",
        
        # Step 8: 评估框架
        "evaluation": "",
        
        # 全局
        "current_tab": 0,
        "generation_status": "",  # idle, running, done, error
        "error_msg": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

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
        with st.spinner("AI 正在生成中，请稍候..."):
            resp = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"], None
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 401:
            return None, "API Key 无效，请检查"
        elif resp.status_code == 429:
            return None, "请求太频繁，请稍后再试"
        else:
            return None, f"API 错误 ({resp.status_code}): {resp.text[:200]}"
    except Exception as e:
        return None, f"调用失败: {str(e)}"

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
    st.markdown("<div class='main-header'>🎓 AI+培训设计器</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>v3.1 — 全生命周期培训方案生成</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # API Key 输入
    st.subheader("🔑 API 设置")
    api_key = st.text_input(
        "DeepSeek API Key",
        type="password",
        value=st.session_state.api_key,
        help="在 platform.deepseek.com 注册获取"
    )
    if api_key != st.session_state.api_key:
        st.session_state.api_key = api_key
    
    if st.session_state.api_key:
        st.success("✅ API Key 已设置")
    else:
        st.warning("⚠️ 请设置 API Key 以使用生成功能")
    
    st.divider()
    
    # 重置按钮
    if st.button("🔄 重置所有数据", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        init_state()
        st.rerun()

# ============================================================
# 主页面标题
# ============================================================
st.markdown("<div class='main-header'>产品认知培训完整方案生成器</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>基于 ADDIE + Bloom + Kirkpatrick + 70-20-10 方法论框架，为任意企业软件产品生成覆盖培训全生命周期的完整方案</div>", unsafe_allow_html=True)

# ============================================================
# 使用说明
# ============================================================
with st.expander("📖 使用说明", expanded=False):
    st.markdown("""
    **本工具覆盖培训全生命周期 8 大步骤：**
    
    1. **产品理解校验** — 输入产品信息，AI提取结构化理解，用户确认后防止AI幻觉
    2. **培训参数设置** — 设置目标岗位、培训时长、经验水平等6个参数
    3. **自适应判断** — AI自动判断产品复杂度、考核方式、实操需求等级
    4. **培训蓝图** — 生成产品定位、模块全景、场景串讲、术语表、问答库、考核系统
    5. **软件实操任务** — 条件触发：L3深度实操/L2基础实操/L1无需实操
    6. **培训素材** — 生成PPT大纲、讲师手册、学员练习册、快速参考卡
    7. **学习迁移计划** — 30天计划，70-20-10模型，遗忘曲线对抗
    8. **效果评估框架** — Kirkpatrick四级：满意度→前后测→行为观察→ROI
    
    **注意：** 每个步骤完成后，点击"确认并进入下一步"，后续步骤会基于前面的结果生成。
    """)

# ============================================================
# Step 0: 产品理解校验
# ============================================================
step0_expanded = not st.session_state.step_completed[0]
with st.expander("📝 Step 0: 产品理解校验（防幻觉）", expanded=step0_expanded):
    st.markdown("<div class='info-box'>请先提供产品信息（任意格式：产品文档、简介、功能清单等）。AI会提取结构化理解并请你确认，防止后续生成中出现编造的功能。</div>", unsafe_allow_html=True)
    
    product_input = st.text_area(
        "粘贴产品信息",
        value=st.session_state.product_input,
        height=200,
        placeholder="请粘贴产品介绍、功能文档、官网描述等（支持任意格式，可混合）",
        help="信息越详细，AI理解越准确"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🚀 提取产品理解", use_container_width=True, disabled=not product_input.strip()):
            if not st.session_state.api_key:
                st.error("请先设置 API Key")
            else:
                prompt = f"请基于以下产品信息，提取结构化的产品理解：\n\n{product_input}"
                result, error = call_ai(SYS_PRODUCT_VALIDATION, prompt)
                if error:
                    st.error(error)
                else:
                    st.session_state.product_input = product_input
                    st.session_state.product_validation = result
                    # 解析结构化理解
                    lines = result.split("\n")
                    for line in lines:
                        if "产品类型" in line:
                            st.session_state.product_type = line.split("：")[-1].strip() if "：" in line else ""
                        elif "产品定位" in line:
                            st.session_state.product_positioning = line.split("：")[-1].strip() if "：" in line else ""
                        elif "核心模块" in line and "不确定" not in line:
                            st.session_state.core_modules = [m.strip() for m in line.split("：")[-1].split("、") if m.strip()]
                    st.rerun()
    
    if st.session_state.product_validation:
        st.markdown("---")
        st.subheader("AI 提取的产品理解")
        st.markdown(st.session_state.product_validation)
        
        st.markdown("<div class='warning-box'>⚠️ 请仔细检查上述理解是否正确，特别关注「不确定项」部分。如果理解有误，请修改上方的产品信息后重新提取。</div>", unsafe_allow_html=True)
        
        confirm = st.checkbox("✅ 我已确认上述产品理解正确，可以基于此生成培训方案")
        if confirm and not st.session_state.validation_confirmed:
            st.session_state.validation_confirmed = True
            st.session_state.step_completed[0] = True
            st.success("产品理解已确认，可以进入下一步")
            st.rerun()
        elif not confirm and st.session_state.validation_confirmed:
            st.session_state.validation_confirmed = False
            st.session_state.step_completed[0] = False
            st.rerun()

# ============================================================
# Step 1: 收集培训参数
# ============================================================
step1_expanded = st.session_state.step_completed[0] and not st.session_state.step_completed[1]
with st.expander("🎯 Step 1: 收集培训参数", expanded=step1_expanded):
    if not st.session_state.step_completed[0]:
        st.info("请先完成 Step 0 产品理解校验")
    else:
        st.markdown("<div class='info-box'>设置培训的基本参数，AI会根据这些参数调整内容深度、互动方式和考核方式。</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            target_role = st.selectbox(
                "目标岗位",
                ["销售", "售前顾问", "实施顾问", "实施工程师", "客服", "客户成功经理", 
                 "运维工程师", "技术支持", "产品经理", "市场专员", "行政", "财务", "人力资源", "其他"],
                index=0 if not st.session_state.target_role else ["销售", "售前顾问", "实施顾问", "实施工程师", "客服", "客户成功经理", "运维工程师", "技术支持", "产品经理", "市场专员", "行政", "财务", "人力资源", "其他"].index(st.session_state.target_role) if st.session_state.target_role in ["销售", "售前顾问", "实施顾问", "实施工程师", "客服", "客户成功经理", "运维工程师", "技术支持", "产品经理", "市场专员", "行政", "财务", "人力资源", "其他"] else 0
            )
            training_duration = st.selectbox(
                "培训时长",
                ["1天", "2天", "1周（5天）"],
                index=["1天", "2天", "1周（5天）"].index(st.session_state.training_duration)
            )
            experience_level = st.selectbox(
                "经验水平",
                ["新人（0-1年）", "有经验（1-5年）", "资深（5年+）"],
                index=["新人（0-1年）", "有经验（1-5年）", "资深（5年+）"].index(st.session_state.experience_level)
            )
        with col2:
            prior_knowledge = st.selectbox(
                "先验知识",
                ["完全不了解该类产品", "了解同类竞品", "已熟悉本公司其他产品"],
                index=["完全不了解该类产品", "了解同类竞品", "已熟悉本公司其他产品"].index(st.session_state.prior_knowledge)
            )
            team_size = st.selectbox(
                "团队规模",
                ["1对1培训", "小组培训（3-8人）", "批量培训（10人+）"],
                index=["1对1培训", "小组培训（3-8人）", "批量培训（10人+）"].index(st.session_state.team_size)
            )
        
        # 保存参数
        st.session_state.target_role = target_role
        st.session_state.training_duration = training_duration
        st.session_state.experience_level = experience_level
        st.session_state.prior_knowledge = prior_knowledge
        st.session_state.team_size = team_size
        
        st.session_state.training_params = {
            "target_role": target_role,
            "training_duration": training_duration,
            "experience_level": experience_level,
            "prior_knowledge": prior_knowledge,
            "team_size": team_size
        }
        
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
        st.markdown("<div class='info-box'>AI 根据产品信息和培训参数，自动判断复杂度、考核方式和实操等级。</div>", unsafe_allow_html=True)
        
        if st.button("🚀 开始自适应判断", use_container_width=True):
            if not st.session_state.api_key:
                st.error("请先设置 API Key")
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
                    # 解析结果
                    lines = result.split("\n")
                    for line in lines:
                        if "产品复杂度" in line and "判断" not in line:
                            st.session_state.complexity = line.split("：")[-1].strip().replace("[", "").replace("]", "").replace("简单", "简单").replace("中等", "中等").replace("复杂", "复杂")
                            if st.session_state.complexity not in ["简单", "中等", "复杂"]:
                                st.session_state.complexity = "中等"
                        elif "场景数量" in line:
                            try:
                                st.session_state.scene_count = int(line.split("：")[-1].strip().replace("个", ""))
                            except:
                                st.session_state.scene_count = 3
                        elif "术语数量" in line:
                            try:
                                st.session_state.term_count = int(line.split("：")[-1].strip().replace("个", ""))
                            except:
                                st.session_state.term_count = 8
                        elif "问答数量" in line:
                            try:
                                st.session_state.qa_count = int(line.split("：")[-1].strip().replace("条", ""))
                            except:
                                st.session_state.qa_count = 10
                        elif "实操等级" in line and "说明" not in line:
                            level = line.split("：")[-1].strip().replace("[", "").replace("]", "")
                            if "L3" in level:
                                st.session_state.hands_on_level = "L3"
                            elif "L2" in level:
                                st.session_state.hands_on_level = "L2"
                            elif "L1" in level:
                                st.session_state.hands_on_level = "L1"
                            else:
                                st.session_state.hands_on_level = "L2"
                    st.rerun()
        
        if st.session_state.adaptive_result:
            st.markdown("---")
            st.markdown(st.session_state.adaptive_result)
            
            # 展示关键判断结果
            st.markdown("---")
            st.subheader("关键判断摘要")
            cols = st.columns(4)
            with cols[0]:
                st.metric("产品复杂度", st.session_state.complexity)
            with cols[1]:
                st.metric("场景数量", f"{st.session_state.scene_count}个")
            with cols[2]:
                st.metric("术语数量", f"{st.session_state.term_count}个")
            with cols[3]:
                level_map = {"L3": "深度实操", "L2": "基础实操", "L1": "无需实操"}
                st.metric("实操等级", level_map.get(st.session_state.hands_on_level, "基础实操"))
            
            if st.button("✅ 确认判断结果并进入下一步", use_container_width=True):
                st.session_state.step_completed[2] = True
                st.rerun()

# ============================================================
# Step 3: 生成培训蓝图
# ============================================================
step3_expanded = st.session_state.step_completed[2] and not st.session_state.step_completed[3]
with st.expander("📋 Step 3: 生成培训蓝图", expanded=step3_expanded):
    if not st.session_state.step_completed[2]:
        st.info("请先完成 Step 2 自适应判断")
    else:
        if st.button("🚀 生成培训蓝图", use_container_width=True):
            if not st.session_state.api_key:
                st.error("请先设置 API Key")
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
            
            if st.button("✅ 确认蓝图并进入下一步", use_container_width=True):
                st.session_state.step_completed[3] = True
                st.rerun()

# ============================================================
# Step 4: 生成软件实操任务
# ============================================================
step4_expanded = st.session_state.step_completed[3] and not st.session_state.step_completed[4]
with st.expander("🔧 Step 4: 生成软件实操任务（条件触发）", expanded=step4_expanded):
    if not st.session_state.step_completed[3]:
        st.info("请先完成 Step 3 培训蓝图")
    else:
        level_map = {"L3": "深度实操", "L2": "基础实操", "L1": "无需实操"}
        level_name = level_map.get(st.session_state.hands_on_level, "基础实操")
        st.markdown(f"<div class='info-box'>当前岗位「{st.session_state.target_role}」的实操等级为 **{st.session_state.hands_on_level}（{level_name}）**。{'将生成实操任务设计。' if st.session_state.hands_on_level in ['L3', 'L2'] else '无需实操，将生成产品价值速览卡。'}</div>", unsafe_allow_html=True)
        
        if st.button("🚀 生成实操任务", use_container_width=True):
            if not st.session_state.api_key:
                st.error("请先设置 API Key")
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
            
            if st.button("✅ 确认并进入下一步", use_container_width=True):
                st.session_state.step_completed[4] = True
                st.rerun()

# ============================================================
# Step 5: 生成考核系统
# ============================================================
step5_expanded = st.session_state.step_completed[4] and not st.session_state.step_completed[5]
with st.expander("🎯 Step 5: 生成考核系统", expanded=step5_expanded):
    if not st.session_state.step_completed[4]:
        st.info("请先完成 Step 4 实操任务")
    else:
        if st.button("🚀 生成考核系统", use_container_width=True):
            if not st.session_state.api_key:
                st.error("请先设置 API Key")
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
            
            if st.button("✅ 确认并进入下一步", use_container_width=True):
                st.session_state.step_completed[5] = True
                st.rerun()

# ============================================================
# Step 6: 生成培训素材
# ============================================================
step6_expanded = st.session_state.step_completed[5] and not st.session_state.step_completed[6]
with st.expander("📑 Step 6: 生成培训素材", expanded=step6_expanded):
    if not st.session_state.step_completed[5]:
        st.info("请先完成 Step 5 考核系统")
    else:
        if st.button("🚀 生成培训素材", use_container_width=True):
            if not st.session_state.api_key:
                st.error("请先设置 API Key")
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
            
            if st.button("✅ 确认并进入下一步", use_container_width=True):
                st.session_state.step_completed[6] = True
                st.rerun()

# ============================================================
# Step 7: 生成学习迁移计划
# ============================================================
step7_expanded = st.session_state.step_completed[6] and not st.session_state.step_completed[7]
with st.expander("🔄 Step 7: 生成学习迁移计划（30天）", expanded=step7_expanded):
    if not st.session_state.step_completed[6]:
        st.info("请先完成 Step 6 培训素材")
    else:
        if st.button("🚀 生成学习迁移计划", use_container_width=True):
            if not st.session_state.api_key:
                st.error("请先设置 API Key")
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
            
            if st.button("✅ 确认并进入下一步", use_container_width=True):
                st.session_state.step_completed[7] = True
                st.rerun()

# ============================================================
# Step 8: 生成效果评估框架
# ============================================================
step8_expanded = st.session_state.step_completed[7] and not st.session_state.step_completed[8]
with st.expander("📊 Step 8: 生成效果评估框架（Kirkpatrick四级）", expanded=step8_expanded):
    if not st.session_state.step_completed[7]:
        st.info("请先完成 Step 7 学习迁移计划")
    else:
        if st.button("🚀 生成评估框架", use_container_width=True):
            if not st.session_state.api_key:
                st.error("请先设置 API Key")
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
            
            if st.button("🎉 完成全部生成！", use_container_width=True):
                st.session_state.step_completed[8] = True
                st.rerun()

# ============================================================
# 完成页
# ============================================================
if st.session_state.step_completed[8]:
    st.divider()
    st.markdown("<div class='main-header' style='text-align:center;'>🎉 培训方案生成完成！</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header' style='text-align:center;'>所有 8 个步骤已完成，以下是完整的培训方案汇总</div>", unsafe_allow_html=True)
    
    # 下载功能
    full_report = f"""# {st.session_state.product_positioning or '产品'} 认知培训完整方案

**目标岗位**：{st.session_state.target_role}  |  **培训时长**：{st.session_state.training_duration}
**经验水平**：{st.session_state.experience_level}  |  **先验知识**：{st.session_state.prior_knowledge}  |  **团队规模**：{st.session_state.team_size}
**产品复杂度**：{st.session_state.complexity}  |  **实操等级**：{st.session_state.hands_on_level}

---

# 第一部分：产品理解校验

{st.session_state.product_validation}

---

# 第二部分：自适应判断

{st.session_state.adaptive_result}

---

# 第三部分：培训蓝图

{st.session_state.blueprint}

---

# 第四部分：软件实操任务

{st.session_state.hands_on_tasks}

---

# 第五部分：考核系统

{st.session_state.assessment}

---

# 第六部分：培训素材

{st.session_state.materials}

---

# 第七部分：学习迁移计划（30天）

{st.session_state.transfer_plan}

---

# 第八部分：效果评估框架（Kirkpatrick四级）

{st.session_state.evaluation}

---

> 本方案由 AI+培训设计器 v3.1 生成
> 基于 ADDIE + Bloom + Kirkpatrick + 70-20-10 方法论框架
"""
    
    st.download_button(
        label="📥 下载完整方案（Markdown）",
        data=full_report,
        file_name=f"training_plan_{st.session_state.target_role}.md",
        mime="text/markdown",
        use_container_width=True
    )
