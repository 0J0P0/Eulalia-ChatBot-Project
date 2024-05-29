import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { coy } from 'react-syntax-highlighter/dist/esm/styles/prism';
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
    return (
      <ReactMarkdown
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');

            const customStyle = {
              fontSize: '1.3vw',
              borderRadius: '2vw',
              backgroundColor: '#F4F4F4',
            };

            return !inline && match ? (
              <SyntaxHighlighter
                style={coy} customStyle={customStyle}
                language={match[1]}
                PreTag="div"
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              <code className={className} {...props}>
                {children}
              </code>
            );
          }
        }}
      >
        {content}
      </ReactMarkdown>
    );
  };

  const formatEulaliaMessage = (message, isExpanded, index, sender) => {
    const splitText = "Aquestes són les taules relacionades més importants que he trobat:";
    const parts = message.split(new RegExp(`(${splitText})`));
    const answer = parts[0];
    const restOfMessage = parts.slice(1).join('');

    if (isExpanded) {
      return (
        <React.Fragment>
          <ReactMarkdown>{answer}</ReactMarkdown>
          {formatMessage(restOfMessage)}
          {sender === 'Eulàlia' && <button className="message_button" onClick={() => toggleMessageExpansion(index)}>Veure menys</button>}
        </React.Fragment>
      );
    } else {
      return (
        <React.Fragment>
          <ReactMarkdown>{answer}</ReactMarkdown>
          {restOfMessage && sender === 'Eulàlia' && <button className="message_button" onClick={() => toggleMessageExpansion(index)}>Veure més</button>}
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
                {formatMessage(message.message)}
              </div>
            )}
          </div>
        </div>
      ))}
      {isTyping && <TypingIndicator content='Eulàlia està escrivint...' className="blinking" />}
      <div ref={messagesEndRef} />
    </div>
  );
}

export default ChatConversation;
