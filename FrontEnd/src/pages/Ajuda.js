import React from 'react';

import "../styles/ajuda.css";

import Logo from '../components/Logo.js';
import img_aj from "../img/Logo_Ajuntament.jpg";
import Footer from '../components/Footer.js';
// import img_ine from "../img/Logo_INE.jpg";
// import img_gene from "../img/Logo_Generalitat.jpg";
// import img_gob from "../img/Logo_Gobierno.png";
// import img_od from "../img/Logo_Open_Data.png";
// import img_od2 from "../img/Logo_Open_Data_2.png";


function Ajuda() {
  return (
    <div>
      <div className='ajuda_container'>
        <Logo subtitle="AJUDA"/>
        <div className="grid_container">
          
          <a href="https://opendata-ajuntament.barcelona.cat/es" className='One'>
              <img src={img_aj} alt='Open Data BCN'/>
              <div className='text_link'>
                  Open Data BCN
              </div>
          </a>
      
          <a href="https://portaldades.ajuntament.barcelona.cat/ca/" className='Two'>
              <img src={img_aj} alt='Barcelona Dades'/>
              <div className='text_link'>
                  Barcelona Dades
              </div>
          </a>
      
          <a href="https://www.ine.es/" className='Three'>
              <img src={img_aj} alt="Institut Nacional d'Estadística"/>
              <div className='text_link'>
                  Institut Nacional d'Estadística
              </div>
          </a>

          <a href="https://ajuntament.barcelona.cat/ca/" className='Four'>
              <img src={img_aj} alt='Ajuntament de Barcelona'/>
              <div className='text_link'>
                  Ajuntament de Barcelona
              </div>
          </a>
      
          <a href="https://web.gencat.cat/ca/inici/index.html" className='Five'>
              <img src={img_aj} alt='Generalitat de Catalunya'/>
              <div className='text_link'>
                  Generalitat de Catalunya
              </div>
          </a>
      
          <a href="https://www.lamoncloa.gob.es/Paginas/index.aspx" className='Six'>
              <img src={img_aj} alt='El Govern'/>
              <div className='text_link'>
                  El Govern
              </div>
          </a>
        </div>
      </div>
      <Footer />
    </div>
  );
}

export default Ajuda;
