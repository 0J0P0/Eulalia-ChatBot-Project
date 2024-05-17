"""
Module: connection.py
Author: JP Zaldivar & Noa Mediavilla
Date: April 20, 2024

Description:
This module contains the function to create a connection to the database.

Contents:
- create_connection: Function to create a connection to the database.
"""


import os
import psycopg
import psycopg2


def create_connection(database, user, pyscopg2=True):
    """
    Create a connection to the database.

    Parameters
    ----------
    database : str
        Name of the database to connect to.
    user : str
        User name to connect to the database.
    pyscopg2 : bool
        Flag to use psycopg2 instead of psycopg.

    Returns
    -------
    conn : psycopg2.extensions.connection
        Connection to the database.
    cur : psycopg2.extensions.cursor
        Cursor to the database.
    """
   
    if pyscopg2:
        conn = psycopg2.connect(database=database,
                                    user=user,
                                    password=str(os.getenv("DATABASE_PASSWORD")),
                                    host=os.getenv("DATABASE_HOST"),
                                    port=os.getenv("DATABASE_PORT"))
    else:
        conn = psycopg.connect("postgresql://postgres:password@localhost:5432/usersDB")

    cur = conn.cursor()

    return conn, cur