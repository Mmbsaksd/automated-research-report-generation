import os
import sys
from datetime import datetime
from typing import Optional
from langgraph.types import Send

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(project_root)

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.messages import get_buffer_string
from langchain_community.tools import TavilySearchResults

from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from research_and_analysts.schemas.models import(
    Analyst,
    Perspectives,
    GenerateAnalystsState,
    InterviewState,
    ResearchGraphState
)
def build_interview_graph(llm, travily_search=None):
    memory = MemorySaver()
    def generate_question(state:InterviewState):
        pass

    def search_web(state:InterviewState):
        pass

    def generate_answer(state:InterviewState):
        pass

    def save_interview(state:InterviewState):
        pass

    def write_section(state:InterviewState):
        pass

    builder = StateGraph(InterviewState)
    builder.add_node("ask_question", generate_question)
    builder.add_node("search_web", search_web)
    builder.add_node("generate_answer",generate_answer)
    builder.add_node("save_interview", save_interview)
    builder.add_node("write_section", write_section)

    builder.add_edge(START, "ask_question")
    builder.add_edge("ask_question", "search_web")
    builder.add_edge("search_web","generate_answer")
    builder.add_edge("generate_answer","save_interview")
    builder.add_edge("save_interview","write_section")
    builder.add_edge("write_section", END)

    return builder.compile(checkpointer=memory)



from research_and_analysts.utils.model_loader import ModelLoader

class AutonomousReportGenerator:
    def __init__(self):
        pass

    def create_analyst(self):
        pass

    def human_feedback(self):
        pass

    def write_report(self):
        pass

    def write_introduction(self):
        pass

    def write_conclusion(self):
        pass

    def finalize_report(self):
        pass

    def save_report(self):
        pass

    def _save_as_docs(self):
        pass

    def _save_as_pdf(self):
        pass

    def build_graph(self):
        builder = StateGraph(ResearchGraphState)

        builder.add_node("create_analyst", self.create_analyst)
        builder.add_node("human_feedback", self.human_feedback)
        builder.add_node("conduct_interview", interview_graph)
        builder.add_node("write_report",self.write_report)
        builder.add_node("write_introduction",self.write_introduction)
        builder.add_node("write_conclusion",self.write_conclusion)
        builder.add_node("write_conclusion",self.finalize_report)

        #Edge
        builder.add_edge(START,"create_analyst")
        builder.add_edge("create_analyst","human_feedback")
        builder.add_conditional_edges("human_feedback", initial_all_interview, ["conduct_interview"])

        builder.add_edge("conduct_interview","write_report")
        builder.add_edge("conduct_interview", "write_introduction")
        builder.add_edge("conduct_interview", "write_conclusion")
        builder.add_edge(["write_report", "write_introduction","write_conclusion"],"finalize_report")
        builder.add_edge("finalize_report",END)

        return builder.compile(interrupt_before=["human_feedback"], checkpointer=self.memory)

if __name__ == "__main__":
    llm = ModelLoader().load_llm()
    print(llm.invoke("hello").content)

    report = AutonomousReportGenerator()
    report.build_graph()
