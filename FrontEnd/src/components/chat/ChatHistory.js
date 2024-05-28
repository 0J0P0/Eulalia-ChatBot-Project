import React from 'react';
import PrevChat from './PrevChat';

import '../../styles/chathistory.css';

function ChatHistory({ messages, setMessages, conversationIds }) {
  return (
    <div className='chathistory_container'>
      <div className='chathistory_header'>
        <h3>Converses</h3>
      </div>
      <div className='chathistory_content'>
        {conversationIds.map((id, index) => (
          <PrevChat
            key={id}
            id={id}
            index={conversationIds.length - index}
            messages={messages}
            setMessages={setMessages}
          />
        ))}
      </div>
    </div>
  );
}

export default ChatHistory;
