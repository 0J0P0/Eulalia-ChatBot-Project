"""
Module: eulalia.py
Author: JP Zaldivar
Date: April 20, 2024

Description:


Contents:
- get_response: Function to process the message received and return a response.
"""


# TODO
def get_response(data: list) -> dict:
    """
    # TODO

    Parameters
    ----------
    data : list
        List of data received.

    Returns
    -------
    dict
        Response message.
    """

    if data:
        if len(data['messages']) == 1:
            conv = 'Chat1'  # placeholder
            # conv = get_conversation_title(data[0])
        else:
            conv = data['messages'][-1]['conversation_title']
        
        # TODO DGAY
        response_message = f'You said: {data['messages'][-1]}'

        response = {'message': response_message, 'conversation_title': conv}
    else:
        response_message = 'No message received.'


    return response