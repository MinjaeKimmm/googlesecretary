import { getServerSession } from "next-auth";
import { authOptions } from "../../auth/[...nextauth]/route";

const BASE_URL = process.env.FASTAPI_URL;

export async function GET() {
  try {
    console.log('Calendar list request received');
    const session = await getServerSession(authOptions);
    console.log('Session:', { 
      email: session?.user?.email,
      hasAccessToken: !!session?.accessToken,
      hasRefreshToken: !!session?.refreshToken
    });
    
    if (!session?.user?.email) {
      console.error('No session or email found');
      return new Response(JSON.stringify({ error: "Not authenticated" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      });
    }

    if (!BASE_URL) {
      console.error('FASTAPI_URL not configured');
      return new Response(JSON.stringify({ error: "Server configuration error" }), {
        status: 500,
        headers: { "Content-Type": "application/json" },
      });
    }

    console.log(`Making request to ${BASE_URL}/api/calendar/list_calendars`);

    const response = await fetch(`${BASE_URL}/api/calendar/list_calendars`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${session.accessToken}`
      },
      body: JSON.stringify({ 
        email: session.user.email,
        access_token: session.accessToken,
        refresh_token: session.refreshToken
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('FastAPI error:', errorText);
      throw new Error(`Failed to fetch calendars. Status: ${response.status}. Error: ${errorText}`);
    }

    const data = await response.json();
    console.log('Calendar data from FastAPI:', data);
    return new Response(JSON.stringify(data), {
      headers: { "Content-Type": "application/json" },
    });
  } catch (error: any) {
    console.error('Calendar list error:', error);
    return new Response(JSON.stringify({ 
      error: error.message,
      stack: error.stack
    }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
