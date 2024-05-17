import React, { useRef, useEffect } from 'react';
import eulalia_message_logo from '../../img/eulalia_message_logo.svg';
import user_message_logo from '../../img/user_message_logo.svg';
import { TypingIndicator } from '@chatscope/chat-ui-kit-react';
import '../../styles/chat_conversation.css';

function ChatConversation({ messages, isTyping }) {
  // Ref for scrolling to bottom
  const messagesEndRef = useRef(null);

  // Function to scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Function to format the message content
  const formatMessage = (message) => {
    // Split the message by \n to handle new lines
    const lines = message.split('\n');
    
    // Process each line separately
    return lines.map((line, index) => (
      <React.Fragment key={index}>
        {line.split('<br>').map((part, i) => (
          <React.Fragment key={i}>
            {part}
            {i !== line.split('<br>').length - 1 && <br />}
          </React.Fragment>
        ))}
        {index !== lines.length - 1 && <br />}
      </React.Fragment>
    ));
  };

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
                {formatMessage(message.message)}
              </div>
            ) : (
              <div className='user_message'>
                {formatMessage(message.message)}
              </div>
            )}
          </div>
        </div>
      ))}
      {isTyping && <TypingIndicator content='Eulàlia està escrivint...' />}
      <div ref={messagesEndRef} />
    </div>
  );
}

export default ChatConversation;
