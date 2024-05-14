import nltk
import re
import re
import os
import json
import openai
import chromadb
import pandas as pd
from fuzzywuzzy import fuzz
from unidecode import unidecode
from nltk.corpus import stopwords
from chromadb.utils import embedding_functions

os.environ["OPENAI_API_KEY"]="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"
nltk.download('stopwords')

def get_data():
    df = pd.read_json('/home/user/eulalia/Data/Dades_solr_pro/yol_definicio_indicadors_collection_k8s_20240215.json', lines=True)
    dd = df[df['api_origen']=='estadistiques'].dropna(axis=1, how='all')

    dt = dd[['descripcio.ca', 'id_indicador', 'tags.ca', 'fet.ca', 'indicador.ca', 'tipus_territori.ca', 'unitat.ca', 'unitat_mesura.ca',  'valors_territori', 'llistat_dimensions.ca', 'notes_indicador.ca', 'valors_dimensions.ca']]
    dt['tipus_territori.ca'] = dt['tipus_territori.ca'].astype(str)

    dt['id_indicador'] = dt['id_indicador'].apply(lambda x: 'a' + x if x[0].isdigit() else x)

    print('get_data')
    return dt


def get_territory_values(dt):

    Municipi = dt[dt['tipus_territori.ca'] == "['Municipi']"]['valors_territori'].value_counts().keys().tolist()[0]
    AreaMetropolitana = dt[dt['tipus_territori.ca'] == "['Àrea Metropolitana']"]['valors_territori'].value_counts().keys().tolist()[0]

    # Comunitat Autònoma
    ComunitatAutonoma = dt[dt['tipus_territori.ca'] == "['Comunitat Autònoma', 'Municipi']"]['valors_territori'].value_counts().keys().tolist()[0]
    ComunitatAutonoma.remove('Barcelona')

    # Districte
    dt_districte = dt[dt['tipus_territori.ca'] == "['Municipi', 'Districte']"].copy()
    Districte = dt_districte['valors_territori'].value_counts().keys().tolist()[0]
    Districte.remove('Barcelona')

    # Barri
    e = dt[dt['tipus_territori.ca'] == "['Municipi', 'Districte', 'Barri']"]['valors_territori'].value_counts().keys().copy()
    count, lists = [], []
    lengths = set([len(row) for row in e.tolist()])
    barri_lengths = {element: True for element in lengths}

    for i in range(len(e)):
        l = len(e.tolist()[i])
        if l in lengths and barri_lengths[l]:
            barri_lengths[l] = False
            lists.append(e.tolist()[i])
        count.append(l)
    
    new = []
    for i in range(len(lists)):
        lists[i].remove('Barcelona')
        for dist in Districte:
            if dist in lists[i]:
                lists[i].remove(dist)
        new.append(lists[i])
    
    flat_list = [string for sublist in new for string in sublist]
    Barri = list(set(flat_list))

    print('get_territory_values')
    return Municipi, AreaMetropolitana, ComunitatAutonoma, Districte, Barri


def encode(string):
    return re.sub(r'\W+', ' ', unidecode(string).lower()) 

def clean_text(text, chars_to_remove):
    cleaned_text = ''.join([c for c in text if c not in chars_to_remove])
    cleaned_text = re.sub(r'\bnan\b', '', cleaned_text, flags=re.IGNORECASE)
    return cleaned_text


def generar_text(row):
    descripcio_ca = row['descripcio.ca'] 
    indicador_ca = row['indicador.ca'] 
    fet_ca = row['fet.ca']  
    unitat_mesura_ca = row['unitat_mesura.ca']  
    tipus_territori_ca = row['tipus_territori.ca']  
    llistat_dimensions_ca = row['llistat_dimensions.ca']  
    tags_ca = row['tags.ca'] 

    text = f"La taula conté informació de {descripcio_ca} amb l'indicador {indicador_ca}. Es mostra el fet {fet_ca} mesurat en {unitat_mesura_ca},"
    text_2 = f" en funció d'un conjunt de dimensions: {tipus_territori_ca}, {llistat_dimensions_ca}. La informació està relacionada amb les temàtiques: {tags_ca}."
    chars_to_remove = "!@#^&*[]'"
    text_2 = clean_text(text_2, chars_to_remove)

    return text+text_2 #encode(text+text_2)


def fuzzy_search_and_modify(word, stop_words_catalan, Barri, Districte, Municipi, ComunitatAutonoma):
    for vector_name, vector in [("barri", Barri), ("districte", Districte), ("municipi", Municipi), ("comunitat autonoma", ComunitatAutonoma)]:
        for term in vector:
            for w in term.split():
                if w not in stop_words_catalan:
                    if fuzz.partial_ratio(word, encode(w)) >= 95:  
                        return f"{vector_name} {word}"
    return word


def modify_query(q, Barri, Districte, Municipi, ComunitatAutonoma):

    stop_words_catalan = set(stopwords.words('catalan'))
    stop_words_catalan.add('l')

    modified_query = " ".join(fuzzy_search_and_modify(word, stop_words_catalan, Barri, Districte, Municipi, ComunitatAutonoma) for word in encode(q).split() if word not in stop_words_catalan)

    return modified_query


def query_collection(collection, query, max_results, dataframe):
    results = collection.query(query_texts=query, n_results=max_results, include=['distances']) 
    df = pd.DataFrame({
                'id':results['ids'][0], 
                'score':results['distances'][0],
                'content': dataframe[dataframe.ID.isin(results['ids'][0])]['Descripcio'],
                })
    
    return df


def create_collection(df_descr):

    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.environ["OPENAI_API_KEY"],
                model_name="text-embedding-3-small"
            )
    
    client = chromadb.Client()
    collection = client.get_or_create_collection(name = "descripcions_taules", embedding_function=openai_ef, metadata = {"hnsw:space": "cosine"})


    desc = df_descr['Descripcio'].tolist()
    ids = df_descr['ID'].tolist()
    collection.add(documents=desc, ids=ids)

    return collection
    

def relevant_docs(q):

    dt = get_data()
    
    Municipi, AreaMetropolitana, ComunitatAutonoma, Districte, Barri = get_territory_values(dt)

    # Create a new DataFrame with ID and text columns
    df_descr = pd.DataFrame({
        'ID': dt['id_indicador'], ##################################################################################################################################################
        #'nom_taula': dt['indicador.ca'],
        'Descripcio': dt.apply(generar_text, axis=1)
    })

    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.environ["OPENAI_API_KEY"],
                model_name="text-embedding-3-small"
            )
    
    client = chromadb.Client()

    collection = client.get_or_create_collection(name = "test", embedding_function=openai_ef, metadata = {"hnsw:space": "cosine"})

    desc = df_descr['Descripcio'].tolist()
    ids = df_descr['ID'].tolist()
    collection.add(documents=desc, ids=ids)

    modified_query = modify_query(q, Barri, Districte, Municipi, ComunitatAutonoma)

    query_result = query_collection(
        collection=collection,
        query=modified_query,
        max_results=10,
        dataframe=df_descr
    )

    ruta_archivo_json = "./DataBase/diccionario.json"

    # Leer el archivo JSON
    with open(ruta_archivo_json, "r") as archivo:
        diccionario_leido = json.load(archivo)

    l_id = list(query_result['id'])
    #print(l_id)
    indicadors = []
    for i in l_id:
        indicadors.append(diccionario_leido[i])

    return indicadors
    