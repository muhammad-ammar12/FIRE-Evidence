
from pdf2image import convert_from_path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
import math
import openai
import re
import pickle



def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.replace('\x00', '')  # Remove NULL bytes
    text = re.sub(r'[\x01-\x08\x0B-\x0C\x0E-\x1F]', '', text)  # Remove control characters
    return text.strip()

def chunk_and_vectorize_from_data(data, store=False):
    
    page_texts = []
    page_metadata = []

    # Loop through the structured data by page
    for page_num, items in data.items():
        page_content = ""

        # Extract and clean text and tables for each page
        for item in items:
            if item['type'] == 'text':  # Process only text items
                text = clean_text(item['content'])
                if text:
                    page_content += text + "\n"  # Combine text blocks within the page
            elif item['type'] == 'table':  # Process tables
                table_content = "\n".join(["\t".join([str(cell) if cell is not None else "" for cell in row]) for row in item['content']])

                page_content += "\n" + table_content + "\n"  # Append tables to page content

        if page_content.strip():
            page_texts.append(page_content)  # Treat the entire page as one chunk
            #page_metadata.append({"page_num": page_num, "content": page_content})  # Add metadata (e.g., page number and content)

    #return page_texts,page_metadata

    # Vectorize using OpenAI embeddings
    openai_embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    db_openEmbedd = FAISS.from_texts(page_texts, openai_embeddings)

    # Store page-level metadata as part of the FAISS index
    #db_openEmbedd.add_metadata(page_metadata)

    # Optionally, store the FAISS index
    if store:
        return db_openEmbedd
    else:
        k_value = math.ceil(len(page_texts) / 1)  # Dynamic K based on chunk count 1.08
        print("k_value for retrieval:", k_value)
        open_retriever = db_openEmbedd.as_retriever(search_kwargs={"k": k_value})
        return open_retriever


#  Chunk, Vectorize, and Store FAISS Index 
def chunk_vectorize_and_store_from_data(data, file_name='default_index_Output'):
    
    # Generate embeddings and store FAISS index
    KB = chunk_and_vectorize_from_data(data=data, store=True)
    file_name=f"{file_name}_index"
    KB.save_local(file_name)
    print(f"FAISS index saved to {file_name}")


#  Load Vector Store (FAISS index) from disk 
def load_vector_store(file_name, openai_embeddings=None):

    file_name=f"{file_name}_index"
    
    if openai_embeddings is None:
        openai_embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    KB = FAISS.load_local(file_name, openai_embeddings, allow_dangerous_deserialization=True)

    # Retrieve number of chunks
    chunks = KB.index.ntotal
    print(f"Number of Chunks in VDB: {chunks}")

    # Set search parameters dynamically
    k_value = math.ceil(chunks / 1)  # Adjust K value based on chunks 1.08, 2.4
    print("k_value for retrieval:", k_value)

    open_retriever = KB.as_retriever(search_kwargs={"k": k_value})
    return open_retriever
