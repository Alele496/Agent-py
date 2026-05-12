import os
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

# ---------- 1. 状态定义 ----------
class SurveyState(TypedDict):
    topic: str                      # 用户输入的研究主题
    sub_questions: List[str]        # Planner 拆解出的子问题
    search_results: List[str]       # 检索到的摘要/观点
    synthesized_notes: str          # 聚合后的笔记
    draft_report: str               # 初稿报告
    final_report: str               # 最终报告（经评估后可能改写）
    evaluation_feedback: str        # 评估反馈

# ---------- 2. 初始化 LLM ----------
# API Key 和 Base URL（兼容 OpenAI 格式）
llm = ChatOpenAI(
    model="gpt-3.5-turbo", 
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY"),  
    # openai_api_base="https://api.xiaomimimo.com/v1"  
)

# ---------- 3. 定义各 Agent 节点 ----------
def planner(state: SurveyState) -> SurveyState:
    prompt = f"""你是一个研究规划专家。请将研究主题拆分为3-5个具体的子问题，用于全面调研。
研究主题：{state['topic']}
直接返回子问题列表，每行一个，不要编号。"""
    response = llm.invoke(prompt).content
    sub_questions = [q.strip() for q in response.split('\n') if q.strip()]
    return {"sub_questions": sub_questions}

def searcher(state: SurveyState) -> SurveyState:
    # 模拟多源检索，实际可以接真实搜索 API
    results = []
    for q in state['sub_questions']:
        prompt = f"""你是一个信息检索专家。针对以下子问题，请生成2-3条相关的学术观点或发现摘要，并注明可能的来源类型（例如：论文、技术报告、行业观察）。
子问题：{q}
每条摘要控制在30字以内。"""
        res = llm.invoke(prompt).content
        results.append(f"【子问题】{q}\n{res}")
    return {"search_results": results}

def synthesizer(state: SurveyState) -> SurveyState:
    all_results = "\n\n".join(state['search_results'])
    prompt = f"""你是一个信息分析专家。请根据以下检索到的材料，提炼出核心观点、共识、争议点和研究空白，并用结构化笔记的形式呈现。
材料：
{all_results}
笔记格式：使用 Markdown 的二级标题（##）和列表。"""
    notes = llm.invoke(prompt).content
    return {"synthesized_notes": notes}

def writer(state: SurveyState) -> SurveyState:
    prompt = f"""你是一位擅长撰写学术综述的写作者。请基于下面的笔记，撰写一份结构清晰的综述报告（Markdown格式）。
笔记：
{state['synthesized_notes']}
报告需包含：
1. 摘要
2. 当前研究现状
3. 主要挑战与争议
4. 未来展望
5. 参考文献（根据前面出现的来源模拟列出3-5条）
"""
    draft = llm.invoke(prompt).content
    return {"draft_report": draft}

def evaluator(state: SurveyState) -> SurveyState:
    prompt = f"""你是一位严格的学术评审。请对以下综述初稿进行评价，指出其优点、不足，并给出修改建议。
初稿：
{state['draft_report']}
如果质量已达到发布标准，请在反馈末尾注明“【合格】”。如果不够好，也请注明。"""
    feedback = llm.invoke(prompt).content
    # 简单判定：如果反馈里包含“合格”，则直接采用初稿，否则尝试简单修改
    if "【合格】" in feedback:
        final = state['draft_report']
    else:
        revise_prompt = f"""请根据以下评审意见，对初稿进行最终润色和补充，生成最终版综述报告。
评审意见：{feedback}
初稿：{state['draft_report']}
直接输出最终报告。"""
        final = llm.invoke(revise_prompt).content
    return {"evaluation_feedback": feedback, "final_report": final}

# ---------- 4. 构建状态图 ----------
workflow = StateGraph(SurveyState)

workflow.add_node("planner", planner)
workflow.add_node("searcher", searcher)
workflow.add_node("synthesizer", synthesizer)
workflow.add_node("writer", writer)
workflow.add_node("evaluator", evaluator)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "searcher")
workflow.add_edge("searcher", "synthesizer")
workflow.add_edge("synthesizer", "writer")
workflow.add_edge("writer", "evaluator")
workflow.add_edge("evaluator", END)

app = workflow.compile()

# ---------- 5. 运行主程序 ----------
if __name__ == "__main__":
    topic = "大语言模型在医疗领域的应用与挑战"
    print(f"🚀 开始调研主题：{topic}\n")
    inputs = {"topic": topic}

    # 流式输出每一步的结果（便于截取终端截图）
    for step_output in app.stream(inputs):
        node_name = list(step_output.keys())[0]
        print(f"\n{'='*20} {node_name.upper()} 输出 {'='*20}")
        # 打印该节点返回的更新内容
        for key, value in step_output[node_name].items():
            print(f"[{key}]:\n{value}\n")

    # 最终报告单独保存
    final_state = app.invoke(inputs)
    report = final_state.get("final_report", "")
    with open("final_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("\n✅ 最终综述报告已保存至 final_report.md")
