from dotenv import load_dotenv
load_dotenv()

##llm, db, agent, tools, systemprompt

from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
import streamlit as st

db = SQLDatabase.from_uri("sqlite:///my_tasks.db")
db.run("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT CHECK(status IN ('pending', 'in_progress', 'completed')) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

""")

model = llm = ChatGroq(model = "openai/gpt-oss-20b")
toolkit = SQLDatabaseToolkit(db=db, llm= model)
tools = toolkit.get_tools()

system_prompt = """
You are a task management assistant that intreacts with a SQL database contaning a 'tasks' table

TASKS RULES:
1- limit SELECT query to 10  results max with ORDER BY created_at DESC
2- after CREATE/UPDATE/DELETE, confirm withth select query 
3- if the user requests a list of tasks, present the output in a sturctured table formatto ensure clean and organized display in browser

CURD OPERATIONS:
    CREATE: INSERT INTO tasks(title, description, status)
    READ: SELECT * FROM tasks WHERE ... LIMIT 10
    UPDATE: UPDATE tasks SET status=? WHERE id=? OR title=?
    DELETE: DELETE FROM tasks WHERE id=? or title=?

Table schema: id,title, description, status(pending/completed/in_progress), created_at.

"""

@st.cache_resource
def get_agent():
    agent = create_agent(
        model= model,
        tools= tools,
        system_prompt= system_prompt,
        checkpointer= InMemorySaver()
    )
    return agent
agent = get_agent()


st.subheader("🛖 TaskBot- Manage your Tasks")

if "messages" not in st.session_state:
    st.session_state.messages = []
for messages in st.session_state.messages:
    st.chat_message(messages["role"]).markdown(messages["content"])

prompt = st.chat_input("Ask me anything!!")
if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("ai"):
        with st.spinner("Processing...."):
            response = agent.invoke(
                {"messages":[{"role":"user", "content": prompt}]},
                {"configurable":{"thread_id":"yash"}})
            result = response["messages"][-1].content
            st.session_state.messages.append({"role": "ai", "content": result})
            st.markdown(result)

