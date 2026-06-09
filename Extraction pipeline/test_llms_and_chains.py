from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
#from langchain_ollama import ChatOllama
from langchain_community.chat_models import ChatOllama
import textwrap
import systematic_prompts as sp
import formatting_wordfile as fm
import os


os.environ["OPENAI_API_KEY"] = "Your API KEY"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
#chat_LLM = ChatOpenAI(model_name='gpt-4o', temperature=0.5, model_kwargs={"seed": 42})
chat_LLM = ChatOllama(model="llama3.1", temperature=0.5)

def wrap_text_preserve_newlines(text, width=150):
    # Split the input text into lines based on newline characters
    lines = text.split('\n')
    # Wrap each line individually
    wrapped_lines = [textwrap.fill(line, width=width) for line in lines]
    # Join the wrapped lines back together using newline characters
    wrapped_text = '\n'.join(wrapped_lines)
    return wrapped_text

def process_llm_response(llm_response):
    if type(llm_response) == dict:
        print('entering if scope of LLM response')
        return wrap_text_preserve_newlines(llm_response['result'])
    else:
        print('entering else scope of LLM response')
        return wrap_text_preserve_newlines(llm_response)
    



def extract_evidence(retriever, filename="default"):


    chain = RetrievalQA.from_chain_type (llm=chat_LLM,
                        chain_type="stuff",
                        chain_type_kwargs={"prompt":sp.pico},
                        retriever=retriever,
                        return_source_documents=False)
        


    pico_evidence=process_llm_response(chain(sp.query))

    outcome_chain = RetrievalQA.from_chain_type (llm=chat_LLM,#llm_for_table,
                                  chain_type="stuff",
                                  chain_type_kwargs={"prompt":sp.outcomes},
                                  retriever=retriever,
                                  return_source_documents=False)
    llm_response = outcome_chain(sp.outcome_query)
    json_stats=process_llm_response(llm_response)

    fm.write_into_word_file(pico_evidence=pico_evidence, json_stats=json_stats, fileName=f"{filename}_extraction_LLama3.1")

    return pico_evidence
        



