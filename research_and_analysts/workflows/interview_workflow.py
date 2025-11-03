from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.messages import get_buffer_string
from langgraph.types import Send
from IPython.display import Image, display
import os
import sys

currnt_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(currnt_dir,"../../"))
sys.path.append(project_root)

from research_and_analysts.schemas.models import InterviewState, SearchQuery

from research_and_analysts.utils.model_loader import ModelLoader
from research_and_analysts.logger import GLOBAL_LOGGER
from research_and_analysts.exceptions.custom_exception import ResearchAnalystException

class InterviewGraphBuilder:
    def __init__(self, llm, tavily_search):
        self.llm = llm
        self.logger = GLOBAL_LOGGER.bind(module="InterviewGraphBuilder")
        self.memory = MemorySaver()
        self.tavily_search = tavily_search

    def _generate_question(self, state:InterviewState):
        pass

    def web_search(self, state:InterviewState):
        pass

    def _generate_answer(self, state:InterviewState):
        pass

    def _save_interview(self, state:InterviewState):
        pass

    def _write_section(self, state:InterviewState):
        pass

    def build(self):
        try:
            self.logger.info("Building Interview Graph workflow")
            builder = StateGraph(InterviewState)

            builder.add_node("ask_question", self._generate_question)
            builder.add_node("search_web", self.web_search)
            builder.add_node("generate_answer", self._generate_answer)
            builder.add_node("save_interview", self._save_interview)
            builder.add_node("write_section", self._write_section)

            builder.add_edge(START, "ask_question")
            builder.add_edge("ask_question","search_web")
            builder.add_edge("search_web", "generate_answer")
            builder.add_edge("generate_answer", "save_interview")
            builder.add_edge("save_interview", "write_section")
            builder.add_edge("write_section", END)

            graph = builder.compile(checkpointer=self.memory)
            self.logger.info("Interview Graph compiled successfully")

            return graph


        except Exception as e:
            self.logger.error("Error building interview graph", error=str(e))

# if __name__ == "__main__":
#     llm = ModelLoader().load_llm()
#     interview = InterviewGraphBuilder(llm)
#     graph = interview.build()
#     img_bytes = graph.get_graph(xray=1).draw_mermaid_png()
#     out_path = os.path.join(project_root,"interview.png")

#     with open(out_path,"wb") as f:
#         f.write(img_bytes)
#     print("Saved graph image to: ", out_path)



