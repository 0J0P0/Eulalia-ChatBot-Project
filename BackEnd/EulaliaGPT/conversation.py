import uuid
import psycopg
# from langchain.memory import ChatMessageHistory
from EulaliaGPT.framework_rag_integrated import process_question
from langchain_postgres import PostgresChatMessageHistory


sync_connection = psycopg.connect("postgresql://postgres:password@localhost:5432")
table_name = "chat_history_test"

class Conversation():
    def __init__(self, id: str = None):
        self.id = id if id is not None else str(uuid.uuid4())
        self.memory = PostgresChatMessageHistory(
            table_name,
            self.id,
            sync_connection=sync_connection
        )
    
    def ask_question(self, question):
        
        answer = process_question(question, self.memory, self.id)
        # print("Answer: -------------------------------------")
        # print(answer)

        return answer