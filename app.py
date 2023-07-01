import streamlit as st
import os
import sys
#from dotenv import load_dotenv
from langchain.document_loaders import SeleniumURLLoader, PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS, Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQAWithSourcesChain, ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain import OpenAI
import pickle
import faiss

# Load environment variables if necessary
# load_dotenv()

# Set the page title
st.set_page_config(page_title="Question Answering App")

# Define the app layout
st.title("Question Answering App")
input_type = st.radio("Select Input Type", ("Upload Files", "Enter URLs"))
#folder_path = st.text_input("Enter the folder path to save uploaded files", value="docs")
uploaded_files = st.file_uploader("Upload documents", type=["pdf", "docx", "doc", "txt"], accept_multiple_files=True)
user_urls = st.text_input("Enter URLs (separated by commas)")
user_question = st.text_input("Ask a question")

def main():
    if st.button("Answer"):
        if input_type == "Upload Files":
            if not uploaded_files:
                st.write("Please upload at least one document.")
                return
            
            # Create the folder to save uploaded files if it doesn't exist
            if not os.path.exists("new"):
                os.makedirs('new')
            
            documents = []
            for uploaded_file in uploaded_files:
                # Save the uploaded file to the specified folder
                file_path = os.path.join(uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Load the uploaded document based on its file type
                if file_path.endswith(".pdf"):
                    loader = PyPDFLoader(file_path)
                    documents.extend(loader.load())
                elif file_path.endswith('.docx') or file_path.endswith('.doc'):
                    loader = Docx2txtLoader(file_path)
                    documents.extend(loader.load())
                elif file_path.endswith('.txt'):
                    loader = TextLoader(file_path)
                    documents.extend(loader.load())

        elif input_type == "Enter URLs":
            if not user_urls:
                st.write("Please enter at least one URL.")
                return
            
            urls = [url.strip() for url in user_urls.split(",")]

            loader = SeleniumURLLoader(urls=urls)
            data = loader.load()

            text_splitter = CharacterTextSplitter(separator='\n',
                                                  chunk_size=2550,
                                                  chunk_overlap=200)
            documents = text_splitter.split_documents(data)
        
        os.environ["OPENAI_API_KEY"] = "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"

        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_documents(documents, embeddings)
        with open("faiss_store_openai.pkl", "rb") as f:
            VectorStore = pickle.load(f)

        llm = OpenAI(temperature=0.5, max_tokens=50)
        chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=vectorstore.as_retriever())

        answer = chain({"question": user_question}, return_only_outputs=True)

        # Display the question and answer
        st.write(f"Question: {user_question}")
        st.write(f"Answer: {answer['answer']}")

# Run the Streamlit app
if __name__ == '__main__':
    main()
