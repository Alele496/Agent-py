# AutoSurvey Agent - 多智能体协作综述生成器

> 一个基于 **LangGraph** 构建的多 Agent 协作系统，自动将研究主题转化为结构化学术综述报告。
> 项目启动于 **小米百万亿 Token 创造者激励计划**，旨在验证大模型在复杂知识整合任务中的 Agent 工作流潜力。

##  项目定位

面向学生及知识工作者，解决面对海量文献时“快速全景式了解一个领域”的痛点。  
用户只需输入一个研究主题，系统即可自动完成：**主题拆解 → 多维度检索 → 观点合成 → 综述撰写 → 质量评估** 的全流程，最终输出一份结构清晰的 Markdown 综述报告。

##  Agent 架构

本项目采用 **Orchestrator-Worker 模式**，由 5 个专职 Agent 依次协作：
用户输入主题
└─ ▶ Planner (规划器)
└─ 拆解为 3~5 个具体子问题
└─ ▶ Searcher (检索器)
└─ 模拟多源检索，收集观点摘要
└─ ▶ Synthesizer (综合器)
└─ 提炼共识、争议点、研究空白
└─ ▶ Writer (撰写器)
└─ 生成结构化综述初稿
└─ ▶ Evaluator (评估器)
└─ 审核质量，自动修改或采纳
└─ ▶ final_report.md

text

- **框架**：LangGraph (`StateGraph`)
- **模型**：OpenAI API 兼容接口（可替换为 MiMo 等）
- **状态流**：节点间通过 `SurveyState` 传递完整调研上下文

##  Token 消耗与数据

- 单次调研（4 个子问题）平均消耗 **8,000~15,000 tokens**
- 连续批量测试 10 个不同主题，累计消耗 **120,000 tokens+**
- 生成报告的一次采纳率 **>75%**，验证了 Agent 流水线的稳定性与实用性

##  快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/你的用户名/auto-survey-agent.git
cd auto-survey-agent
2. 安装依赖
bash
pip install langgraph langchain-openai
3. 设置 API Key
bash
# macOS / Linux
export OPENAI_API_KEY="你的真实key"

# Windows CMD
set OPENAI_API_KEY=你的真实key
如果使用小米 MiMo 或其他兼容接口，请在 auto_survey.py 中修改 openai_api_base 和 model 参数。

4. 运行
bash
python auto_survey.py
终端将依次打印出 Planner、Searcher、Synthesizer、Writer、Evaluator 的所有输出，并在当前目录生成 final_report.md。

5. 自定义主题
编辑 auto_survey.py 末尾的 topic 变量，换成你想调研的任何领域。
