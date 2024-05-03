import React from 'react'

import '../styles/quisom.css';

import quisom1 from '../img/quisom1.jpg';
import quisom2 from '../img/quisom2.jpg';
import phone from '../img/phone.svg';
import mail from '../img/mail.svg';
import location from '../img/location.svg';

import Logo from '../components/Logo.js';


function Quisom() {

  const handleSend = async (event) => {
    event.preventDefault();
  
    const form = event.target.closest('form');
    const formData = new FormData(form);
  
    const message = {
      name: formData.get('name'),
      email: formData.get('email'),
      message: formData.get('message')
    };
  
    try {
      await processMessageBackEnd(message);
      alert('Missatge enviat correctament');
      form.reset();
    } catch (error) {
      console.error('Error:', error);
      alert('Error en enviar el missatge');
    }
  };
  
  async function processMessageBackEnd(message) {
    try {
      fetch('/api/store_contact_messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(message)
      })
      .then(response => response.json())
      .then(data => {console.log('Success:', data)})
    } catch (error) {
      console.error('Error:', error);
    }
  }

  return (
    <div>
      <Logo subtitle='QUI SOM' />

      <div className='quisom_container'>
        <img src={quisom1} alt='El nostre Equip'/>
        <div className='quisom_text'>
          <h3>El nostre equip</h3>
          <p>L'equip de desenvolupadors està format per un grup de 10 estudiants del 3r any del grau de Ciència i Enginyeria de Dades a la Universitat Politècnica de Catalunya.</p>
        </div>
      </div>

      <div className='project_container'>
        <img src={quisom2} alt='Sobre Eulalia'/>
        <div className='quisom_text'>
          <h3>Sobre Eulalia</h3>
          <p>Eulàlia és un assistent de xat dissenyat per oferir suport intern a l'equip de tècnics de l'Ajuntament de Barcelona. La seva principal tasca és proporcionar respostes a les preguntes dels tècnics utilitzant una base de dades que conté informació detallada sobre els serveis i les estadístiques oferts per l'Ajuntament de Barcelona.</p>
        </div>
      </div>

      <div className='contact_container'>
        <form className='form_container'>
          <label for='name'>Nom:</label>
          <input type='name' id='name' name='name' required></input>
          <label for='email'>Email:</label>
          <input type='email' id='email' name='email' required></input>
          <label for='message'>Missatge:</label>
          <textarea id='message' name='message' required></textarea>
          <input type='submit' value='Enviar' onClick={handleSend}></input>
        </form>
        <div className='contact_data_container'>
          <p className='description_text'>Si vols conèixer més sobre el nostre equip o sobre la Eulàlia, pots contactar-nos a través del següent formulari:</p>
          <div className='contact_data'>
            <div className='contact_item'>
              <img src={phone} alt='phone' />
              <p>+34 673 91 45 60</p>
            </div>
            <div className='contact_item'>
              <img src={mail} alt='mail' />
              <p>eulalia.contact@gmail.com</p>
            </div>
            <div className='contact_item'>
              <img src={location} alt='location' />
              <p>C. de Jordi Girona, 1, 08034 Barcelona</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Quisom