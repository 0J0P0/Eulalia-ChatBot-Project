import warnings
warnings.filterwarnings("ignore")

import nltk
import re
import os
import ast
import json
import dotenv
import openai
import chromadb
import pandas as pd
from fuzzywuzzy import fuzz
from unidecode import unidecode
from nltk.corpus import stopwords
from chromadb.utils import embedding_functions

dotenv.load_dotenv()
os.environ["OPENAI_API_KEY"] = str(os.getenv("API_KEY"))
nltk.download('stopwords')


def encode(string):
    """
    Write strings in plain text.

    Parameters
    ----------
    string : str
        Any string value.

    Returns
    -------
    string : str
        String in plain text.
    """
    return re.sub(r'\W+', ' ', unidecode(string).lower()) 


def fuzzy_search_and_modify(word, stop_words_catalan, Barri, Districte, Municipi, ComunitatAutonoma):
    """
    Fuzzy search for the 'territori' values.

    Parameters
    ----------
    word : str
        Any string from a sequence (word from the query).
    stop_words_catalan : List
        List containing all catalan stopwords.
    Municipi : List
        List containing all values corresponding to a Municipality.
    AreaMetropolitana : List
        List containing all values corresponding to a Metropolitan Area.
    ComunitatAutonoma : List 
        List containing all values corresponding to a Autonomous Community.
    Districte : List
        List containing all values corresponding to a District.
    Barri : List
        List containing all values corresponding to a Neighborhood.

    Returns
    -------
    word : str
        Same parameter string or with territorial information added.
    """

    for vector_name, vector in [("barri", Barri), ("districte", Districte), ("municipi", Municipi), ("comunitat autonoma", ComunitatAutonoma)]:
        for term in vector:
            for w in term.split():
                if w not in stop_words_catalan:
                    if fuzz.partial_ratio(word, encode(w)) >= 95:  
                        return f"{vector_name} {word}"
    return word


def modify_query(q, Barri, Districte, Municipi, ComunitatAutonoma):
    """
    Process the query to remove stopwords and write it in plain text.

    Parameters
    ----------
    q : str
        A sequence of strings (query).
    Barri : List
        List containing all values corresponding to a Neighborhood.
    Districte : List
        List containing all values corresponding to a District.
    Municipi : List
        List containing all values corresponding to a Municipality.
    ComunitatAutonoma : List 
        List containing all values corresponding to a Autonomous Community.

    Returns
    -------
    modified_query : str
        A sequence of strings with territorial information added and without stopwords.
    """

    stop_words_catalan = set(stopwords.words('catalan'))
    stop_words_catalan.add('l')

    modified_query = " ".join(fuzzy_search_and_modify(word, stop_words_catalan, Barri, Districte, Municipi, ComunitatAutonoma) for word in encode(q).split() if word not in stop_words_catalan)

    return modified_query


def query_collection(collection, query, max_results, dataframe):
    """
    Find the top 'max_results' most similar tables given a query.

    Parameters
    ----------
    collection : ChromaDB collection
        Embedding and metadata space.
    query : str
        A sequence of strings.
    max_results : int
        Maximum number of returned tables.
    dataframe : DataFrame
        DtaFrame containing the embeddings of the tables in the DataBase

    Returns
    -------
    df : DataFrame
        DataFrame where each row is a table whose content is similar to a given query, in descending order.
    """

    results = collection.query(query_texts=query, n_results=max_results, include=['distances']) 
    df = pd.DataFrame({
                'id':results['ids'][0], 
                'score':results['distances'][0],
                'content': dataframe[dataframe.ID.isin(results['ids'][0])]['Descripcio'],
                })
    return df
    

def relevant_docs(q, max_results=10):
    """
    Find the top 'max_results' most similar tables given a query.

    Parameters
    ----------
    q : str
        A sequence of strings.
    max_results : int
        Maximum number of returned tables.

    Returns
    -------
    indicators : List
        List containing the 'max_results' most similar tables of the DataBase.
    """

    with open('territory_values.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    Municipi, Districte, Barri, ComunitatAutonoma =  data['Municipi'], data['Districte'], data['Barri'], data['ComunitatAutonoma']

    df = pd.read_csv('./embedded_descr_large_weight.csv', sep = ';')

    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.environ["OPENAI_API_KEY"],
                model_name="text-embedding-3-large"
            )
    
    client = chromadb.Client()

    if "new_collection" in [c.name for c in client.list_collections()]:
        collection = client.get_or_create_collection(name = "new_collection", embedding_function=openai_ef, metadata = {"hnsw:space": "cosine"})
    else:
        ids = df['ID'].tolist()
        df['embd'] = df['embeddings'].apply(ast.literal_eval)
        list_of_embd = df['embd'].tolist()
        collection = client.get_or_create_collection(name = "new_collection", embedding_function=openai_ef, metadata = {"hnsw:space": "cosine"})
        collection.add(ids=ids, embeddings = list_of_embd)


    modified_query = modify_query(q, Barri, Districte, Municipi, ComunitatAutonoma)

    query_result = query_collection(
        collection = collection,
        query = modified_query,
        max_results = max_results,
        dataframe = df
    )

    # Modify the names of the tables to transform its ids into a explanatory sentence
    json_file = "./diccionario.json"

    with open(json_file, "r") as file:
        dictionary_read = json.load(file)
    indicators = [dictionary_read[i] for i in list(query_result['id'])]

    return indicators
    