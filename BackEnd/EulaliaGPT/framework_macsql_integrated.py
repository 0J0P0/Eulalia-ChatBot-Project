"""
Module: framework_rag_integrated.py
Author: Oriol Mayne, Silvia Fabregas & Xavier Pacheco
Date: May 15, 2024

Description:
This module contains the RAG model integration to process the questions received and return a response.

Contents:
- process_question: Function to process the question received and return a response.
"""

import os
import json
import dotenv
import subprocess
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain_postgres import PostgresChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages

from DataBase.connection import create_connection


############################################################################################################
#                                             Pre-Processing                                               #
############################################################################################################


dotenv.load_dotenv()
os.environ["OPENAI_API_KEY"] = str(os.getenv("API_KEY"))
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)


def macsql_tool(question,
                tool_script: str = "./EulaliaGPT/MacSqlUtils/run_automated.sh",
                input_file: str = "./EulaliaGPT/MacSqlUtils/input_automated.json",
                output_file: str = "./EulaliaGPT/MacSqlUtils/output_eulaliadb_automated.json"):
    """
    ...

    Parameters
    ----------
    question : str
        Pregunta de l'usuari.
    tool_script : str
        Bash script to execute the MAC-SQL tool.
    input_file : str
        Input file for the MAC-SQL tool.
    output_file : str
        Output file for the MAC-SQL tool.

    Returns
    -------
    results : list
        Result of the query.
    sql_query : str
        SQL query generated.
    dades : dict
        Data returned by the tool.
    relevant_tables : list
        Relevant tables to the query.
    """
    
    _, cur = create_connection(database=os.getenv("DATABASE_INFO"), user=(os.getenv("DATABASE_INFO_USER")))

    # Write the input data to the input file
    with open(input_file, 'w') as f:
        dades = [{"db_id": "dbeulalia", "question": question, "evidence": "","SQL": ""}]
        json.dump(dades, f)

    # Create the output file
    with open(output_file, "w") as f:
        f.truncate(0)

    # Run the MAC-SQL tool
    subprocess.run(["bash", tool_script], check = True)

    f = open(output_file)
    dades = json.load(f)
    sql_query = dades["pred"].replace("`","")

    # Returns all the tables relevant to the query
    relevant_tables = list(dades["extracted_schema"].keys())
    
    try:
        cur.execute(sql_query)
        results = cur.fetchall()
    except: 
        results = "No query was generated and therefore no results have been obtained."

    f.close()

    return results, sql_query, dades, relevant_tables


# Funció en format tool pel model
macsql_tool_agent = Tool.from_function(
    func=macsql_tool,
    name="macsql_tool",
    description="Function to generate an run an SQL query on relevant tables"
)


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
            MUST NOT invent a query. You MUST send the original question of the query, as it is.
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
            """,
            # Imperative: Write an additional line, indicating a brief title for the question of the user. It must be
            # written in the following format: "Title: <title>".
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


tools = [macsql_tool_agent]
llm_with_tools = llm.bind_tools(tools)


# Creation of the agent by linking the prompt with the tools-enhanced LLM. An agent is a tool that is able to make decisions about the actions to take with the tools at its disposal, as specified in the prompt
agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"],
        ),
        "chat_history": lambda x: x["chat_history"],
    }
    | prompt
    | llm_with_tools
    | OpenAIToolsAgentOutputParser()
)


############################################################################################################
#                                               Processing                                                 #
############################################################################################################


def process_question(question: str, memory: PostgresChatMessageHistory, id: str) -> dict:
    """
    Processes the question and returns the answer.

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
    dict
        answer: str
            Answer to the question.
        relevant_tables: list
            Relevant tables to the query.
        sql_query: str
            SQL query generated.
    """
    agent_executor = AgentExecutor(agent=agent, tools = tools, verbose=True, return_intermediate_steps=True)
    
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

    output_file = "./EulaliaGPT/MacSqlUtils/output_eulaliadb_automated.json"
    f = open(output_file)
    dades = json.load(f)
    sql_query = dades["pred"].replace("`","")
    relevant_tables = list(dades["chosen_db_schem_dict"].keys())
    f.close()

    print("RELEVANT TABLES: ")
    print(relevant_tables)
    print()
    print("SQL QUERY: ")
    print(sql_query)
    
    
    output = {}
    if not agent_output["intermediate_steps"]:
        output["answer"] = agent_output["output"]
        output["relevant_tables"] = []
        output["sql_query"] = ""
    else:
        output["answer"] = agent_output["output"]
        output["relevant_tables"] = relevant_tables
        output["sql_query"] = sql_query


    return output