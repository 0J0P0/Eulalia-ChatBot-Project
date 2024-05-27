"""
Module: server.py
Author: JP Zaldivar & Noa Mediavilla
Date: April 20, 2024

Description:
This module contains the server that will receive messages from the frontend and return a response.

Contents:
- login: Function to authenticate user based on provided credentials.
- store_contact_messages: Function to store the contact messages received in a postgreSQL database.
- process_chat_message: Function to process the message received and return a response.
"""


import os
import sys
import dotenv
dotenv.load_dotenv()
os.environ['PYTHONPATH'] = str(os.getenv("PROJECT_PATH"))  # Absolute path to the BackEnd folder
sys.path.append('./')

from flask_cors import CORS
from flask import Flask, request, jsonify

from EulaliaGPT.conversation import get_response, format_message
from DataBase.connection import create_connection


app = Flask(__name__)
CORS(app)


@app.route('/login', methods=['POST'])
def login():
    """
    Authenticate user based on provided credentials.
    
    Returns:
    --------
    dict
        Response message with authentication status.
    """

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    try:
        conn, cur = create_connection(database=os.getenv('DATABASE_CHAT'),
                                      user=os.getenv('DATABASE_CHAT_USER'))
        
        cur.execute(f"SELECT * FROM {(os.getenv('LOGIN_TABLE'))} WHERE username = %s AND password = %s;", (username, password))

        user = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if user:
            return jsonify({"success": True, "message": "Authentication successful"})
        else:
            return jsonify({"success": False, "message": "Authentication failed"})
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return jsonify({"success": False, "message": "Authentication failed"}), 500


@app.route('/api/store_contact_messages', methods=['POST'])
def store_contact_messages() -> dict:
    """
    Store the contact messages received in a postgreSQL database.

    Returns
    -------
    dict
        Response message with log information.
    """

    data = request.get_json()

    try:
        conn, cur = create_connection()

        cur.execute(
            f'''INSERT INTO {os.getenv("DATABASE_CONTACT_TABLE")} (user_id, user_name, user_contact_message) VALUES (%s, %s, %s);''',
            (data['email'], data['name'], data['message'])
        )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"log": "Message stored successfully"})
    except Exception as e:
        print(f"Error storing contact message: {e}")
        return jsonify({"log": "Error storing message"})


@app.route('/api/process_chat_message', methods=['POST'])
def process_chat_message() -> dict:
    """
    Process the message received and return a response.

    Returns
    -------
    dict
        Dictionary with the response message and previous conversation messages.
    """
    
    data = request.get_json()
    
    response = get_response(data)
    
    return jsonify(response)


@app.route('/api/refresh_history', methods=['POST'])
def refresh_history():
    """
    Refresh history
    Returns list of distinct session IDs
    """

    try:
        conn, cur = create_connection(database=os.getenv('DATABASE_CHAT'),
                                      user=os.getenv('DATABASE_CHAT_USER'))

        cur.execute(
            f'''
            SELECT session_id
            FROM (
                SELECT session_id, message_id
                FROM message_references
                ORDER BY message_id DESC
            ) subquery
            GROUP BY session_id
            ORDER BY MAX(message_id);
            '''
        )

        session_ids = [row[0] for row in cur.fetchall()]
        session_ids.reverse()
        # total_sessions = len(session_ids)
        # session_ids = [total_sessions - i for i in range(total_sessions)]

        conn.commit()
        cur.close()
        conn.close()

        return jsonify(session_ids)
    
    except Exception as e:
        print(f"Error getting last conversation: {e}")
        return jsonify({"log": "Error getting last conversation"})


@app.route('/api/get_conversation', methods=['POST'])
def get_conversation():
    """
    Retrieve messages for a given conversation ID.

    Parameters
    ----------
    conversation_id : str
        The ID of the conversation to retrieve.

    Returns
    -------
    dict
        Dictionary containing the messages for the conversation.
    """

    data = request.get_json()
    
    try:
        conn, cur = create_connection(database=os.getenv('DATABASE_CHAT'),
                                        user=os.getenv('DATABASE_CHAT_USER'))


        cur.execute(
            f"SELECT tbl.session_id, tbl.message, tbl.relevant_tables, tbl.sql_query, tbl.sender FROM message_references AS tbl WHERE tbl.session_id = %s ORDER BY tbl.message_id ASC;", (data['id'],)
        )
        
        
        messages = []
        senders = []
        conv_titles = []
        rows = cur.fetchall()
        for row in rows:
            conv_titles.append(row[0])
            senders.append(row[4])
            message = row[1]
            relevant_tables = row[2]
            sql_query = row[3]
            messages.append(format_message(message, relevant_tables, sql_query))
            
        
        formated_messages = []
        for i, message in enumerate(messages):
            formated_message = {'message': message,
                                'sender': senders[i],
                                'conv_title': conv_titles[i]}
            
            formated_messages.append(formated_message)
        
        
                
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"messages": formated_messages})
        
    except Exception as e:
        print(f"Error retrieving conversation: {e}")
        return jsonify({"error": "Error retrieving conversation"}), 500


if __name__ == '__main__':
    app.run(debug=True)
