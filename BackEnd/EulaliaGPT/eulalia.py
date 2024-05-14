"""
Module: eulalia.py
Author: JP Zaldivar, Noa Mediavilla & David Gallardo
Date: April 20, 2024

Description:
This module contains the function to process the message received and return a response.

Contents:
- Conversation: Class to create or continue a conversation with the user.
- get_response: Function to process the message received and return a response.
"""


import uuid
import psycopg
# from langchain.memory import ChatMessageHistory
from EulaliaGPT.framework_rag_integrated import process_question as process_question_normal
# from carpeta_macsql import process_question as process_question_macsql
from langchain_postgres import PostgresChatMessageHistory


#TODO
sync_connection = psycopg.connect("postgresql://postgres:password@localhost:5432")
table_name = "chat_history_test"

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
            sync_connection=sync_connection
        )

    def generate_answer(self, question):
        """
        Process the question received and return the answer.
        
        Parameters
        ----------
        question : str
            Question to process.
            
        Returns
        -------
        str
            Answer to the question.
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

    response = {'message': response_message,
                'sender': 'Eulàlia',
                'conv_title': data['messages'][-1]['conv_title']}

    data['messages'].append(response)

    return data