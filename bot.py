from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate  # Import PromptTemplate
import json

import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')

def generate_response(json_data, query):
    """
    Generate a concise response to a query using a JSON list as context.
    
    Args:
        json_data (list): A JSON list containing the context data.
        query (str): The question to answer.
    
    Returns:
        dict: A JSON object containing the concise response.
    """
    # Convert JSON list to a single string
    formatted_document = [json.dumps(item) for item in json_data]
    
    # Split the document into chunks
    text_splitter = CharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=0
    )
    docs = text_splitter.create_documents(formatted_document)
    
    # Create embeddings
    embeddings = HuggingFaceEmbeddings()
    
    # Create a vector store from the documents
    store = FAISS.from_documents(docs, embeddings)
    
    # Create the LLM (Language Model)
    llm = ChatGroq(
        temperature=0.2,
        model="deepseek-r1-distill-llama-70b",  # Use the specified model
        api_key=GROQ_API_KEY
    )
    
    # Define a custom prompt template for concise answers
    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template="Context: {context}\n\nQuestion: {question}\n\nAnswer: Provide a simple and concise answer to the user's question with proper reasoning and context reference."
    )
    
    # Create the retrieval chain with the custom prompt
    retrieval_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=store.as_retriever(),
        chain_type_kwargs={
            "prompt": prompt_template  # Pass the PromptTemplate object
        }
    )
    
    # Run the chain with the query
    result = retrieval_chain.invoke(query)
    
    # Extract the response and format it as a JSON object
    response = result.get("result", "No response generated.")

    return {"response": response}  # Return the response as a JSON object