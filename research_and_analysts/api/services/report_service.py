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
        try:
            thread_id = str(uuid.uuid4())
            thread = {"configurable":{"thread_id":thread_id}}
            self.logger.info("Starting report pipeline", topic=topic, thread_id=thread_id)
            for _ in self.graph({"topic":topic, "max_analysts":max_analyst}, thread, stream_mode="values"):
                pass
            return {"thread_id":thread_id, "message":"Pipeline initiated successfully."}
        except Exception as e:
            self.logger.error("Error starting report generation", error=str(e))
            raise ResearchAnalystException("Failed to start report generation", e)

    def submit_feedback(self,thread_id:str, feedback:str):
        try:
            thread = {"configurable":{"thread_id":thread_id}}
            self.graph.update_state(thread, {"human_analyst_feedback":feedback}, as_node="human_feedback")
            self.logger.info("Feedback updated", thread_id=thread_id)
            for _ in self.graph.stream(None, thread, stream_node="values"):
                return {"message":"Feedback processed successfully"}
            
        except Exception as e:
            self.logger.error("Error submitting feedback", error=str(e))
            raise ResearchAnalystException("Failed to submit feedback", e)

    def get_report_status(self, thread_id:str):
        pass
    
    @staticmethod
    def download_file(file_name:str):
        pass