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
    if data:
        print('Data recieved in backend:            ', data)
        if len(data['messages']) == 1:
            data['messages'][0]['conv_title'] = 'Chat1'
            print('First user message', data['messages'][0]['conv_title'])
        else:
            data['messages'][-1]['conv_title'] = data['messages'][0]['conv_title']
            print('user message', data['messages'][-1]['conv_title'])
        
        response_message = f'You said: {data['messages'][-1]['message']}'
        response = {'message': response_message, 'sender': 'Eulàlia', 'conv_title': data['messages'][-1]['conv_title']}

    else:
        response = {'message': 'No message received.'}

    data['messages'].append(response)

    return data