##To Build this Bot we need few things
## LLM
## Tool- google search tool
## Agent 
## memory
## Streaming
## Web Interface

from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent 
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from langchain_community.utilities import GoogleSerperAPIWrapper
import streamlit as st

llm = ChatGroq(model = "openai/gpt-oss-20b", streaming= True)
search = GoogleSerperAPIWrapper()


if("memory" not in st.session_state):
    st.session_state.memory = MemorySaver()
    st.session_state.history = []

agent = create_agent(
    model = llm,
    tools= [search.run],
    system_prompt= "you are a Qna chat bot. You can answer the questions using google",
    checkpointer= st.session_state.memory,
)
##Building Web Interface
st.subheader("QNA BOT WITH GROQ")

for message in st.session_state.history:
    role = message["role"]
    content = message["content"]
    st.chat_message(role).markdown(content)

query = st.chat_input("Ask Anything ?")
if query:
    st.chat_message("user").markdown(query)
    st.session_state.history.append({"role": "user", "content": query})
    response = agent.stream(

    {"messages": [{"role": "user", "content": query}]},
    {"configurable": {"thread_id": "yash"}},
    stream_mode= "messages"

    )

    ###here we created the Ai container and used streaming to get the real time typing view if you do not need the container just remove he AI cotainer and streaming and use the below commented  code.
    ai_container = st.chat_message("ai")
    with ai_container:
        space = st.empty()  ##here space refer to AI container

        message = ""

        for chunk in response:
            message = message + chunk[0].content
            space.write(message)
        st.session_state.history.append({"role": "ai", "content": message})
    # answer = response["messages"][-1].content
    # st.chat_message("ai").markdown(answer)
    


