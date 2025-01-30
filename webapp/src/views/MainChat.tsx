import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Components } from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/cjs/styles/prism'
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import SideMenu from '../component/SideMenu';
import userAssistant from '../assets/userAssistant.png';
import uploadFile from '../assets/load-file.png';
import sendMessage from '../assets/send-message.png';
import { baseURL } from '../service';
import { RootState } from '../store';
import { useAppSelector } from '../hooks';
import { Message } from '../features/chat/chatSlice';
import { useNavigate, useParams } from 'react-router-dom';
import { LLMModels } from '../util/model';
import CallToActionItems from '../component/CTA';
import ChatMessages from '../component/ChatMessages';


const MainChat: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const { chatId } = useParams<{ chatId?: string }>();
    const user = useAppSelector((selector: RootState) => selector.auth.user)
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<null | HTMLDivElement>(null);
    const abortControllerRef = useRef<AbortController | null>(null);
    const [selectedChatService, setSelectedChatService] = useState<LLMModels>('ollama');
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    const [copiedCode, setCopiedCode] = useState('');
    const navigate = useNavigate()

    const startNewChat = useCallback(async () => {
        try {
            const response = await fetch(`${baseURL}/start-chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${user?.access_token}`
                },
                body: JSON.stringify({ messages: messages })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log(data)
            navigate(`/chat/${data.chat_id}`, { replace: true });
        } catch (error) {
            console.error('Error starting new chat:', error);
            // toast.error('Failed to start a new chat. Please try again.');
        }
    }, [messages, navigate, user?.access_token]);

    const fetchChats = useCallback(async () => {
        try {
            setIsLoading(true);
            const response = await fetch(`${baseURL}/chats/${chatId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${user?.access_token}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const fetchedChat = await response.json();
            setMessages(fetchedChat);
        } catch (error) {
            console.error('Error fetching chat:', error);
            toast.error('Failed to load chat history. Please try again.');
            setMessages([]);
        } finally {
            setIsLoading(false);
        }
    }, [chatId, user?.access_token]);

    useEffect(() => {
        const loadData = async () => {
            if (chatId) {
                await fetchChats();
            }
        };

        loadData();
    }, [chatId, fetchChats]);

    const updateChat = useCallback(async () => {
        try {
            const response = await fetch(`${baseURL}/chats/${chatId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${user?.access_token}`
                },
                body: JSON.stringify({ messages: messages })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const fetchedChat = await response.json();
            console.log(fetchedChat);
            setMessages(fetchedChat);
        } catch (error) {
            console.error('Error fetching chat:', error);
            toast.error('Failed to fetch chat. Please try again.');
        }
    }, [chatId, messages, user?.access_token]);

    const handleSubmit = useCallback(async (event?: React.FormEvent<HTMLFormElement | KeyboardEvent | HTMLTextAreaElement>, inputMessage?: string) => {
        event?.preventDefault();
        const messageToSend = inputMessage || inputValue;
        if (!messageToSend.trim() || isLoading) return;
        const userMessage: Message = { role: 'user', content: messageToSend };
        setMessages(prevMessages => [...prevMessages, userMessage]);
        setInputValue('');
        setIsLoading(true);

        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
        }

        abortControllerRef.current = new AbortController();
        const signal = abortControllerRef.current.signal;

        try {

            let response: Response;
            switch (selectedChatService) {
                case 'ollama':
                    response = await fetch(`${baseURL}/chats`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${user?.access_token}`
                        },
                        body: JSON.stringify({ messages: [...messages, userMessage] }),
                        signal,
                    });
                    break;
                default:
                    throw new Error(`Unknown chat service: ${selectedChatService}`);
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body?.getReader();
            if (!reader) {
                throw new Error('Response body is not readable');
            }

            const assistantMessage: Message = { role: 'assistant', content: '' };
            setMessages(prevMessages => [...prevMessages, assistantMessage]);

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                const chunk = new TextDecoder().decode(value);
                const lines = chunk.split('\n\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') {
                            setIsLoading(false);
                            break;
                        }

                        try {
                            const parsedData = JSON.parse(data);
                            if (parsedData.content) {
                                const processedChunks = new Set();
                                setMessages(prevMessages => {
                                    const newMessages = [...prevMessages];
                                    const lastMessage = newMessages[newMessages.length - 1];
                                    if (lastMessage.role === 'assistant' && !processedChunks.has(parsedData.id)) {
                                        processedChunks.add(parsedData.id);
                                        lastMessage.content += parsedData.content;
                                    }
                                    return newMessages;
                                });
                            }
                        } catch (error) {
                            console.error('Error parsing SSE data:', error);
                        }
                    }
                }

            }
        } catch (error) {

            if (error instanceof DOMException && error.name === 'AbortError') {
                toast.error('Request timed out. Please try again.');
                return;
            }

        } finally {
            setIsLoading(false);
        }

        if (chatId) {
            await updateChat();
        } else {
            await startNewChat();
        }
    }, [
        inputValue,
        isLoading,
        messages,
        selectedChatService,
        startNewChat,
        updateChat,
        chatId,
        user?.access_token,
    ])

    const toggleSidebar = () => {
        setIsSidebarOpen(!isSidebarOpen);
    };

    const scrollToBottom = useCallback(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [scrollToBottom, messages]);

    useEffect(() => {
        return () => {
            if (abortControllerRef.current) {
                abortControllerRef.current.abort();
            }
        };
    }, []);

    const copyToClipboard = (code: string) => {
        navigator.clipboard.writeText(code).then(() => {
            setCopiedCode(code);
            setTimeout(() => setCopiedCode(''), 2000);
        });
    };

    const markdownComponents: Components = {
        p: ({ children }) => <p className="mb-2">{children}</p>,
        h1: ({ children }) => <h1 className="text-2xl font-bold mb-2">{children}</h1>,
        h2: ({ children }) => <h2 className="text-xl font-bold mb-2">{children}</h2>,
        h3: ({ children }) => <h3 className="text-lg font-bold mb-2">{children}</h3>,
        ul: ({ children }) => <ul className="list-disc list-inside mb-2">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal list-inside">{children}</ol>,
        li: ({ children }) => <li className="mb-1">{children}</li>,
        code: ({ className, children, ...props }) => {
            const match = /language-(\w+)/.exec(className || '');
            const codeContent = String(children).replace(/\n$/, '');
            const language = match ? match[1] : 'text';
            return match ? (
                <div className='relative'>
                    <div className='py-1 px-2 rounded-t-lg font-mono text-xs text-gray-800'>
                        <strong>{language.toUpperCase()}</strong>
                    </div>
                    <SyntaxHighlighter
                        style={vscDarkPlus}
                        className="my-2 rounded-lg"
                        language={match[1]}
                        PreTag="div"
                    >
                        {codeContent}
                    </SyntaxHighlighter>
                    <button
                        onClick={() => copyToClipboard(codeContent)}
                        className=" top-2 right-2 text-xs bg-gray-800 text-white px-2 py-1 rounded hover:bg-gray-700 transition"
                    >
                        {copiedCode === codeContent ? 'Copied!' : 'Copy'}
                    </button>
                </div>

            ) : (
                <code className="my-2 bg-gray-100 px-1 py-1 italic rounded-lg" {...props}>
                    {children}
                </code>
            );
        },
        pre: ({ children }) => <pre className="rounded whitespace-pre-wrap">{children}</pre>,
        a: ({ href, children }) => <a href={href} className="text-blue-600 hover:underline">{children}</a>,
        blockquote: ({ children }) => <blockquote className="border-l-4 border-gray-100 pl-4 italic my-2">{children}</blockquote>,
        hr: () => <hr className="my-4 border-t border-gray-50" />,
        img: ({ src, alt }) => <img src={src} alt={alt} className="max-w-full h-auto my-2" />,
        // Updated table components
        table: ({ children }) => (
            <div className="overflow-x-auto">
                <table className="table-auto border-collapse my-2 w-full bg-white shadow-lg">
                    <tbody>{children}</tbody>
                </table>
            </div>
        ),
        th: ({ children }) => (
            <th className="border border-gray-300 px-4 py-2 font-bold bg-gray-100 text-left">
                {children}
            </th>
        ),
        td: ({ children }) => <td className="border border-gray-300 px-4 py-2">{children}</td>,
        tr: ({ children }) => <tr>{children}</tr>,
    };

    const handleSelectedChatService = (event: React.ChangeEvent<HTMLSelectElement>) => {
        setSelectedChatService(event.target.value as 'ollama' | 'bedrock');
    };

    const handleSubmitCustom = (messageContent: string) => {
        handleSubmit(undefined, messageContent);
    };

    const handleAbort = (event?: React.MouseEvent<HTMLButtonElement>) => {
        event?.preventDefault();
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            setIsLoading(false);
            setInputValue('');
            toast.error('Request cancelled.');
        }
    };

    return (
        <div className="flex flex-col h-screen transition-all duration-300">
            <div className="flex-1 flex flex-row">
                {/* SideMenu remains fixed but with modified width handling */}
                <SideMenu
                    selectedChatService={selectedChatService}
                    handleSelectedChatService={handleSelectedChatService}
                    isOpen={isSidebarOpen}
                    toggleMenu={toggleSidebar}
                />

                {/* Main content area */}
                <main className={`flex-1 flex flex-col items-center mx-auto transition-all duration-300 ease-in-out ${isSidebarOpen ? 'ml-64' : 'ml-12' // Adjust margin based on sidebar state
                    }`}>
                    <div className="flex w-full flex-col">
                        <div className={`flex justify-center text-5xl ${messages.length > 0 ? 'hidden' : 'block'} mx-auto`}>
                            <span className="text-[#fa6f73] font-['poppins'] font-bold">Org</span>
                            <span className="text-[#a1b3ff] font-extrabold font-['poppins']">//</span>
                            <span className="text-[#a1b3ff] font-bold">Pedia</span>
                        </div>

                        <div className={`font-semibold text-[32px] text-center ${messages.length > 0 ? 'hidden' : 'block'}`}>
                            Unlocking the Potential of Organizational Wisdom
                        </div>

                        {messages.length === 0 && <CallToActionItems messages={messages} handleSubmitCustom={handleSubmitCustom} />}

                        <div className="flex flex-1 w-full md:w-[830px] mx-auto pb-20 overflow-hidden">
                            <div className="flex flex-col space-y-10 justify-items-end overflow-auto w-full">
                                {/* Chat messages */}
                                <ChatMessages messages={messages} markdownComponents={markdownComponents} />
                                {isLoading && (
                                    <div className="flex items-start p-4">
                                        <div className="flex-shrink-0 w-8 h-8 mr-4">
                                            <img src={userAssistant} alt="Assistant" className="w-full h-full rounded-full" />
                                        </div>
                                        <div className="flex flex-col flex-grow">
                                            <div className="text-gray-700"></div>
                                        </div>
                                    </div>
                                )}

                                <div ref={messagesEndRef} />


                                {/* Input area */}
                                <div className="flex justify-center left-0 align-middle w-full mx-auto bottom-6 fixed">
                                    <form onSubmit={handleSubmit} className="flex flex-row shadow-md bg-[#F5F5F5] rounded-xl justify-center w-full md:w-[830px] p-6">
                                        <button
                                            type="submit"
                                            className="text-white rounded-full h-10 w-10 justify-center flex items-center focus:outline-none"
                                            disabled={isLoading}
                                        >
                                            <img src={uploadFile} alt="File upload" />
                                        </button>

                                        <textarea
                                            value={inputValue}
                                            onChange={(e) => {
                                                const newValue = e.target.value;
                                                const newLines = newValue.split('\n').length;
                                                const maxLines = 3;
                                                const minHeight = 30;
                                                const lineHeight = 24;
                                                const newHeight = Math.min(newLines * lineHeight, maxLines * lineHeight);
                                                setInputValue(newValue);
                                                e.target.style.height = `${Math.max(newHeight, minHeight)}px`;
                                            }}

                                            onKeyDown={(e) => {
                                                if (e.key === 'Enter' && !e.shiftKey) {
                                                    handleSubmit(e);
                                                }
                                            }}
                                            className="flex-1 bg-[#F5F5F5] text-gray-700 focus:outline-none p-2 text-xl"
                                            placeholder="Type your message..."
                                            rows={1}
                                            style={{ resize: 'none', lineHeight: '24px', minHeight: '36px' }}
                                            disabled={isLoading}
                                        />

                                        {(abortControllerRef.current && isLoading) && (
                                            <button
                                                type="submit"
                                                onClick={(e) => handleAbort(e)}
                                                className="text-white rounded-full h-10 w-10 justify-center flex items-center focus:outline-none"
                                            >
                                                <div className="w-4 h-4 bg-black" />
                                            </button>
                                        )}
                                        {!abortControllerRef.current && (
                                            <button
                                                type="submit"
                                                className={`text-white rounded-full h-10 w-10 justify-center flex items-center focus:outline-none ${isLoading && 'cursor-not-allowed'}`}
                                            >
                                                {inputValue && !isLoading && <img src={sendMessage} className="w-4" alt="Send" />}
                                            </button>
                                        )}
                                    </form>
                                </div>
                            </div>

                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
};


export default MainChat;