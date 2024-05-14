from langchain.agents import create_sql_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent
from langchain.llms.openai import OpenAI
from langchain.sql_database import SQLDatabase
import os
import pandas as pd
import subprocess
import psycopg2
from langchain_postgres import PostgresChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.agents import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad.openai_tools import ( format_to_openai_tool_messages,)

from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents.agent_types import AgentType
import chromadb
from chromadb.utils import embedding_functions
from fuzzywuzzy import fuzz
import time
from langchain.tools import Tool
from DataBase.chroma import relevant_docs
import json

# Definim la API_KEY del model com a variable d'entorn
os.environ["OPENAI_API_KEY"] = "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"

# Eina de langchain per tal de crear un chat (versió OPENAI)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

def extract_output(output):
    """Extracts the output from the json string.
    If an action was taken, returns the relevant tables.
    Otherwise returns the answer to the query."""
    if "actions" in output[0]:
        
        string_data = output[1]["messages"][0].content
        start_index = string_data.find('[')
        end_index = string_data.rfind(']')
        vector = string_data[start_index + 1:end_index].split(', ')
    

        # Stripping the double quotes from each element
        vector = [element.strip('"') for element in vector]
        vector = [string.lower() for string in vector]

        return vector
    else:
        return output[0]["output"]


def macsql_tool(user_question):
    """
    Aquesta funció s'encarrega de cridar a MAC-SQL (que ja integra
    ChromaDB) per tal de generar la query. Quan aquesta és generada,
    la executa. Retorna 3 objectes: la execució de la query, la
    query inicial i la seqüència generada. 
    """
    # Connectem a la BD
    connection = psycopg2.connect(
            user="bot",
            password="password",
            host="localhost",
            port="5432",
            database="dbeulalia"
        )
    
    # Escrivim en el fitxer d'input les dades
    with open("./EulaliaGPT/macsql_files/input_automated.json", 'w') as a:
        dades = [{"db_id": "dbeulalia", "question": user_question, "evidence": "","SQL": ""}]
        json.dump(dades, a)

    # Escrivim en el fitxer d'input les dades
    # if os.path.exists("./EulaliaGPT/macsql_files/output_eulaliadb_automated.json"):
    #     os.remove("./EulaliaGPT/macsql_files/output_eulaliadb_automated.json")


    with open("./EulaliaGPT/macsql_files/output_eulaliadb_automated.json", "w") as json_file:
        json_file.truncate(0)

    subprocess.run(["bash", "./EulaliaGPT/macsql_files/run_automated.sh"], check = True)

    # Objecte que permet executar les consultes
    cursor = connection.cursor()

    # Opening JSON file
    f = open('./EulaliaGPT/macsql_files/output_eulaliadb_automated.json')

    # returns JSON object as a dictionary
    dades = json.load(f)
    sql_query = dades["pred"].replace("`","") 


    # Executem la consulta SQL
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
    except: 
        results = "No query was generated and therefore no results have been obtained."

    return results, sql_query, dades

# Funció en format tool pel model
macsql_tool_agent = Tool.from_function(
    func=macsql_tool,
    name="macsql_tool",
    description="Function to generate an run an SQL query on relevant tables"
)

tools = [macsql_tool_agent]

# Missatge d'entrada que es passa a l'agent
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a very powerful assistant working for the Ajuntament de Barcelona.
            You do not know everything, so you use tools in order to correctly fetch
            the information needed to give an adequate response to the query given by
            the user. 

            The MACSQL tool is a powerful tool that uses an LLM pipeline to retrieve the
            necessary information from the database, select the relevant tables needed to
            answer the question posed by the user. The tool returns the information found
            in the database for a given question, as well as other information returned 
            by the tool that will help you understand the process. If you invoke the 
            MACSQL tool you MUST give it the query performed by the user.

            The MACSQL tool works best when the question is in catalan. You should translate
            the question to catalan before sending it to the tool. You should still create 
            the answer in the original language of the question.

            DO NOT, under any circumstance, send an invented query to the MAC-SQL tool. You 
            MUST NOT invent a query. You MUST send the original question of the query, as is.
            NO CHANGES.
 
            The MACSQL tool should only be invoked whenever the question done by the user is
            related to the information contained in the database. The database contains
            information related to the city of Barcelona, and covers the following topics: 
            demographics, immigration, public policy, popular opinion, elections... as well
            as other topics. 

            If the query done by the user is not related to the city, you should answer
            normally, without fetching the tool.

            You must respond truthfully, taking into account the information from the database
            whenever it is provided. If the MAC-SQL tool has been called, you should use the
            information it provides to explain the steps that have been taken. By that, I mean
            that you should explain the steps that the tool has taken and, furthermore, explain
            what your reasoning has been to use the data returned by the tool to answer the question.

            Additionally, write a short title for the convesation with the user.
            """,
        ),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

llm_with_tools = llm.bind_tools(tools)

# Creem l'agent enllaçant el prompt amb el LLM millorat amb tools. Un agent és
# una eina que és capaç de prendre decisions sobre les accions que fer amb les
# tools que té a l'abast, tal i com se li especifica en el prompt
agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"],
        ),
    }
    | prompt
    | llm_with_tools
    | OpenAIToolsAgentOutputParser()
)

def process_question(question: str, memory: PostgresChatMessageHistory, id: str) -> str:
    """Processes the question and returns the answer.

    Parameters
    ----------
    question : str
        Question to process.
    memory : PostgresChatMessageHistory
        Chat message history.
    id : str
        Session id.

    Returns
    -------
    str
        Answer to the question.
    """

    agent_executor = AgentExecutor(agent=agent, tools = tools, verbose=True)
    
    agent_with_chat_history = RunnableWithMessageHistory(
        agent_executor,
        lambda session_id: memory,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    agent_output = agent_with_chat_history.invoke(
        {"input": question},
        config={"configurable": {"session_id": id}}
    )

    return agent_output["output"]