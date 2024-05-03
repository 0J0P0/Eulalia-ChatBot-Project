"""
Module: eulalia.py

Contents:
- get_response: Function to process the message received and return a response.
"""


def get_response(data: list) -> dict:
    """

    Parameters
    ----------
    data : list
        List of data received.
        conv_title : title of conversation

    Returns
    -------
    dict
        Response message.
    """
    print(data)
    if data:
        if len(data['messages']) == 1:
            data['messages'][0]['conv_title'] = 'Chat1' # placeholder
            # data['messages'][0]['conv_title'] = get_conversation_title(data[0])

        else:
            data['messages'][-1]['conv_title'] = data['messages'][0]['conv_title']
        
        response_message = f'You said: {data['messages'][-1]}'

        response = {'message': response_message}
    else:
        response = {'message': 'No message received.'}

    print(response)

    return response