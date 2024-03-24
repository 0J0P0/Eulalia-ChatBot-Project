import React from 'react'
import { useEffect, useState } from 'react'
import { useUIState, useAIState } from 'ai/rsc'

import Footer from '../components/footer.js'

// import AI from '../components/chat/ai.tsx'
import ChatConversation from '../components/chat/chat_conversation.js'
import InitialChat from '../components/chat/initial_chat.js'
import ChatPanel from '../components/chat/chat_panel.js'

import '../styles/chat.css'
import { nanoid } from '../utils/utils.ts'

import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css'
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
  TypingIndicator
}
from '@chatscope/chat-ui-kit-react'


function Chat() {
  const id = nanoid()
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('')

  return (
    <div className='chat_container'>
      <InitialChat />

      {/* <ChatConversation /> */}

      <ChatPanel id={id} input={input} setInput={setInput} />

      <Footer />
    </div>
  );
}


const API_KEY = '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'
const systemMessage = {
  "role": "system", "content": "Explain things like you're talking to a software professional with 2 years of experience."
}


function Bot() {
  // const id = nanoid()
  // const session = (await auth()) as Session

  const [messages, setMessages] = useState([]);

  const [isTyping, setIsTyping] = useState(false);

  // Handle the sending a message
  const handleSend = async (message) => {
    const newMessage = {
      message,
      direction: 'outgoing',
      sender: "user"
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
    // API is expecting objects in format of { role: "user" or "assistant", "content": "message here"}
    let apiMessages = chatMessages.map((messageObject) => {  // Format the messages for the API
      let role = "";
      if (messageObject.sender === "Eulàlia") {
        role = "assistant";
      } else {
        role = "user";
      }
      return { role: role, content: messageObject.message}
    });

    // Get the request body set up with the model we plan to use
    // and the messages which we formatted above. We add a system message in the front to'
    // determine how we want chatGPT to act. 
    const apiRequestBody = {
      "model": "gpt-3.5-turbo",
      "messages": [
        systemMessage,  // The system message DEFINES the logic of our chatGPT
        ...apiMessages // The messages from our chat with Eulàlia
      ]
    }

    // Make the request to the chatGPT API
    await fetch("https://api.openai.com/v1/chat/completions", 
    {
      method: "POST",
      headers: {
        "Authorization": "Bearer " + API_KEY,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(apiRequestBody)
    }).then((data) => {
      return data.json();
    }).then((data) => {
      console.log(data);
      setMessages([...chatMessages, {  // Add the response from chatGPT to our messages
        message: data.choices[0].message.content,
        sender: "Eulàlia"
      }]);
      setIsTyping(false);
    });
  }

  return (
    <div className='chat_container'>
      <div className='chat_test'>
        <MessageList 
          scrollBehavior="smooth" 
          typingIndicator={isTyping ? <TypingIndicator content="Eulàlia is typing" /> : null}
        >
          {messages.map((message, index) => (
            <div key={index}>
              {message.sender === "Eulàlia" ? (
                <div className='eulalia_message'>
                  {message.message}
                </div>
              ) : (
                <div className='user_message'>
                  {message.message}
                </div>
              )}
            </div>
          ))}
        </MessageList>
        <MessageInput placeholder="Type message here" onSend={handleSend} />        
      </div>
    </div>
  )
}

export default Bot;