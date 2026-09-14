from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader, PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import InMemoryVectorStore
from langchain.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
import streamlit as st



### data in st session
if "agent" not in st.session_state:
    st.session_state.agent = None

if "document_uploaded" not in st.session_state:
    st.session_state.document_uploaded = False

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "messages" not in st.session_state:
    st.session_state.messages = []

def process_document(path):

    ###Load the document
    loader = PyPDFDirectoryLoader(path)
    docs = loader.load()

    ###Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size= 1000, chunk_overlap= 200)
    docs = splitter.split_documents(docs)

    ###Embiddings and Vector DB
    embiddings = GoogleGenerativeAIEmbeddings(model= "gemini-embedding-2-preview")
    vector_db = InMemoryVectorStore.from_documents(
        documents= docs,
        embedding= embiddings
    )

    ###Crete agent using groq
    llm = ChatGroq(model = "openai/gpt-oss-20b", streaming= True)

    @tool
    def retriver_context(query:str):
        """
            This Tool can help to retrive the relevant data from the knowledge base
        """
        print("tool called:", query)
        docs = vector_db.similarity_search(query=query, k=4)

        context = ""

        for doc in docs:
            context = doc.page_content + "\n\n"
        return context


    System_Prompt = """
        You are an helpful agent that answer questions using retrived context,
        My knowledge base consist of the details from the uploaded document.
        Always use the retriver_tool for questions requiring the external knowledge.
        And Always give the response in a organize way and in clean structure 

    """

    agent = create_agent(
        model = llm,
        tools= [retriver_context],
        system_prompt= System_Prompt,
        checkpointer= InMemorySaver()
    )
    st.session_state.agent = agent
    st.session_state.document_uploaded = True

###upload UI
if not st.session_state.document_uploaded:
    uploaded = st.file_uploader(label="Select PDF Files", type="pdf", accept_multiple_files=True)
    if uploaded:
        with st.spinner("Processing..."):
            path = "./doc_files/"
            for file in uploaded:
                with open( path + file.name, "wb") as f:
                    f.write(file.getvalue())

            process_document(path)
            st.rerun() ### in this our whole UI will not rerun ony the variables of you can say the data will be reloaded based on the updated data


###Chat UI
if st.session_state.document_uploaded and st.session_state.agent:
    for message in st.session_state.messages:
        role = message.get("role")
        content = message.get("content")
        st.chat_message(role).markdown(content)

    query = st.chat_input("Ask anything related to uploaded documents...")
    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        st.chat_message("user").markdown(query)
        with st.spinner("Processing...."):
            response = st.session_state.agent.invoke(
                {"messages": [{"role": "user", "content": query}]},
                {"configurable": {"thread_id": "yash"}},
            )

        answer = response["messages"][-1].content
        st.session_state.messages.append({"role": "ai", "content": answer})
        st.chat_message("ai").markdown(answer)



# while True:
#     query = input("User: ")
#     if query.lower() == "quit":
#         break

#     response = agent .invoke(

#     {"messages": [{"role": "user", "content": query}]},
#     {"configurable": {"thread_id": "yash"}},

#     )
#     result = response["messages"][-1].content
#     print("AI: ", result)
