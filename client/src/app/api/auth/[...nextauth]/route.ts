import NextAuth from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';
import { JWT } from 'next-auth/jwt';
import type { NextAuthOptions } from 'next-auth';

type Token = JWT & {
  accessToken?: string;
  refreshToken?: string;
};

type Account = {
  access_token?: string;
  expires_at?: number;
  refresh_token?: string;
};

export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      authorization: {
        params: {
          scope: 'openid email profile https://www.googleapis.com/auth/calendar.readonly https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/calendar.events',
          prompt: 'consent',
          access_type: 'offline',
          response_type: 'code'
        }
      },
      httpOptions: {
        timeout: 10000 // 10 seconds
      }
    })
  ],
  callbacks: {
    async jwt({ token, account }: { token: Token; account: Account | null }) {
      if (account) {
        token.accessToken = account.access_token;
        token.refreshToken = account.refresh_token;
      }
      return token;
    },
    async session({ session, token }: { session: any; token: Token }) {
      session.accessToken = token.accessToken;
      session.refreshToken = token.refreshToken;
      return session;
    }
  },
  debug: true,
  secret: process.env.NEXTAUTH_SECRET,
  pages: {
    signIn: '/',
    error: '/'
  }
};

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
