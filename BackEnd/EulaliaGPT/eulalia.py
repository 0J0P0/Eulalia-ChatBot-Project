"""
Module: eulalia.py
Author: JP Zaldivar
Date: April 20, 2024

Description:


Contents:
- get_response: Function to process the message received and return a response.
"""


# TODO
def get_response(messages: list) -> dict:
    """
    # TODO

    Parameters
    ----------
    messages : list
        List of messages received.

    Returns
    -------
    dict
        Response message.
    """

    if messages:
        response_message = f'You said: {messages[-1]}'
    else:
        response_message = 'No message received.'

    response = {'message': response_message}

    return response