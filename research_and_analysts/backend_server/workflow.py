import os
import re
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
    ResearchGraphState,
    SearchQuery
)
from research_and_analysts.prompt_lib.prompts import *


def build_interview_graph(llm, travily_search=None):
    memory = MemorySaver()
    def generate_question(state:InterviewState):
        analyst = state["analyst"]
        messages = state["messages"]
        context = state["context"]

        system_message = ANALYST_ASK_QUESTIONS.format(goals=analyst.persona,context=context)
        answer = llm.invoke([SystemMessage(content=system_message)]+messages)

        answer.name = "expert"

        return {"messages":[answer]}

    def search_web(state:InterviewState):
        structured_llm = llm.with_structured_output(SearchQuery)
        search_query = structured_llm.invoke([GENERATE_SEARCH_QUERY]+state["messages"])

        search_docs = travily_search.invoke(search_query.search_query)
        formatted_search_docs = "\n\n---\n\n".join(
            [
                f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
                for doc in search_docs
            ]
        )
        return {"context": [formatted_search_docs]}

    def generate_answer(state:InterviewState):
        analyst = state["analyst"]
        messages = state["messages"]
        context = state["context"]

        system_message = GENERATE_ANSWERS.format(goals=analyst.persona,context=context)
        answer = llm.invoke([SystemMessage(content=system_message)]+messages)

        answer.name = "expert"

        return {"messages":[answer]}

    def save_interview(state:InterviewState):
        messages = state["messages"]

        interview = get_buffer_string(messages)

        return {"interview":interview}

    def write_section(state:InterviewState):
        context = state["context"]
        analyst = state["analyst"]

        system_message = WRITE_SECTION.format(focus=analyst.description)
        section = llm.invoke([SystemMessage(content=system_message)]+[HumanMessage(content=f"Use this source to write your section: {context}")])

        return {"sections":[section.content]}

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
    def __init__(self, llm):
        self.llm = llm
        self.memory = MemorySaver()
        self.tavily_search = TavilySearchResults(
            travily_api_key = "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"
        )

    def create_analyst(self, state: GenerateAnalystsState):
        
        structured_llm = self.llm.with_structured_output(Perspectives)
        analysts = structured_llm.invoke([
            SystemMessage(content=CREATE_ANALYSTS_PROMPT),
            HumanMessage(content="Generate the set of analysts.")
            ]
        )
        return {"analysts":analysts.analyst}

    def human_feedback(self, state:ResearchGraphState):
        pass


    def write_report(self, state:ResearchGraphState):
        sections = state.get("sections",[])
        topic = state.get("topic","")
        system_message = f"You are compiling a unified research report on{topic}"

        if not sections:
            sections = ["No sections generated - please verify interview stage."]
        report = self.llm.invoke([
            SystemMessage(content=system_message),
            HumanMessage(content="\n\n".join(sections))
        ])
        return {"content": report.content}

    def write_introduction(self):
        sections = state["sections"]
        topic = state["topic"]

        formatted_str_sections = "\n\n".join([f"{section}" for section in sections])

        instructions = S.format(topic=topic, formatted_str_sections = formatted_str_sections)
        intro = llm.invoke([SystemMessage(content=instructions)]+[HumanMessage(content=f"write the report introduction")])
        return {'introduction':intro.content}

    def write_conclusion(self):
        pass

    def finalize_report(self):
        pass

    def save_report(self,final_report:str, topic:str, format:str="docx", save_dir : str=None):
        safe_topic = re.sub(r'[\\/*?:<>|]',"_", topic)
        file_name = f"{safe_topic.replace(' ','_')}_{timestamp}.{format}"
        if save_dir is None:
            save_dir = os.path.join(os.getcwd(), "generated_report")
        os.makedirs(save_dir, exist_ok=True)

        file_path = os.path.join(save_dir, file_name)
        if format == "docx":
            self._save_as_docs(final_report, file_path)
        elif format == "pdf":
            self._save_as_pdf(final_report, file_path)
        else:
            raise ValueError("Invalid format. Use 'docx' or 'pdf'.")

        print(f"Report saved: {file_path}")
        return file_path

    def _save_as_docs(self, text:str, file_path:str):
        doc = Document()

    def _save_as_pdf(self):
        pass

    def build_graph(self):
        builder = StateGraph(ResearchGraphState)

        interview_graph = build_interview_graph(self.llm, self.tavily_search)

        def initial_all_interview(state:ResearchGraphState):
            topic = state["topic"]
            analysts = state.get("analysts",[])
            if not analysts:
                print("No analysts found - skipping interviewa.")
                return(END)
            return [
                Send(
                    "conduct_interview",{
                        "analyst":analyst,
                        "messages": [HumanMessage(content=f"So let's discuss about {topic}.")],
                        "max_num_turn":2,
                        "context":[],
                        "interview": "",
                        "sections":[],
                    }
                )
                for analyst in analysts
            ]

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

    reporter = AutonomousReportGenerator(llm)
    graph = reporter.build_graph()
    topic = ""

    thread = {"configurable":{"thread_id":"1"}}
    for _ in graph.stream({"topic":topic, "max_analyst":3}, thread, stream_mode="values"):
        pass

    state = graph.get_state(thread)
    feedback = input("\n Enter your feedback or press Enter to eontinue as is: ").strip()

    graph.update_state(thread,{"human_analyst_feedback":feedback}, as_node="human_feedback")

    for _ in graph.stream(None, thread, stream_mode="values"):pass

    final_state = graph.get_state(thread)
    final_report = final_state.values.get("final_report")

    if final_report:
        reporter.save_report(final_report,"topic","docx")
        reporter.save_report(final_report,"topic","pdf")
    else:
        print("No Report Content Generated")


