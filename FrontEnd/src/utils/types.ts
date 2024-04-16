import { Message } from 'ai'

export interface Chat extends Record<string, any> {  // defines the structure of a chat object.
  id: string
  title: string
  createdAt: Date
  userId: string
  path: string
  messages: Message[]  // array of messages.
  sharePath?: string  // optional property that represents the path to share the chat.
}

export type ServerActionResult<Result> = Promise<  // ServerActionResult is a generic type that represents the result of a server action.
  | Result
  | {
      error: string
    }
>  // It's a Promise that resolves to either the expected result (Result) or an object containing an error message.

export interface Session {
  user: {
    id: string
    email: string
  }
}  // Session is an object that represents a user session.

export interface AuthResult {
  type: string
  message: string
}  // AuthResult is an object that represents the result of an authentication action.

export interface User extends Record<string, any> {  // extends is a keyword used to establish inheritance between classes.
  id: string
  email: string
  password: string
  salt: string  
}  // User is an object that represents a user.
