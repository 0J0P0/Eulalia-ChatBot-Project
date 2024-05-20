import React from 'react'

import PrevChat from './PrevChat';

import '../../styles/chathistory.css'

function ChatHistory({ messages, setMessages, conversationIds }) {
  
  return (
    <div className='chathistory_container'>
      <h1>Converses</h1>
      {conversationIds.map(id => (
        <PrevChat key={id} id={id} messages={messages} setMessages={setMessages} />
      ))}
    </div>
  );
}

export default ChatHistory;
