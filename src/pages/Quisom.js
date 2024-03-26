import React from 'react'
import '../styles/quisom.css';

import quisom1 from '../img/quisom1.jpg';
import quisom2 from '../img/quisom2.jpg';

import Footer from '../components/Footer.js';

function Quisom() {
  return (
    <div>
      <div className='fill_logo'>
        <p>Quisom</p>
      </div>

      <div className='quisom_container'>
        <img src={quisom1} alt='El nostre Equip'/>
        <div className='quisom_text'>
          <h3>El nostre equip</h3>
          <p>El nostre equip està format per professionals amb una llarga trajectòria en el sector de la restauració. La nostra missió és oferir als nostres clients una experiència gastronòmica única, on la qualitat dels productes i el servei al client són la nostra prioritat.</p>
        </div>
      </div>

      <div className='project_container'>
        <img src={quisom2} alt='Sobre Eulalia'/>
        <div className='quisom_text'>
          <h3>Sobre Eulalia</h3>
          <p>Eulalia és la nostra xef i la responsable de la cuina. La seva passió per la cuina mediterrània i la seva creativitat són la clau del nostre èxit. La seva trajectòria professional l'ha portat a treballar en restaurants amb estrelles Michelin i a guanyar diversos premis en concursos de cuina.</p>
        </div>
      </div>

      <div className='contact_container'>
        <p>Si vols conèixer més sobre el nostre equip o sobre la nostra xef, pots contactar-nos a través del següent formulari:</p>
        <form>
          <label for='name'>Nom:</label>
          <input type='text' id='name' name='name' required></input>
          <label for='email'>Email:</label>
          <input type='email' id='email' name='email' required></input>
          <label for='message'>Missatge:</label>
          <textarea id='message' name='message' required></textarea>
          <input type='submit' value='Enviar'></input>
        </form>
      </div>
    
      <Footer />
    </div>

  );
}

export default Quisom