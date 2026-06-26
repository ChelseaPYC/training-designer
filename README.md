# AI+培训设计器 v3.1

基于 ADDIE + Bloom + Kirkpatrick + 70-20-10 方法论框架，为任意企业软件产品生成覆盖培训全生命周期的完整方案。

## 功能覆盖

| 步骤 | 功能 | 方法论 |
|------|------|--------|
| Step 0 | 产品理解校验（防AI幻觉） | 结构化提取 + 用户确认 |
| Step 1 | 培训参数设置（6个维度） | 受众画像细化 |
| Step 2 | 自适应判断（复杂度/考核/实操等级） | 复杂度自适应规则 |
| Step 3 | 培训蓝图（6模块） | ADDIE + Bloom |
| Step 4 | 软件实操任务（条件触发） | L3/L2/L1分级设计 |
| Step 5 | 考核系统（3类考核） | 场景分析+实操演练+模拟答辩 |
| Step 6 | 培训素材（4类素材） | PPT大纲+讲师手册+练习册+参考卡 |
| Step 7 | 学习迁移计划（30天） | 70-20-10 + 遗忘曲线对抗 |
| Step 8 | 效果评估框架 | Kirkpatrick四级评估 |

## 部署方式

### Streamlit Cloud（推荐）

1. Fork 本仓库到你的 GitHub 账户
2. 登录 [share.streamlit.io](https://share.streamlit.io)
3. 连接 GitHub，选择本仓库
4. 点击 Deploy

### 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 使用说明

1. 打开网页后，在左侧边栏输入你的 DeepSeek API Key
2. 按步骤依次完成：粘贴产品信息 → 设置培训参数 → AI自动生成完整方案
3. 最后可下载完整的 Markdown 格式培训方案

## 技术栈

- Python + Streamlit
- DeepSeek API (deepseek-chat)

## 版本历史

- v3.1：新增软件实操任务分级设计（L3深度/L2基础/L1无需）
- v3.0：全生命周期升级（产品校验、受众画像、复杂度自适应、3类考核、培训素材、学习迁移、Kirkpatrick四级评估）
