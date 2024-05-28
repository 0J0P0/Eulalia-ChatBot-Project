import React from 'react';

function PrevChat({ id, index, messages, setMessages }) {

  const handlePrevChat = () => {
    console.log('Chat', id);

    fetch('/api/get_conversation', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ id })
    })
      .then(response => response.json())
      .then(data => {
        console.log('Raw data:', data);
        console.log('Messages:', data.messages);
        
        const prevChatMessages = data.messages;
        localStorage.setItem('chatMessages', JSON.stringify(data.messages));
        setMessages(prevChatMessages);
        
        console.log('Messages:', messages);
      })
      .catch(error => console.error('Error:', error));
  };

  return (
    <button onClick={handlePrevChat} className='prevChat'>
      Chat {index}
    </button>
  );
}

export default PrevChat;
