import React from 'react'
import PrevChat from './PrevChat';

import '../../styles/chathistory.css'

function ChatHistory({ messages, setMessages, conversationIds }) {
  
  return (
    <div className='chathistory_container'>
      <div className='chathistory_header'>
        <h3>Converses</h3>
      </div>
      <div className='chathistory_content'>
        {conversationIds.map(id => (
          <PrevChat key={id} id={id} messages={messages} setMessages={setMessages} />
        ))}
      </div>
    </div>
  );
}

export default ChatHistory;
