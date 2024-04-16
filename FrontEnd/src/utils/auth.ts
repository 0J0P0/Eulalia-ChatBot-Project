import NextAuth from 'next-auth'  // provides authentication functionality for Next.js applications.
import Credentials from 'next-auth/providers/credentials'  // enables authentication using credentials (i.e., email and password).
import { authConfig } from './auth.config.ts'
import { z } from 'zod' //  used here to validate the incoming credentials.
import { getStringFromBuffer } from './utils.ts'
import { getUser } from './actions.ts'

export const { auth, signIn, signOut } = NextAuth({  // auth, signIn, and signOut are exported from the result of calling NextAuth().
  ...authConfig,
  providers: [
    Credentials({
      async authorize(credentials) {  // function that takes the credentials and returns the user object if the credentials are valid.
        const parsedCredentials = z  // parsed and validated using Zod schema.
          .object({
            email: z.string().email(),
            password: z.string().min(6)
          })
          .safeParse(credentials)

        if (parsedCredentials.success) {  // if the credentials are valid, the user object is returned.
          const { email, password } = parsedCredentials.data
          const user = await getUser(email)  // getUser function is called with the email to retrieve the user object from the database.

          if (!user) return null

          const encoder = new TextEncoder()
          const saltedPassword = encoder.encode(password + user.salt) // The password is combined with the salt and hashed using the SHA-256 algorithm.
          const hashedPasswordBuffer = await crypto.subtle.digest(
            'SHA-256',
            saltedPassword
          ) 
          const hashedPassword = getStringFromBuffer(hashedPasswordBuffer)

          if (hashedPassword === user.password) {  // If the hashed password matches the stored password, the user object is returned.
            return user
          } else {
            return null
          }
        }
        return null
      }
    })
  ]
})
