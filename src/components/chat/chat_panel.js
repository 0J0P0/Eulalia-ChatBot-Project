import React from 'react';
import '../../styles/chat_panel.css';
import Textarea from 'react-textarea-autosize'


import { nanoid } from 'nanoid'
import { useEnterSubmit } from './hooks/enter_submit'
import { Button } from './hooks/chat_button.js'
import { IconArrowElbow } from '../icons.js'


// export interface ChatPanelProps {
//   id?: string
//   title?: string
//   input: string
//   setInput: (value: string) => void
// }

function ChatPanel({ id, title, input, setInput }) {
  const { formRef, onKeyDown } = useEnterSubmit()
  const inputRef = React.useRef<HTMLTextAreaElement>(null)

  return (
    <div>
      {/* <ButtonScrollToBottom />  Button to scroll to the bottom of the chat */}
      <form
      ref={formRef}
      onSubmit={async (e) => {
        e.preventDefault()
        
        const value = input.trim()
        setInput('')
        if (!value) return

        // setMessages(currentMessages => [  // append the new message to the list of messages
        //   ...currentMessages,
        //   {
        //     id: nanoid(),
        //     display: <UserMessage>{value}</UserMessage>
        //   }
        //   ])

        // const responseMessage = await submitUserMessage(value)
        // setMessages(currentMessages => [...currentMessages, responseMessage])
        }
      }
      >
        <div className='panel_bar'>
          <Textarea
            inputRef={inputRef}
            tabIndex={0}
            onKeyDown={onKeyDown}
            placeholder='Escriu un missatge...'
            className='prompt_bar'
            autoFocus
            spellCheck={false}
            autoComplete="off"
            autoCorrect="off"
            name="message"
            rows={1}
            value={input}
            onChange={e => setInput(e.target.value)}
          />
          <div>
            <Button type="submit" size="icon" disabled={input === ''}>
              <IconArrowElbow />
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
}

export default ChatPanel;