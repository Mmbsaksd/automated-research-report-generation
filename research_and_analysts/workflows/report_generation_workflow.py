import os
import sys
import re
from datetime import date
from typing import Optional
from langgraph.types import Send
from jinja2 import Template

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir,"../../"))
sys.path.append(project_root)

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.tools.tavily_search import TavilySearchResults

from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from research_and_analysts.schemas.models import (
    Perspectives,
    GenerateAnalystsState,
    ResearchGraphState
)
from research_and_analysts.utils.model_loader import ModelLoader
from research_and_analysts.workflows.interview_workflow import InterviewGraphBuilder
from research_and_analysts.logger import GLOBAL_LOGGER
from research_and_analysts.exceptions.custom_exception import ResearchAnalystException

class AutonomousReportGenerator:
    def __init__(self,llm):
        self.llm = llm
        self.memory = MemorySaver()
        self.tavily_search = TavilySearchResults(
            travily_api_key = "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"
        )
        self.logger = GLOBAL_LOGGER.bind(module="AutonomousReportGenerator")
    
    def create_analyst(self, state: ResearchGraphState):
        pass

    def human_feedback(self, state:ResearchGraphState):
        pass


    def build_graph(self):
        try:
            self.logger.info("Building report generation graph")
            builder = StateGraph(ResearchGraphState)
            interview_graph = InterviewGraphBuilder(self.llm, self.tavily_search).build()

            def initiate_all_interview(state: ResearchGraphState):
                pass

            builder.add_node("create_analyst", self.create_analyst)
            builder.add_node("human_feedback", self.human_feedback)
            builder.add_node


        except Exception as e:
            self.logger.error("Error building report graph", error=str(e))
            raise ResearchAnalystException("Failed to build report generation graph", e)