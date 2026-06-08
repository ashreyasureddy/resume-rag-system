from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import streamlit as st

st.set_page_config(
    page_title="Resume RAG System",
    page_icon="🤖",
    layout="centered"
)

# Custom Styling
st.markdown("""
<style>

body {
    background-color: #f0f8ff;
}

.stApp {
    background: linear-gradient(to right, #74ebd5, #ACB6E5);
}

h1 {
    color: darkblue;
    text-align: center;
}

.stTextInput > div > div > input {
    background-color: #ffffff;
    border-radius: 10px;
    border: 2px solid #4CAF50;
}

.stButton button {
    background-color: #4CAF50;
    color: white;
    border-radius: 10px;
    height: 40px;
    width: 150px;
}

</style>
""", unsafe_allow_html=True)

st.title("📄 Resume Question Answering System")
st.write("Ask questions about the resume using AI 🤖")

from dotenv import load_dotenv
import os
load_dotenv()

key = os.getenv('GEMINI_API_KEY')

@st.cache_resource
def load_rag_chain():
    loader = PyPDFDirectoryLoader("data")
    doc = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documents = splitter.split_documents(doc)
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = Chroma(embedding_function=embedding)
    vector_store.add_documents(documents)
    retriever = vector_store.as_retriever()
    prompt = ChatPromptTemplate.from_template("""Based on user question give the correct answer based only on context
                                     question:{question}
                                     context:{context}""")
    llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash', google_api_key=key, temperature=0)
    
    # your original line — just moved inside and returned
    return ({'context': retriever, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser())

rag_chain = load_rag_chain()  # this replaces the original rag_chain line

query = st.text_input("Enter your question:")

if st.button("Predict"):

    response = rag_chain.invoke(query)

    st.success("Answer:")
    st.write(response)

