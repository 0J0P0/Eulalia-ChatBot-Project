import React from 'react';
import { MessageList, TypingIndicator } from '@chatscope/chat-ui-kit-react';

import eulalia_message_logo from '../../img/eulalia_message_logo.svg';
import user_message_logo from '../../img/user_message_logo.svg';

import '../../styles/chat_conversation.css';


function ChatConversation({ messages, isTyping }) {
  return (
    <MessageList 
      scrollBehavior='smooth' 
      typingIndicator={isTyping ? <TypingIndicator content='Eulàlia is typing' /> : null}
    >
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
    </MessageList>
  )
}

export default ChatConversation;

