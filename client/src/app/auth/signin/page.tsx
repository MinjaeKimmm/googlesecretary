'use client';

import { SignInButton } from '@/components/auth/signin-button';

export default function SignIn() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="w-full max-w-md space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-bold tracking-tight">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Use your Google account to access the Workspace Assistant
          </p>
        </div>
        <div className="mt-8 flex justify-center">
          <SignInButton />
        </div>
      </div>
    </div>
  );
}
