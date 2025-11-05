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
from research_and_analysts.prompt_lib.prompt_locator import(
    ANALYST_ASK_QUESTIONS,
    GENERATE_SEARCH_QUERY,
    GENERATE_ANSWERS,
    WRITE_SECTION
)

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
        analyst = state["analyst"]
        messages = state["messages"]

        try:
            self.logger.info("Generating analyst question", analyst=analyst.name)
            system_prompt = ANALYST_ASK_QUESTIONS.render(goals = analyst.persona)
            question = self.llm.invoke([SystemMessage(content=system_prompt)]+messages)
            self.logger.info("Question generated successfully", question_preview = question.content[:200])
            return {"messages":[question]}
        
        except Exception as e:
            self.logger.error("Error generating analyst question", error = str(e))
            raise ResearchAnalystException("Failed to generate analyst question", e)
        

    def web_search(self, state:InterviewState):
        try:
            self.logger.info("Generating search query from conversation")
            structured_llm = self.llm.with_structured_output(SearchQuery)
            search_prompt = GENERATE_SEARCH_QUERY.render()
            search_query = structured_llm.invoke([SystemMessage(content=search_prompt)]+state["messages"])
            self.logger.info("Performing Tavily web search", query = search_query.search_query)

            search_docs = self.tavily_search.invoke(search_query.search_query)

            if not search_query:
                self.logger.warning("No search result found")
                return {"context":["[No resarch results found]."]}
            formatted = "\n\n---\n\n".join(
                [
                    f'<Document href="{doc.get("url", "#")}"/>\n{doc.get("content", "")}\n</Document>'
                    for doc in search_docs
                ]
            )
            self.logger.info("Web search completed", result_count=len(search_docs))
            return {"context":[formatted]}
        except Exception as e:
            self.logger.error("Error during web search", error = str(e))
            raise ResearchAnalystException("Failed during web search excecution", e)

    def _generate_answer(self, state:InterviewState):
        analyst = state['analyst']
        messages = state['messages']
        context = state.get('context',["[No context available.]"])

        try:
            self.logger.info("Generating expert answer", analyst=analyst.name)
            system_prompt = GENERATE_ANSWERS.render(goals = analyst.persona, context=context)
            answer = self.llm.invoke([SystemMessage(content=system_prompt)]+messages)
            answer.name = "expert"
            self.logger.info("Expert answer generated successfully", preview = answer.content[:200])
            return {"messages":[answer]}
        except Exception as e:
            self.logger.info("Error generating expert answer", error=str(e))
            raise ResearchAnalystException("Failed to generate expert answer", e)

    def _save_interview(self, state:InterviewState):
        try:
            messages = state["messages"]
            interview = get_buffer_string(messages)
            self.logger.info("Interview transcription saved", message_count = len(messages))
            return {"interview":interview}
        
        except Exception as e:
            self.logger.error("Error saving interview transcription", error=str(e))
            raise ResearchAnalystException("Failed to saveinterview transcription", e)

    def _write_section(self, state:InterviewState):
        context = state.get("context", ["[No context available.]"])
        analyst = state['analyst']

        try:
            self.logger.info("Generating report section", analyst=analyst.name)
            system_prompt = WRITE_SECTION.render(focus=analyst.description)
            section = self.llm.invoke(
                [SystemMessage(content=system_prompt)]+
                [HumanMessage(content=f"Use this source to write your section: {context}")]
            )
            self.logger.info("Report section generated successfully", length = len(section.content))
            return {"sections":[section.content]}
        
        except Exception as e:
            self.logger.error("Error writing report section", error=str(e))
            raise ResearchAnalystException("Failed to generate report section", e)

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



