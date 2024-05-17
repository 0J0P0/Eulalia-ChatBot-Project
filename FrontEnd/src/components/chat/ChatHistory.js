// ChatHistory.js

import React from 'react'
import { useState } from 'react';
import '../../styles/chathistory.css'



function ChatHistory({ conversationIds }) {

  const [selectedChatId, setSelectedChatId] = useState(null);

  function handlePrevChat(id) {
    setSelectedChatId(id);
    console.log(id)
  }
  
  function PrevChat({ id }) {
    return (   
      <button onClick={handlePrevChat} className='prevChat'>
        Chat {id}
      </button> 
    );
  }
  
  return (
    <div className='chathistory_container'>
      <p className="chathistory_title">Converses</p>
      {conversationIds.map(id => (
        <PrevChat key={id} id={id} />
      ))}
    </div>
  );
}

export default ChatHistory;
