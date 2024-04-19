import React from 'react'
import { useState } from 'react'

import '../styles/bot.css'

import Logo from '../components/Logo.js'
import Footer from '../components/footer.js'
import ChatPanel from '../components/chat/ChatPanel.js'
import ChatConversation from '../components/chat/ChatConversation.js'
import InitialChat from '../components/chat/InitialChat.js'

function Bot() {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);

  // Handle the sending a message
  const handleSend = async (message) => {
    const newMessage = {
      message,
    };

    const newMessages = [...messages, newMessage];
    
    setMessages(newMessages);

    await processMessageToChatGPT(newMessages);
  };

  async function processMessageToChatGPT(chatMessages) {

    const messages = chatMessages.map((message) => message.message);

    fetch('/api/process_message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ messages })
    })
    .then(response => response.json())
    .then(data => {
      const newMessage = {
        message: data.message,
      };

      const newMessages = [...chatMessages, newMessage];
      setMessages(newMessages);
    })
    .catch(error => console.error('Error:', error));
  }

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
    </div>
  )
}

export default Bot;