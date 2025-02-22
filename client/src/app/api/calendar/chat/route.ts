import { getServerSession } from "next-auth";
import { authOptions } from "../../auth/[...nextauth]/route";

const BASE_URL = process.env.FASTAPI_URL;

export async function POST(request: Request) {
  try {
    const session = await getServerSession(authOptions);
    console.log('Session data:', {
      email: session?.user?.email,
      hasAccessToken: !!session?.accessToken,
      hasRefreshToken: !!session?.refreshToken
    });
    
    if (!session?.user?.email) {
      return new Response(JSON.stringify({ error: "Not authenticated" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      });
    }

    if (!BASE_URL) {
      return new Response(JSON.stringify({ error: "Server configuration error" }), {
        status: 500,
        headers: { "Content-Type": "application/json" },
      });
    }

    const body = await request.json();
    console.log('Request body received:', body);
    
    // Handle both formats (message or user_message)
    const user_message = body.user_message || body.message;
    const calendar_id = body.calendar_id;
    
    if (!user_message) {
      return new Response(JSON.stringify({ error: "Message is required" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    if (!calendar_id || calendar_id === 'id' || calendar_id === '') {
      return new Response(JSON.stringify({ error: "Valid calendar ID is required" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }
    
    const payload = {
      user_email: session.user.email,
      user_message,
      calendar_id,
      access_token: session.accessToken,
      refresh_token: session.refreshToken
    };
    
    console.log('Sending payload to backend:', {
      user_email: payload.user_email,
      calendar_id: payload.calendar_id,
      hasAccessToken: !!payload.access_token,
      hasRefreshToken: !!payload.refresh_token
    });
    console.log('Sending payload to FastAPI:', payload);

    const response = await fetch(`${BASE_URL}/api/calendar/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${session.accessToken}`
      },
      body: JSON.stringify({
        user_email: session.user.email,
        access_token: session.accessToken,
        refresh_token: session.refreshToken,
        user_message,
        calendar_id,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to send chat message. Status: ${response.status}`);
    }

    const data = await response.json();
    return new Response(JSON.stringify(data), {
      headers: { "Content-Type": "application/json" },
    });
  } catch (error: any) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
