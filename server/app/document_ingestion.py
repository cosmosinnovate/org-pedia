# Document ingestion module
# This module is responsible for ingesting documents into the system
# It provides a function to ingest a document and store it in the system
# It also provides a function to retrieve a document from the system
# It uses the document storage module to store and retrieve documents

# from langchain_community.document_loaders import UnstructuredPDFLoader
import os
from langchain_community.document_loaders import PyPDFLoader, UnstructuredPDFLoader


doc_path = "./data/Fair Credit Reporting Acts summary of rights.pdf"
model = "llama3.2"


def load_pdf(file_path):
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found at path: {file_path}")
        print(f"Current working directory: {os.getcwd()}")
        return None
    
    try:
        loader = PyPDFLoader(file_path=file_path)
        data = loader.load()
        print("Done loading...")
        return data
    except Exception as e:
        print(f"Error loading PDF: {str(e)}")
        return None

if doc_path:
    data = load_pdf(doc_path)
    if data:
        # PyPDFLoader returns a list of documents, one per page
        content = data[0].page_content
        print("First page content:")
        print(content[:1000])
else:
    print("Please provide a PDF file path")