import React, { useState } from 'react';

import '../../styles/chat_panel.css';


function ChatPanel({ handleSend }) {
  const [input, setInput] = useState('');

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

  return (
    <form onSubmit={handleSubmit} className='panel_bar'>
      <input
        className='prompt_bar'
        type="text"
        placeholder="Escriu un missatge..."
        value={input}
        onChange={handleChange}
      />
      <button type="submit" className='submit_button'>Enviar</button>
    </form>
  );
}

export default ChatPanel;
