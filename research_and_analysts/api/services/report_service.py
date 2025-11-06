import uuid
import os
from fastapi.responses import FileResponse
from research_and_analysts.utils.model_loader import ModelLoader
from research_and_analysts.workflows.report_generation_workflow import AutonomousReportGenerator
from research_and_analysts.logger import GLOBAL_LOGGER
from research_and_analysts.exceptions.custom_exception import ResearchAnalystException
from langgraph.checkpoint.memory import MemorySaver

_shared_memory = MemorySaver()

class ReportService:
    def __init__(self):
        self.llm = ModelLoader().load_llm()
        self.reporter = AutonomousReportGenerator(self.llm)
        self.reporter.memory = _shared_memory
        self.graph = self.reporter.build_graph()
        self.logger = GLOBAL_LOGGER.bind(module='ReportService')

    def start_report_generation(self, topic:str, max_analyst:int):
        pass

    def submit_feedback(self,thread_id:str, feedback:str):
        pass

    def get_report_status(self, thread_id:str):
        pass
    
    @staticmethod
    def download_file(file_name:str):
        pass