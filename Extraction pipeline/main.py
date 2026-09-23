
import test_loading as ts
import test_preprocessing as pre
import test_llms_and_chains as llms
import os

os.environ["MKL_SERVICE_FORCE_INTEL"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# Credentials must be supplied through OPENAI_API_KEY in the environment.

def load_vectorize_and_store_into_VDB(filepath, filename):
    data = ts.extract_pdf_structured(filepath)
    pre.chunk_vectorize_and_store_from_data(data,filename)

def load_from_VDB(filename):
    retriever=pre.load_vector_store(filename)
    return retriever

def decider(filename="write your file name",pdf_path="no need if just loading",store=False, load=False , store_and_load=False):

    if store:
        load_vectorize_and_store_into_VDB(pdf_path,filename)
    elif load:
        retrieve = load_from_VDB(filename)
        return retrieve
    elif store_and_load:
        load_vectorize_and_store_into_VDB(pdf_path,filename)
        retrieve = load_from_VDB(filename)
        return retrieve
    else:
        print("Please choose True for any of the following: store or load or store_and_load")


if __name__ == "__main__":
    
    
    pdf_path = "inputs/tanner.pdf"  # Replace with your file path  ""
    filename ="tanner-2025"

    ret=decider(filename=filename,pdf_path=pdf_path,store_and_load=True, load=False)

    ans=llms.extract_evidence(ret,filename)
    print("<------------------------------------------ extracted evidence ------------------------------------------>")
    print(ans)

        
    
    '''    ret=pre.load_vector_store("cooper_index_new_withoutmeta")
        ret.search_kwargs["k"] = 20
        result=ret.get_relevant_documents("what is the population in this study?")

        for x in result:
            print("---------------------------------------------------------------------------")
            print(x)

        result=ret.get_relevant_documents("what is the population in this study")
        for x in result:
            print("---------------------------------------------------------------------------------")
            print(x)
'''

       
    





    #text, meta=pre.chunk_and_vectorize_from_data(data)
    #ts.write_to_word(data)
