import { getServerSession } from "next-auth";
import { authOptions } from "../../auth/[...nextauth]/route";

const BASE_URL = process.env.FASTAPI_URL;

export async function POST(request: Request) {
  try {
    const session = await getServerSession(authOptions);
    
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

    const { calendar_id } = await request.json();

    const response = await fetch(`${BASE_URL}/api/calendar/list_events`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: session.user.email,
        calendar_id,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch events. Status: ${response.status}`);
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
