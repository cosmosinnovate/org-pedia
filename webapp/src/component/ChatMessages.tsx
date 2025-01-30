import React, { useRef } from "react";
import { Message } from "../features/chat/chatSlice";
import ReactMarkdown, { Components } from 'react-markdown';

import 'react-toastify/dist/ReactToastify.css';
import userAssistant from '../assets/userAssistant.png';
import remarkGfm from 'remark-gfm';

interface ChatMessagesProps {
    messages: Message[]
    markdownComponents: Components
}

const ChatMessages: React.FC<ChatMessagesProps> = React.memo(({ messages, markdownComponents }) => {
    const messageListRef = useRef<HTMLDivElement>(null);
    const renderMessage = (message: Message, index: number) => (
        <div
            key={index}
            className={`flex flex-col ${message.role === 'user' ? 'justify-start' : 'justify-end'}`}
        >
            {message.role !== 'user' && (
                <div className='mb-4 flex-col'>
                    <img src={userAssistant} alt="User" className="w-8 h-8 rounded-full"></img>
                    {!message.content && <p>...</p>}
                </div>
            )}

            <div
                className={`mb-4 ${message.role === 'user'
                    ? 'flex max-w-max p-3 bg-gray-200 text-black rounded-2xl top-0'
                    : 'text-gray-500 rounded-lg'
                    }`}
            >
                {message.role === 'user' ? (
                    message.content
                ) : (
                    <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={markdownComponents}
                    >
                        {message.content}
                    </ReactMarkdown>
                )}
            </div>
        </div>
    );

    return (
        <div className="flex flex-col p-4 space-y-4 justify-items-end" ref={messageListRef}>
            {messages.map(renderMessage)}
        </div>
    );
});


export default ChatMessages;