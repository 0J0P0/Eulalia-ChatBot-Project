import React from 'react';

import eulalia_message_logo from '../../img/eulalia_message_logo.svg';
import user_message_logo from '../../img/user_message_logo.svg';

import { TypingIndicator } from '@chatscope/chat-ui-kit-react';

import '../../styles/chat_conversation.css';


function ChatConversation({ messages, isTyping }) {
  // Ref for scrolling to bottom
  const messagesEndRef = React.useRef(null);

  // Function to scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className='message_list_container'>
      {messages.map((message, index) => (
        <div key={index} className='message_container'>
          <img
            src={message.sender === 'Eulàlia' ? eulalia_message_logo : user_message_logo}
            alt='Message Logo'
            className='message_logo' />
          <div>
            {message.sender === 'Eulàlia' ? (
              <div className='eulalia_message'>
                {message.message}
              </div>
            ) : (
              <div className='user_message'>
                {message.message}
              </div>
            )}
          </div>
        </div>
      ))}
      {isTyping && <TypingIndicator content='Eulàlia is typing' />}
      <div ref={messagesEndRef} /> {/* Ref for scrolling to bottom */}
    </div>
  )
}

export default ChatConversation;

