"""
Module: framework_rag_integrated.py
Author: David Gallardo, Xavi Pacheco & Pablo Gete
Date: May 15, 2024

Description:
This module contains the RAG model integration to process the questions received and return a response.

Contents:
- process_question: Function to process the question received and return a response.
"""


import os
import dotenv
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain_postgres import PostgresChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages


from DataBase.chroma import relevant_docs
from DataBase.connection import create_connection


############################################################################################################
#                                             Pre-Processing                                               #
############################################################################################################


dotenv.load_dotenv()
os.environ["OPENAI_API_KEY"] = str(os.getenv("API_KEY"))
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are very powerful assistant, but don't know everything.
            You can use tools to help you answer queries.

            The similarity search tool utilizes similarity search to find 
            information about the query within a dataset. 
            The assistant should only invoke the similarity search tool when
            the query is related to information contained in the dataset.
            
            The information contained in the dataset is about Barcelona and its demographics; 
            Always remember to use the tool when the query is related to this information.

            After the answer you should provide a message saying "These are the most relevant tables for your query:" in the language of the conversation.
            """,
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

conn, _ = create_connection(database=os.getenv("DATABASE_INFO"), user=(os.getenv("DATABASE_INFO_USER")))

sim_search_tool = Tool.from_function(
    func=relevant_docs,
    name="SimilaritySearchTool",
    description="Function to find relevant documents"
)

tools = [sim_search_tool]
llm_with_tools = llm.bind_tools(tools)

agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"]
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


def process_question(question: str, memory: PostgresChatMessageHistory, id: str) -> str:
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
    str
        Answer to the question.
    """
    
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)
    
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
    # print("=============================")
    # for value in agent_output["intermediate_steps"][0]:
    #     print(value)
    #     print()
    # print("=============================")   

    if len(agent_output["intermediate_steps"]) == 0:
        output = {"answer": agent_output["output"], 
                "relevant_tables": "", 
                "sql_query": ""}
    else:
        output = {"answer": agent_output["output"], 
                "relevant_tables": agent_output["intermediate_steps"][0][1], 
                "sql_query": ""}
    print(output)
    return output

