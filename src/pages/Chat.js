// import { nanoid } from '../utils/utils.ts'
// import { Chat } from '../components/chat'
// import { AI } from '@/lib/chat/actions'  // likely a component or utility related to managing AI functionality.  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// import { auth } from '../utils/auth.ts'  // handles authentication-related functionality.
// import { Session } from '../utils/types.ts'  // might represent a user session or authentication session.
// import { getMissingKeys } from '../actions'

import React from 'react';
import InitialChat from '../components/chat/initialchat.js' 
import Footer from '../components/footer.js';

function ChatHome() {
  return (
    <div>
      <InitialChat />

      {/* <ChatConversation /> */}

      {/* <ChatPanel /> */}

      <Footer />
    </div>
  );
}

export default ChatHome;