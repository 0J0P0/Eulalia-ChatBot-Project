"""
Module: eulalia.py

Contents:
- get_response: Function to process the message received and return a response.
"""


from EulaliaGPT.conversation import Conversation


def get_response(data: list):
    """

    Parameters
    ----------
    data : list
        List of data received.

    Returns
    -------
    dict
        Response message.
    """

    conv_id = data['messages'][0]['conv_title']

    if conv_id is None:
        conversation = Conversation()
        data['messages'][0]['conv_title'] = conversation.id
    else:
        conversation = Conversation(conv_id)
        data['messages'][-1]['conv_title'] = conv_id
    
    response_message = conversation.ask_question(data['messages'][-1]['message'])

    response = {'message': response_message,
                'sender': 'Eulàlia',
                'conv_title': data['messages'][-1]['conv_title']}

    data['messages'].append(response)

    return data