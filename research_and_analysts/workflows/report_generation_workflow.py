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
from research_and_analysts.prompt_lib.prompt_locator import(
    CREATE_ANALYSTS_PROMPT,
    INTRO_CONCLUSION_INSTRUCTIONS,
    REPORT_WRITER_INSTRUCTIONS,
)
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
        topic = state['topic']
        max_analysts = state['max_analysts']
        human_analyst_feedback = state.get("human_analyst_feedback","")

        try:
            self.logger.info("Createing analyst personas", topic=topic)
            structured_llm = self.llm.with_structured_output(Perspectives)
            system_prompt = CREATE_ANALYSTS_PROMPT.render(
                topic = topic,
                max_analysts = max_analysts,
                human_analyst_feedback = human_analyst_feedback
            )
            analysts = structured_llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content="Generate the set of analysts."),
            ])
            self.logger.info("Analyst created", count = len(analysts.analysts))
            return {"analysts":analysts.analysts}

        except Exception as e:
            self.logger.error("Error creating analysts", error=str(e))
            raise ResearchAnalystException("Failed to create analysts", e)

    def human_feedback(self, state:ResearchGraphState):
        try:
            self.logger.info("Awaiting human feedback")
        except Exception as e:
            self.logger.error("Error during feedback stage", error = str(e))
            raise ResearchAnalystException("Human feedback node failed", e)

    def write_report(self, state:ResearchGraphState):
        pass

    def write_introduction(self, state:ResearchGraphState):
        pass

    def write_conclusion(self, state:ResearchGraphState):
        pass

    def finalize_report(self, state:ResearchGraphState):
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
            builder.add_node("generate_answer", interview_graph)
            builder.add_node("write_report", self.write_report)
            builder.add_node("write_introduction", self.write_introduction)
            builder.add_node("write_conclusion", self.write_conclusion)
            builder.add_node("finalize_report", self.finalize_report)

            builder.add_edge(START, "create_analyst")
            builder.add_edge("create_analyst", "human_feedback")
            builder.add_conditional_edges(
                "human_feedback",
                initiate_all_interview,
                ["conduct_interview", END]
            )
            builder.add_edge("conduct_interview", "write_report")
            builder.add_edge("conduct_interview", "write_introduction")
            builder.add_edge("conduct_interview", "write_conclusion")

            builder.add_edge(["write_report", "write_introduction", "write_conclusion"],"final_report")
            builder.add_edge("final_report", END)

            graph = builder.compile(interrupt_before=["human_feedback"], checkpointer=self.memory)
            self.logger.info("Report generation graph built successfully")
            return graph

        except Exception as e:
            self.logger.error("Error building report graph", error=str(e))
            raise ResearchAnalystException("Failed to build report generation graph", e)