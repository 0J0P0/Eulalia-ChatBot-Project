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

    answer = response_message['answer']
    query = response_message['sql_query']
    relevant_tables = response_message['relevant_tables']

    # Formatted message based on new requirements
    formated_message = answer
    
    if relevant_tables:
        formated_message += "\n\nAquestes són les taules relacionades més importants que he trobat:"
        for idx, tbl in enumerate(relevant_tables):
            formated_message += f"\n{idx + 1}: {tbl}"
    
    if query:
        formated_message += "\n\nAquesta és la consulta SQL que he utilitzat per trobar la informació proporcionada:"
        formated_message += f"\n\n```sql\n{query}\n```"

    response = {
        'message': formated_message,
        'sender': 'Eulàlia',
        'conv_title': data['messages'][-1]['conv_title']
    }

    data['messages'].append(response)

    return data