'use client';

import { useState } from 'react';
import { signOut } from 'next-auth/react';

interface LogoutDropdownProps {
  user: {
    name?: string;
    image?: string;
  };
}

export default function LogoutDropdown({ user }: LogoutDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      {/* 프로필 버튼 */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center bg-white text-gray-900 p-2 rounded-md"
      >
        <img src={user.image || "/google.svg"} alt="profile" className="w-6 h-6 mr-3 rounded-full" />
        <span className="text-lg font-medium">{user.name || "User"}</span>
        <svg
          className={`w-5 h-5 ml-2 transition-transform ${isOpen ? "rotate-180" : "rotate-0"}`}
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* 드롭다운 메뉴 */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-24 bg-white border border-gray-200 rounded-md shadow-lg">
          <button
            onClick={() => signOut()}
            className="block w-full text-left px-4 py-2 text-gray-800 hover:bg-gray-100 text-red-500"
          >
            로그아웃
          </button>
        </div>
      )}
    </div>
  );
}
