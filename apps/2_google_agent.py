##for Now I am commenting the chat_history and also the way I am appending the msgs to memory because we can use the MemorySaver from Langgraph and it is easy to understand and shorter

from dotenv import load_dotenv
load_dotenv()

from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
##from langchain.messages import AIMessage, HumanMessage

model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
search = GoogleSerperAPIWrapper()
memory = MemorySaver()

agent = create_agent(
    model=model,
    tools =[search.run],
    system_prompt = "you are a agent and can search anything on google",
    checkpointer= memory,
)
##chat_history = []
###Here I uses the chathistory to append the user response and then pass that chat_history to the agent and after that append the AI message
###like this-
# [
#     HumanMessage(content="PM of India"),
#     AIMessage(content="Narendra Modi"),
#     HumanMessage(content="his age?")
# ]

# PM of India → Narendra Modi
#                   ↓
#              "his age?"
#                   ↓
#         Oh, "his" = Narendra Modi
while True:
    query = input("User: " )
    if query.lower() == "quit":
        print("GoodBye")
        break
    ##chat_history.append(HumanMessage(content= query))
    response = agent.invoke(
        {"messages" : [{"role": "user", "content": query}]},
        {"configurable" : {"thread_id" : "yash"}},

        )
    ##response = agent.invoke({"messages" : chat_history})
    #chat_history.append(AIMessage(content=response["messages"][-1].content))  -->> we can use this also but in google search tool there should be other messages also so if we only use the human and AI messages then we can loose the data so that's why we send all the preserve data to chat history like in below line.
    #chat_history = response["messages"]

    print("AI:", response["messages"][-1].content, "\n")