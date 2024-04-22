"""
Module: connection.py
Author: JP Zaldivar
Date: April 20, 2024

Description:
This module contains the function to create a connection to the database.

Contents:
- create_connection: Function to create a connection to the database.
"""


import os
import psycopg2 
from dotenv import load_dotenv


def create_connection():
    """
    Create a connection to the database.

    Returns
    -------
    conn : psycopg2.extensions.connection
        Connection to the database.
    cur : psycopg2.extensions.cursor
        Cursor to the database.
    """
   
    conn = psycopg2.connect(user='postgres',
                                host='147.83.46.71',
                                password='password',
                                database='usersDB', 
                                port=5990)
    cur = conn.cursor()

    return conn, cur