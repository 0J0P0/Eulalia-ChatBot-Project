"""
Module: conversation.py
Author: JP Zaldivar, Noa Mediavilla & David Gallardo
Date: April 20, 2024

Description:
This module contains the function to process the message received and return a response.

Contents:
- Conversation: Class to create or continue a conversation with the user.
- get_response: Function to process the message received and return a response.
"""


import os
import uuid
from DataBase.connection import create_connection
from langchain_postgres import PostgresChatMessageHistory
from EulaliaGPT.framework_rag_integrated import process_question as process_question_normal
from EulaliaGPT.framework_macsql_integrated import process_question as process_question_macsql


############################################################################################################
#                                         Connection to DataBase                                           #
############################################################################################################


conn, _ = create_connection(os.getenv("DATABASE_CHAT"), os.getenv("DATABASE_CHAT_USER"), pyscopg2=False)
table_name = str(os.getenv("DATABASE_CHAT_TABLE"))
PostgresChatMessageHistory.create_tables(conn, table_name)


############################################################################################################
#                                           Conversation Class                                             #
############################################################################################################


class Conversation():
    """
    Class to create or continue a conversation with the user.

    Attributes:
    -----------
    id : str
        Unique identifier for the conversation.
    model : str
        Model to use for processing the questions.
    memory : ChatMessageHistory
        Memory of the conversation.
    
    Methods:
    --------
    generate_answer(question: str) -> str
        Process the question received and return the answer.

    Parameters:
    -----------
    id : str
        Unique identifier for the conversation.
    model : str
        Model to use for processing the questions.

    Returns:
    --------
    Conversation
        Object to create or continue a conversation with the user.
    """

    def __init__(self, id: str = str(uuid.uuid4()), model: str = "NORMAL"):
        self.id = id
        self.model = model
        self.memory = PostgresChatMessageHistory(
            table_name,
            self.id,
            sync_connection=conn
        )

    def generate_answer(self, question):
        """
        Process the question received and return the answer.
        """

        if self.model == "MACSQL":
            answer = process_question_macsql(question, self.memory, self.id)
        elif self.model == "NORMAL":
            answer = process_question_normal(question, self.memory, self.id)

        print(answer)
        
        return answer


def get_response(data: dict):
    """
    Create or continue a conversation with the user. Process the message received and return a response.

    Parameters
    ----------
    data : dict
        Data containing the messages of the conversation.

    Returns
    -------
    dict
        Data containing the messages of the conversation with the response message.
    """

    conv_id = data['messages'][0]['conv_title']

    if conv_id is None:
        conversation = Conversation()
        data['messages'][0]['conv_title'] = conversation.id
    else:
        conversation = Conversation(conv_id)
        data['messages'][-1]['conv_title'] = conv_id
    
    response_message = conversation.generate_answer(data['messages'][-1]['message'])

    formated_message = response_message['answer'] + "\n"
    for idx, tbl in enumerate(response_message['relevant_tables']):
        formated_message += f"\n{idx+1}: {tbl}"
    formated_message += "\n\n```sql" + response_message['sql_query'].replace("\n", " ")
    
    # formated_message = "L'Ajuntament de Barcelona té un total de 37 seguidors a la seva compte de Twitter. Aquesta informació es basa en la suma dels seguidors dels comptes de Twitter relacionats amb la mobilitat de l'Ajuntament.\n\n1: poblacio\n2: persones_abonades_instal_lacions_esportives_municipals\n3: domicilis_per_nombre_de_persones\n4: nombre_de_domicilis\n5: ocupacio_mitjana_dels_domicilis\n6: nombre_de_persones_treballadores_de_l_ajuntament_per_ens\n7: persones_usuaries_instal_lacions_esportives_municipals\n8: persones_emigrants\n9: domicilis_pel_nombre_de_persones_de_18_a_64_anys\n10: poblacio_empadronada_sola_al_domicili\n\n```sqlSELECT valor FROM nombre_de_seguidors_al_compte_de_bcn_mobilitat_de_twitter ORDER BY data_inici DESC LIMIT 1"

    response = {'message': formated_message,
                'sender': 'Eulàlia',
                'conv_title': data['messages'][-1]['conv_title']}

    data['messages'].append(response)

    return data