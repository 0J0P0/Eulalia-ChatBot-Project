import React, { useState, useEffect } from 'react';

import '../styles/bot.css';

import Logo from '../components/Logo.js';
import ChatPanel from '../components/chat/ChatPanel.js';
import InitialChat from '../components/chat/InitialChat.js';
import ChatHistory from '../components/chat/ChatHistory.js';
import ChatConversation from '../components/chat/ChatConversation.js';

import new_chat_icon from '../img/new_chat.svg';

function Bot({ newSession, setNewSession }) {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [conversationIds, setConversationIds] = useState([]);

  useEffect(() => {
    
    if (newSession) {
      handleNewChat();
      setNewSession(false);
    } else {
      const storedMessages = localStorage.getItem('chatMessages');
      const storedConversationIds = localStorage.getItem('conversationIds');
      if (storedMessages) {
        setMessages(JSON.parse(storedMessages));
      }
      if (storedConversationIds) {
        setConversationIds(JSON.parse(storedConversationIds));
      }
    }
  }, [newSession, setNewSession]);

  const handleSend = async (message) => {
    const newMessage = {message: message, sender: 'User', conv_title: null};
    const newMessages = [...messages, newMessage];

    localStorage.setItem('chatMessages', JSON.stringify(newMessages));
    setMessages(newMessages);
    setIsTyping(true);

    await processMessageToChatGPT(newMessages);
  };

  async function processMessageToChatGPT(chatMessages) {
    const messages = chatMessages.slice(-50);

    fetch('/api/process_chat_message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ messages })
    })
    .then(response => response.json())
    .then(data => {
      console.log('ChatGPT response:', data.messages);
      const newMessages = data.messages

      localStorage.setItem('chatMessages', JSON.stringify(newMessages));
      setMessages(newMessages);
      setIsTyping(false);
    })
    .catch(error => console.error('Error:', error));
  }

  const handleNewChat = () => {
    setMessages([]);
    localStorage.removeItem('chatMessages');

    // Send request to backend: refresh history bar
    fetch('/api/refresh_history', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
      localStorage.setItem('conversationIds', JSON.stringify(data));
      setConversationIds(data);
    })
    .catch(error => console.error('Error:', error));
  };

  return (
    <div className='bot_page_container'>
      <Logo subtitle='' />
      <div className='chat_container'>
        <div className='left_chat_col'>
          <ChatHistory messages={messages} setMessages={setMessages} conversationIds={conversationIds}/>
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
