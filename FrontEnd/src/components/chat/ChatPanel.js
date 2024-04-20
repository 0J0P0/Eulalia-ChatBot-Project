import React, { useRef, useState, useEffect } from 'react';

import '../../styles/chat_panel.css';


function ChatPanel({ handleSend }) {
  const [input, setInput] = useState('');
  // const promptBarRef = useRef(null);

  const handleChange = (event) => {
    setInput(event.target.value);
  };
  
  const handleSubmit = (event) => {
    event.preventDefault();
    if (input.trim() !== '') {
      handleSend(input);
      setInput('');
    }
  };

  // const scrollToBottom = () => {
  //   promptBarRef.current?.scrollIntoView({ behavior: "smooth" });
  // };

  // useEffect(() => {
  //   scrollToBottom();
  // }, [input]);

  return (
    <form onSubmit={handleSubmit} className='panel_bar'>
      <input
        className='prompt_bar'
        type="text"
        placeholder="Escriu un missatge..."
        value={input}
        onChange={handleChange}
      />
      <button type="submit" className='submit_button'>
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg">
          <path d="M21.7071 2.29292C21.9787 2.56456 22.0707 2.96779 21.9438 3.33038L15.3605 22.14C14.9117 23.4223 13.1257 23.4951 12.574 22.2537L9.90437 16.2471L17.3676 7.33665C17.7595 6.86875 17.1312 6.24038 16.6633 6.63229L7.75272 14.0956L1.74631 11.426C0.504876 10.8743 0.577721 9.08834 1.85999 8.63954L20.6696 2.05617C21.0322 1.92926 21.4354 2.02128 21.7071 2.29292Z" fill="#FFFFFF"/>
        </svg>
      </button>
    </form>
  );
}

export default ChatPanel;
