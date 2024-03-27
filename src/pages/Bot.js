import React from 'react'
import { useEffect, useState } from 'react'
// import { useUIState, useAIState } from 'ai/rsc'

import Footer from '../components/Footer.js'

// import AI from '../components/chat/ai.tsx'
// import InitialChat from '../components/chat/initial_chat.js'
// import ChatPanel from '../components/chat/chat_panel.js'
// import { nanoid } from '../utils/utils.ts'

import '../styles/bot.css'

import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css'

import ChatConversation from '../components/chat/ChatConversation.js'
import ChatPanel from '../components/chat/ChatPanel.js'
import Logo from '../components/Logo.js'


// function Chat() {
//   const id = nanoid()
//   const [messages, setMessages] = useState([]);
//   const [input, setInput] = useState('')

//   return (
//     <div className='chat_container'>
//       <InitialChat />

//       {/* <ChatConversation /> */}

//       <ChatPanel id={id} input={input} setInput={setInput} />

//       <Footer />
//     </div>
//   );
// }


const API_KEY = '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'
const systemMessage = {
  'role': 'system', 'content': "Ets un assistent de xat dissenyat per oferir suport intern a un equip de tècnics de l'Ajuntament de Barcelona. La teva tasca principal és proporcionar respostes a les preguntes dels tècnics utilitzant una base de dades que conté informació detallada sobre els serveis i les estadístiques oferts per l'Ajuntament de Barcelona. Si no teniu la resposta adequada, podeu suggerir-vos que es comuniquin a través de la pàgina de contacte o dirigir-los a la secció d'informació rellevant."
}

// https://github.com/coopercodes/ReactChatGPTChatbot

function Bot() {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);

  // Handle the sending a message
  const handleSend = async (message) => {
    const newMessage = {
      message,
      direction: 'outgoing',
      sender: 'user'
    };

    const newMessages = [...messages, newMessage];
    
    // add the new message to the state
    setMessages(newMessages);

    // Set the typing indicator to true
    setIsTyping(true);
    // Process the message to chatGPT and wait for a response
    await processMessageToChatGPT(newMessages);
  };

  async function processMessageToChatGPT(chatMessages) {
    // Format messages for chatGPT API
    // API is expecting objects in format of { role: 'user' or 'assistant', 'content': 'message here'}
    let apiMessages = chatMessages.map((messageObject) => {  // Format the messages for the API
      let role = '';
      if (messageObject.sender === 'Eulàlia') {
        role = 'assistant';
      } else {
        role = 'user';
      }
      return { role: role, content: messageObject.message}
    });

    // Get the request body set up with the model we plan to use
    // and the messages which we formatted above. We add a system message in the front to'
    // determine how we want chatGPT to act. 
    const apiRequestBody = {
      'model': 'gpt-3.5-turbo',
      'messages': [
        systemMessage,  // The system message DEFINES the logic of our chatGPT
        ...apiMessages // The messages from our chat with Eulàlia
      ]
    }

    // Make the request to the chatGPT API
    await fetch('https://api.openai.com/v1/chat/completions', 
    {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + API_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(apiRequestBody)
    }).then((data) => {
      return data.json();
    }).then((data) => {
      console.log(data);
      setMessages([...chatMessages, {  // Add the response from chatGPT to our messages
        message: data.choices[0].message.content,
        sender: 'Eulàlia'
      }]);
      setIsTyping(false);
    });
  }

  return (
    <div>
      <Logo subtitle='' />
      <div className='chat_container'>
        <ChatConversation messages={messages} isTyping={isTyping} />
        <ChatPanel handleSend={handleSend} />
        <Footer />
      </div>
    </div>
  )
}

export default Bot;