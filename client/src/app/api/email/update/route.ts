import { NextRequest } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../[...nextauth]/route';
import apiClient from '@/lib/api-client';

export async function POST(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session) {
      return new Response('Unauthorized', { status: 401 });
    }

    const body = await req.json();

    const response = await apiClient.post('/api/email/update', {
      credential: body.credential
    }, {
      headers: {
        Authorization: `Bearer ${session.accessToken}`
      }
    });

    return new Response(JSON.stringify(response.data), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error: any) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
