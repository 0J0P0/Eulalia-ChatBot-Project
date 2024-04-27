import React, { useState, useEffect } from 'react';

import '../styles/bot.css';

import Logo from '../components/Logo.js';
import Footer from '../components/Footer.js';
import ChatPanel from '../components/chat/ChatPanel.js';
import InitialChat from '../components/chat/InitialChat.js';
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
    const newMessage = { message, sender: 'User' };
    const newMessages = [...messages, newMessage];
    setMessages(newMessages);

    setIsTyping(true);

    // Store messages in localStorage
    localStorage.setItem('chatMessages', JSON.stringify(newMessages));

    await processMessageToChatGPT(newMessages);
  };

  async function processMessageToChatGPT(chatMessages) {
    // Get the last 50 messages text
    const messages = chatMessages.slice(-50).map(message => message.message);
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
      const newMessage = { message: data.message, sender: 'Eulàlia' };
      const newMessages = [...chatMessages, newMessage];
      setMessages(newMessages);
      setIsTyping(false);

      // Store updated messages in localStorage
      localStorage.setItem('chatMessages', JSON.stringify(newMessages));
    })
    .catch(error => console.error('Error:', error));
  }

  const handleNewChat = () => {
    setMessages([]);
    localStorage.removeItem('chatMessages');
  };

  return (
    <div>
      <Logo subtitle='' />
      <div className='chat_container'>
        {messages.length === 0 ? (
          <InitialChat />
        ) : (
          <ChatConversation messages={messages} isTyping={isTyping} />
        )}
        <ChatPanel handleSend={handleSend} />
      </div>
      <button onClick={handleNewChat} className='new_chat_button'>
        <img
          src={new_chat_icon}
          alt='New chat' />
      </button>
      <Footer />
    </div>
  )
}

export default Bot;
