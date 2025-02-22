'use client';

import * as React from 'react';
import { Message } from '@/types/services';
import Markdown from 'react-markdown';
import { ThreeDots } from 'react-loader-spinner';
import { useSession } from 'next-auth/react';

interface MessageListProps {
  messages: Message[];
  selectedCharacter: string;
}

export function MessageList({ messages, selectedCharacter }: MessageListProps) {
  const { data: session } = useSession();
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  const assistantAvatars: Record<string, string> = {
    Bunny: "/profile/bunny.png",
    Shortcut: "/profile/shortcut.png",
    Wolf: "/profile/wolf.png",
    Teenager: "/profile/teenager.png",
    Tuxedo: "/profile/tuxedo.png",
    Yukata: "/profile/yukata.png",
  };

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col space-y-4 p-3 overflow-y-auto scrollbar scrollbar-thumb-blue scrollbar-thumb-rounded scrollbar-track-blue-lighter scrollbar-w-2 scrolling-touch">
      {messages.map((message, index) => (
        message.role === 'user' ? (
          <div key={index}>
            <div className="flex items-end justify-end">
              <div className="flex flex-col space-y-2 text-md leading-tight max-w-lg mx-2 order-1 items-end">
                <div>
                  <span className="px-4 py-3 rounded-xl inline-block rounded-br-none bg-blue-500 text-white whitespace-pre-wrap">
                    {message.content}
                  </span>
                </div>
              </div>
              <img 
                src={session?.user?.image || "https://i.pravatar.cc/100?img=7"} 
                alt="" 
                className="w-6 h-6 rounded-full order-2"
              />
            </div>
          </div>
        ) : (
          <div key={index}>
            <div className="flex items-end">
              <div className="flex flex-col space-y-2 text-md leading-tight max-w-lg mx-2 order-2 items-start">
                <div>
                  <span className="px-4 py-3 rounded-xl inline-block rounded-bl-none bg-gray-100 text-gray-600">
                    {message.content === "Loading..." ? (
                      <div className="flex items-center justify-center w-16">
                        <ThreeDots
                          height="40"
                          width="40"
                          radius="6"
                          color="#4B5563"
                          ariaLabel="three-dots-loading"
                          visible={true}
                        />
                      </div>
                    ) : (
                      <div className="markdown-content space-y-0.5">
                        {message.content.split('\n').map((line, i, lines) => {
                          if (!line.trim()) {
                            // Check if this empty line is between a main bullet and its sub-items
                            const prevLine = i > 0 ? lines[i-1].trim() : '';
                            const nextLine = i < lines.length - 1 ? lines[i+1].trim() : '';
                            const isPrevMainBullet = prevLine.startsWith('- **');
                            const isNextSubItem = nextLine.startsWith('  -');
                            const isNextMainBullet = nextLine.startsWith('- **');

                            if (isPrevMainBullet && isNextSubItem) {
                              return null; // Skip empty line between header and sub-items
                            }
                            if (isPrevMainBullet && isNextMainBullet) {
                              return <div key={i} className="h-6" />; // More space between main sections
                            }
                            return <div key={i} className="h-3" />; // Default spacing
                          }
                          
                          const boldPattern = /\*\*(.*?)\*\*/g;
                          const processText = (text: string) => {
                            const parts = text.split(boldPattern);
                            return parts.map((part, j) => (
                              j % 2 === 1 ? 
                                <strong key={j} className="font-bold">{part}</strong> : 
                                <span key={j}>{part}</span>
                            ));
                          };

                          // Handle bullet points with indentation
                          const bulletMatch = line.match(/^(\s*)(-|•)\s+(.*)$/);
                          if (bulletMatch) {
                            const [, indent, , content] = bulletMatch;
                            const indentLevel = Math.floor(indent.length / 2); // 2 spaces = 1 level
                            const isMainBullet = indentLevel === 0;
                            
                            // Check if this is a main bullet and has sub-items
                            const hasSubItems = isMainBullet && 
                              i < lines.length - 1 && 
                              lines[i+1].trim().startsWith('  -');

                            // Check if this is the last sub-item
                            const isLastSubItem = !isMainBullet && 
                              (i === lines.length - 1 || 
                               !lines[i+1].trim().startsWith('  -'));

                            return (
                              <div 
                                key={i} 
                                className={`
                                  flex items-start
                                  ${isMainBullet 
                                    ? (hasSubItems ? 'mb-1.5' : 'mb-4')
                                    : (isLastSubItem ? 'mb-4' : 'mb-1')}
                                `}
                                style={{ 
                                  paddingLeft: isMainBullet ? '0.25rem' : `${(indentLevel + 1) * 1}rem`
                                }}
                              >
                                <span className="inline-block w-2 mr-2 text-center leading-normal">•</span>
                                <div className="flex-1">
                                  {isMainBullet ? (
                                    <div className="font-bold">{processText(content)}</div>
                                  ) : (
                                    processText(content)
                                  )}
                                </div>
                              </div>
                            );
                          }

                          // Regular text
                          return (
                            <div key={i} className="mb-2">
                              {processText(line)}
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </span>
                </div>
              </div>
              <img 
                src={assistantAvatars[selectedCharacter] || "/avatars/bunny.png"} 
                alt="assistant-avatar" 
                className="w-6 h-6 rounded-full order-1"
              />
            </div>
          </div>
        )
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
}
