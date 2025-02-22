'use client';

import { signIn, signOut, useSession } from 'next-auth/react';

export default function SignInButton() {
    const { status, data: session } = useSession();

    return (
        <div className="flex items-center">
            {status === "authenticated" ? (
                <button onClick={() => signOut()} className="text-lg flex items-center bg-white text-gray-900 p-2 rounded-md">
                    <img src={session?.user?.image || "google.svg"} alt="profile" className="w-6 h-6 mr-2 rounded-full" />
                    Logout
                </button>
            ) : (
                <button 
                    onClick={() => signIn("google", { 
                        redirect: true,
                        callbackUrl: window.location.origin 
                    })} 
                    className="text-lg flex items-center bg-white text-gray-900 p-2 rounded-md"
                >
                    <img src="google.svg" alt="Google Login" className="w-4 h-4 mr-2" />
                    Login
                </button>
            )}
        </div>
    );
}
