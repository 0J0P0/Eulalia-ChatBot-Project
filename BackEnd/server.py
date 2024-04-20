"""
Module: server.py
Author: JP Zaldivar
Date: April 20, 2024

Description:
This module contains the server that will receive messages from the frontend and return a response.

Contents:
- store_message: Function to store the message received in a postgreSQL database.
- process_message: Function to process the message received and return a response.
"""


import os
import psycopg2 
from flask_cors import CORS
from dotenv import load_dotenv
from flask import Flask, request, jsonify


from EulaliaGPT.eulalia import get_response


app = Flask(__name__)
CORS(app)  # Allow CORS for all routes



def store_message(data, response):
    """
    Store the message received in a postgreSQL database.

    Parameters
    ----------
    data : dict
        Data received.
    """
    # Connect to the database
    try:
        conn = psycopg2.connect(database=os.getenv("DATABASE_URL"),
                                user=os.getenv("DATABASE_USER"),
                                password=os.getenv("DATABASE_PASSWORD"),
                                host=os.getenv("DATABASE_HOST"),
                                port=os.getenv("DATABASE_PORT"))
        # Create a cursor
        cur = conn.cursor()

        # Insert the message into the table
        user_message = data['messages'][-1]
        chat_message = response['message']
        cur.execute( 
            '''INSERT INTO messages (user_id, user_message, chat_message) VALUES (%s, %s, %s);''',
            ('admin', user_message, chat_message))
        
        # Commit the changes
        conn.commit() 

        # Close the cursor and connection
        cur.close() 
        conn.close() 
    except Exception as e:
        print(f"Error storing message: {e}")


@app.route('/api/process_message', methods=['POST'])
def process_message() -> dict:
    """
    Process the message received and return a response.

    Returns
    -------
    dict
        Response message.
    """

    data = request.get_json()

    
    response = get_response(data['messages'])
    store_message(data, response)

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
