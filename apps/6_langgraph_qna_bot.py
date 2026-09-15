from dotenv import load_dotenv
load_dotenv()
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from typing import Annotated


class ChatState(BaseModel):
    messages: Annotated[list, add_messages]

llm = ChatGroq(model = "openai/gpt-oss-20b")

def chatBotNode(state:ChatState) -> ChatState:
    res = llm.invoke(state.messages)
    state.messages = [res]
    return state

memory = InMemorySaver()
graph = StateGraph(ChatState)
graph.add_node("chatbotnode", chatBotNode)

graph.add_edge(START, "chatbotnode")
graph.add_edge("chatbotnode", END)

graph = graph.compile(checkpointer=memory)

while True:
    query = input("User :")
    if query.lower() in ["quit","exit"]:
        print("Thank You bye")
        break
    response = graph.invoke(
        {"messages":[{"role":"user", "content":query}]}, 
        {"configurable": {"thread_id": "yash"}},
        )
    res = response["messages"][-1].content
    print("AI :", res)