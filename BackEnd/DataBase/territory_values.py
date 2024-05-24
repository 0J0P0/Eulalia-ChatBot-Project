import warnings
warnings.filterwarnings("ignore")

import nltk
import re
import os
import ast
import json
import pandas as pd
from fuzzywuzzy import fuzz
from unidecode import unidecode
from nltk.corpus import stopwords


def get_data():
    """
    Extract data from the JSON file.

    Returns
    -------
    dt : DataFrame
        DataFrame containing all the data regarding the DataBase.
    """

    df = pd.read_json('/dades/eulalia/Data/Dades_solr_pro/yol_definicio_indicadors_collection_k8s_20240215.json', lines=True)
    dd = df[df['api_origen']=='estadistiques'].dropna(axis=1, how='all')

    dt = dd[['descripcio.ca', 'id_indicador', 'tags.ca', 'fet.ca', 'indicador.ca', 'tipus_territori.ca', 'unitat.ca', 'unitat_mesura.ca',  'valors_territori', 'llistat_dimensions.ca', 'notes_indicador.ca', 'valors_dimensions.ca']]
    dt['tipus_territori.ca'] = dt['tipus_territori.ca'].astype(str)

    dt['id_indicador'] = dt['id_indicador'].apply(lambda x: 'a' + x if x[0].isdigit() else x)
    return dt


def get_territory_values(dt):
    """
    Extract territorial values from the data.

    Parameters
    ----------
    dt : DataFrame
        DataFrame containing all the data regarding the DataBase.

    Returns
    -------
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
    """

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

    return Municipi, AreaMetropolitana, ComunitatAutonoma, Districte, Barri



dt = get_data()
Municipi, AreaMetropolitana, ComunitatAutonoma, Districte, Barri = get_territory_values(dt)

dict_territory_vals = {'Municipi' : Municipi, 'AreaMetropolitana': AreaMetropolitana, 'ComunitatAutonoma' : ComunitatAutonoma, 'Districte':Districte, 'Barri':Barri}

with open('territory_values.json', 'w', encoding='utf-8') as json_file:
    json.dump(dict_territory_vals, json_file, indent=4, ensure_ascii = False )
