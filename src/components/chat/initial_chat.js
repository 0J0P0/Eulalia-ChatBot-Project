import React from 'react';
import '../../styles/initial_chat.css';

function InitialChat() {
  return (
    <div className='initial_container'>
      <div className='intro_container'>
        <h1>Què ès Eulàlia?</h1>
        <p>Eulàlia és un assistent virtual que t'ajudarà a trobar la informació que necessites.</p>
      </div>
      <div className='intro_container'>
        <h1>Com usar Eulàlia?</h1>
        <p>Per començar a parlar amb Eulàlia, simplement escriu la teva pregunta en el xat de sota.</p>
      </div>
    </div>
  );
}

export default InitialChat;