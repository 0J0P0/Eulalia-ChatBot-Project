import React, { useState, useEffect } from 'react';

import '../styles/bot.css';

import Logo from '../components/Logo.js';
import ChatPanel from '../components/chat/ChatPanel.js';
import InitialChat from '../components/chat/InitialChat.js';
import ChatHistory from '../components/chat/ChatHistory.js';
import ChatConversation from '../components/chat/ChatConversation.js';

import new_chat_icon from '../img/new_chat.svg';

function Bot() {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    const storedMessages = localStorage.getItem('chatMessages');
    if (storedMessages) {
      setMessages(JSON.parse(storedMessages));
    }
  }, []);

  const handleSend = async (message) => {
    // const messages_len = messages.length
    const newMessage = {message: message, sender: 'User', conv_title: null};

    // if (messages_len > 0) {
    //   // set the conv_title of all the messages the one from the last message
    //   const newMessages = messages.map((msg, index) => {
    //     if (index === messages_len - 1) {
    //       return {...msg, conv_title: message};
    //     } else {
    //       return msg;
    //     }
    //   });
    // }

    const newMessages = [...messages, newMessage];
    localStorage.setItem('chatMessages', JSON.stringify(newMessages));
    
    setMessages(newMessages);
    setIsTyping(true);

    await processMessageToChatGPT(newMessages);
  };

  async function processMessageToChatGPT(chatMessages) {
    // Get the last 50 messages text
    const messages = chatMessages.slice(-50);
    // Send the messages to the backend
    fetch('/api/process_chat_message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ messages })
    })
    .then(response => response.json())
    .then(data => {
      // Add the response to the chat
      console.log(data)
      console.log(data.messages)

      // const newMessage = { message: data.message, sender: 'Eulàlia', conv_title: data.conv_title};
      const newMessages = data.messages
      setMessages(newMessages);
      setIsTyping(false);

      // Store updated messages in localStorage
      localStorage.setItem('chatMessages', JSON.stringify(newMessages));
    })
    .catch(error => console.error('Error:', error));
  }

  // const handleNewChat = () => {
  //   setMessages([]);
  //   localStorage.removeItem('chatMessages');
  // };

  const handleNewChat = () => {
    // Reset chat history
    setMessages([]);
    localStorage.removeItem('chatMessages');

    // // Send request to backend: refresh history bar
    // fetch('/api/refresh_history', {
    //     method: 'POST',
    //     headers: {
    //         'Content-Type': 'application/json'
    //     },
    //     body: JSON.stringify({})
    // })
    // .then(response => response.json())
    // .then(data => {
    //     // Handle response from backend if needed
    // })
    // .catch(error => console.error('Error:', error));
};

  return (
    <div>
      <Logo subtitle='' />
      <div className='chat_container'>
        <div className='left_chat_col'>
          <ChatHistory />
          <button onClick={handleNewChat} className='new_chat_button'>
            <img
              src={new_chat_icon}
              alt='New chat' />
          </button>
        </div>
        <div className='right_chat_col'>
          {messages.length === 0 ? (
            <InitialChat />
          ) : (
            <ChatConversation messages={messages} isTyping={isTyping} />
          )}
          <ChatPanel handleSend={handleSend} />
        </div>
      </div>
    </div>
  )
}

export default Bot;
