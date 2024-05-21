import React, { useState, useRef, useEffect } from 'react';

import { TypingIndicator } from '@chatscope/chat-ui-kit-react';

import '../../styles/chat_conversation.css';

import user_message_logo from '../../img/user_message_logo.svg';
import eulalia_message_logo from '../../img/eulalia_message_logo.svg';


function ChatConversation({ messages, isTyping }) {
  const [expandedMessages, setExpandedMessages] = useState({});
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const toggleMessageExpansion = (index) => {
    setExpandedMessages((prev) => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const formatMessage = (content) => {
    return content.split('\n').map((line, lineIndex) => {
      // Check if the line starts with code snippet indicator
      if (line.trim().startsWith('```sql')) {
        const code = line.split('```sql')[1] || '';
        return (
          <div className="code-snippet" key={lineIndex}>
            {code.trim()}
          </div>
        );
      } else {
        return (
          <React.Fragment key={lineIndex}>
            {line}
            <br />
          </React.Fragment>
        );
      }
    });
  };

  const formatEulaliaMessage = (message, isExpanded, index, sender) => {
    const [answer, ...rest] = message.split('\n\n');
    const restOfMessage = rest.join('\n\n');

    if (isExpanded) {
      return (
        <React.Fragment>
          {answer}
          <br /><br />
          {formatMessage(restOfMessage)}
          {sender === 'Eulàlia' && <button className="message_button" onClick={() => toggleMessageExpansion(index)}>Veure menys</button>}
        </React.Fragment>
      );
    } else {
      return (
        <React.Fragment>
          {answer}
          {rest.length > 0 && sender === 'Eulàlia' && <button className="message_button" onClick={() => toggleMessageExpansion(index)}>Veure més</button>}
        </React.Fragment>
      );
    }
  };

  return (
    <div className='message_list_container'>
      {messages.map((message, index) => (
        <div key={index} className='message_container'>
          <img
            src={message.sender === 'Eulàlia' ? eulalia_message_logo : user_message_logo}
            alt='Message Logo'
            className='message_logo' />
          <div className='message_container_row'>
            {message.sender === 'Eulàlia' ? (
              <div className='eulalia_message'>
                {formatEulaliaMessage(message.message, expandedMessages[index], index, message.sender)}
              </div>
            ) : (
              <div className='user_message'>
                {formatMessage(message.message, expandedMessages[index], index, message.sender)}
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
