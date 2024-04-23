import React from 'react'
import { useState } from 'react'

import '../styles/bot.css'

import Logo from '../components/Logo.js'
import ChatPanel from '../components/chat/ChatPanel.js'
import ChatConversation from '../components/chat/ChatConversation.js'
import InitialChat from '../components/chat/InitialChat.js'
import Footer from '../components/Footer.js'

function Bot() {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = async (message) => {
    const newMessage = { message, sender: 'User' };
    const newMessages = [...messages, newMessage];
    setMessages(newMessages);

    setIsTyping(true);

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
    })
    .catch(error => console.error('Error:', error));
  }

  return (
    <div>
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
      <Footer />
    </div>
  )
}

export default Bot;