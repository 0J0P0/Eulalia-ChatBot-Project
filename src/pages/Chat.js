// import { Chat } from '../components/chat'
// import { AI } from '@/lib/chat/actions'  // likely a component or utility related to managing AI functionality.  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// import { auth } from '../utils/auth.ts'  // handles authentication-related functionality.
// import { Session } from '../utils/types.ts'  // might represent a user session or authentication session.
// import { getMissingKeys } from '../actions'

import { nanoid } from '../utils/utils.ts'

import React from 'react';
import { useEffect, useState } from 'react'

import Footer from '../components/footer.js';
import InitialChat from '../components/chat/initial_chat.js' 
import ChatPanel from '../components/chat/chat_panel.js'

import '../styles/chat.css';

function ChatHome() {
  const id = nanoid()
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

export default ChatHome;