import React from 'react';

import "../styles/ajuda.css";

import Logo from '../components/Logo.js';

import img_ine from "../img/ine.jpg";
import img_moncloa from "../img/moncloa.jpg";
import img_opendata from "../img/opendata.png";
import img_aj from "../img/barcelona.jpg";
import img_generalitat from "../img/generalitat.png";
import img_bcn_dades from "../img/Logo_Ajuntament.jpg";


function Ajuda() {
  return (
    <div>
        <Logo subtitle="AJUDA"/>
        <div className="grid_container">
          
          <a href="https://opendata-ajuntament.barcelona.cat/es" className='One'>
              <img src={img_opendata} alt='Open Data BCN'/>
              <div className='text_link'>
                  Open Data BCN
              </div>
          </a>
      
          <a href="https://portaldades.ajuntament.barcelona.cat/ca/" className='Two'>
              <img src={img_bcn_dades} alt='Barcelona Dades'/>
              <div className='text_link'>
                  Barcelona Dades
              </div>
          </a>
      
          <a href="https://www.ine.es/" className='Three'>
              <img src={img_ine} alt="Institut Nacional d'Estadística"/>
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
              <img src={img_generalitat} alt='Generalitat de Catalunya'/>
              <div className='text_link'>
                  Generalitat de Catalunya
              </div>
          </a>
      
          <a href="https://www.lamoncloa.gob.es/Paginas/index.aspx" className='Six'>
              <img src={img_moncloa} alt='El Govern'/>
              <div className='text_link'>
                  El Govern
              </div>
          </a>

        </div>
    </div>
  );
}

export default Ajuda;
