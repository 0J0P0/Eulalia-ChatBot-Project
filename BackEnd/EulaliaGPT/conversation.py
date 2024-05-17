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

    def __init__(self, id: str = str(uuid.uuid4()), model: str = "MACSQL"):
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

    # response_message = """
    # Hi ha un total de 1.625.137 arbres a Barcelona l'any 2017.
    
    # Les 10 taules rellevants trobades pel MACSQL són:
    # 1. puntuacio_mitjana_d_avaluacio_d_espais_verds
    # 2. valoracio_de_la_gestio_municipal_per_edat
    # 3. dades_de_les_eleccions_al_consell_municipal_de_barcelona
    # 4. percepcio_del_propi_barri
    # 5. valoracio_de_la_gestio_municipal
    # 6. percepcio_del_propi_barri_per_edat
    # 7. valoracio_de_la_gestio_municipal_per_sexe
    # 8. resultats_eleccions_municipals_26_maig_2019_candidatura
    # 9. resultats_eleccions_municipals_28_maig_2023_candidatura
    # 10. percentatge_participacio_eleccions_consell_municipal_franja_hor 
    
    # Si necessites més informació sobre algun d'aquests temes, no dubtis a preguntar-me.
    # """

    response = {'message': response_message,
                'sender': 'Eulàlia',
                'conv_title': data['messages'][-1]['conv_title']}

    data['messages'].append(response)

    return data