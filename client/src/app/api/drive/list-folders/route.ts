import { NextRequest } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const { parentId, accessToken } = await req.json();

    if (!accessToken) {
      console.error('No access token provided');
      return Response.json(
        { error: 'No access token provided' },
        { status: 401 }
      );
    }

    // Log token info (first few chars only)
    console.log('Token info:', {
      length: accessToken.length,
      preview: accessToken.substring(0, 20) + '...',
    });

    const url = 'https://www.googleapis.com/drive/v3/files';
    const params = new URLSearchParams({
      q: `mimeType='application/vnd.google-apps.folder' and '${parentId || 'root'}' in parents`,
      fields: 'files(id,name)',
      orderBy: 'name',
      pageSize: '100'
    });

    console.log('Fetching from URL:', `${url}?${params}`);

    const response = await fetch(`${url}?${params}`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Accept': 'application/json',
      }
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Google Drive API error:', {
        status: response.status,
        statusText: response.statusText,
        error: errorText
      });
      throw new Error(`Google Drive API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    console.log('Received data:', data);

    return Response.json({ folders: data.files || [] });
  } catch (error) {
    console.error('Error in list-folders:', error);
    return Response.json(
      { error: error instanceof Error ? error.message : 'Failed to fetch folders' },
      { status: 500 }
    );
  }
}
