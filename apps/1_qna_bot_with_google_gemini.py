# import warnings
# warnings.filterwarnings("ignore")
from dotenv import load_dotenv
load_dotenv() ##load environment variables from .env file

from langchain.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st

llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")

st.title("🤖 AskBuddy -  AI QnA Bot")
st.markdown("My QnA bot is powered by Google Gemini 3.6 and LangChain. You can ask any question and get an answer from the AI model.")
query = st.chat_input("Ask a question:")
### Here we are using the session state to store the messages. The session state is a dictionary that is used to store the state of the app. We are using the session state to store the messages so that we can display the chat history when the user asks a question. We are also using the session state to store the role of the message (user or ai) so that we can display the messages in the correct order.
if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    st.chat_message(role).markdown(content)
if query:
    st.session_state.messages.append({"role":"user",  "content" : query})
    
    st.chat_message("User:").markdown(query)
    ####here we are creating a chat history from the messages stored in the session state. We are creating a list of HumanMessage and AIMessage objects from the messages stored in the session state. This chat history is then passed to the llm.invoke method to get the response from the AI model.
    chat_history = []
    for msg in st.session_state.messages:
        if msg["role"] =="user":
            chat_history.append(HumanMessage(content=msg["content"]))

        else:
                chat_history.append(AIMessage(content=msg["content"]))


        
    response = llm.invoke(chat_history)
    st.chat_message("AI:").markdown(response.content[0]["text"])
    st.session_state.messages.append({"role":"ai",  "content" : response.content[0]["text"]})
    

    ###below code is for testing the bot in command line interface. You can uncomment it to test the bot in CLI.
# while True:
#     query = input("User:")
#     if not query.strip():
#         print("Please type a question or type 'exit' to quit.")
#         continue
#     if query.lower() in ["exit", "quit", "bye"]:
#         print("Exiting the chat. Goodbye!") 
#         break
#     response = llm.invoke(query)
#     print("AI:",response.content[0]["text"], "\n")

