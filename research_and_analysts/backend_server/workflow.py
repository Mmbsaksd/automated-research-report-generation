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
        pass

if __name__ == "__main__":
    llm = ModelLoader().load_llm()
    print(llm.invoke("hello").content)

    report = AutonomousReportGenerator()
    report.build_graph()
