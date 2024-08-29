import React, { CSSProperties, FC, useEffect, useRef, useState } from 'react';
import ReactMarkdown, { Components } from 'react-markdown';
import { Prism as SyntaxHighlighter, SyntaxHighlighterProps } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/cjs/styles/prism'
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css'; // Import the CSS for styling
import SideMenu from '../component/SideMenu';
import userAssistant from '../assets/userAssistant.png';
import uploadFile from '../assets/load-file.png';
import sendMessage from '../assets/send-message.png';

/**
 * 
 * import React from 'react';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { CopyToClipboard } from 'react-copy-to-clipboard';

const syntaxStyle = {
  // your style configuration here...
};

interface CodeBlockProps extends React.ComponentProps<typeof SyntaxHighlighter> {
  className?: string;
}

const CodeBlock: React.FC<CodeBlockProps> = ({ className, children, ...props }) => {
  const match = /language-(\w+)/.exec(className || '');
  return (
    <div class="flex">
      <SyntaxHighlighter
        style={syntaxStyle}
        language={match[1]}
        PreTag="div"
        {...props}
      >
        {String(children).replace(/\n$/, '')}
      </SyntaxHighlighter>
      <CopyButton children={children} />
    </div>
  );
};

interface CopyButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children?: string;
}

const CopyButton: React.FC<CopyButtonProps> = ({ children }) => {
  const [copied, setCopied] = React.useState(false);

  return (
    <button
      type="button"
      class={`${
        copied ? 'bg-green-500 hover:bg-green-700' : 'bg-gray-200 hover:bg-gray-300'
      } text-white px-4 py-2 rounded`}
      onClick={() => setCopied(true)}
    >
      {copied ? 'Copied!' : 'Copy'}
    </button>
  );
};

export default CodeBlock;
 */

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

const baseURL = "http://localhost:8000";

interface ChatMessagesProps {
    messages: Message[]
    markdownComponents: Components
}

const ChatComponent: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<null | HTMLDivElement>(null);
    const abortControllerRef = useRef<AbortController | null>(null);
    const [selectedChatService, setSelectedChatService] = useState<'ollama' | 'bedrock'>('ollama');
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    const syntaxStyle: SyntaxHighlighterProps['style'] | CSSProperties = oneDark;


    const toggleSidebar = () => {
        setIsSidebarOpen(!isSidebarOpen);
    };

    const handleSubmit = async (event?: React.FormEvent<HTMLFormElement | KeyboardEvent | HTMLTextAreaElement>, inputMessage?: string) => {
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
                    response = await fetch(`${baseURL}/ollama-chat`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ messages: [...messages, userMessage] }),
                        signal,
                    });
                    break;
                case 'bedrock':
                    response = await fetch(`${baseURL}/bedrock-chat`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
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
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        return () => {
            if (abortControllerRef.current) {
                abortControllerRef.current.abort();
            }
        };
    }, []);

    const markdownComponents: Components = {
        p: ({ children }) => <p className="mb-2">{children}</p>,
        h1: ({ children }) => <h1 className="text-2xl font-bold mb-2">{children}</h1>,
        h2: ({ children }) => <h2 className="text-xl font-bold mb-2">{children}</h2>,
        h3: ({ children }) => <h3 className="text-lg font-bold mb-2">{children}</h3>,
        ul: ({ children }) => <ul className="list-disc list-inside mb-2">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal list-inside mb-2">{children}</ol>,
        li: ({ children }) => <li className="mb-1">{children}</li>,

        code: ({ className, children, ...props }) => {
            const match = /language-(\w+)/.exec(className || '');
            return match ? (
                <SyntaxHighlighter
                    style={syntaxStyle}
                    language={match[1]}
                    PreTag="div"
                    {...props}
                >
                    {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
            ) : (
                <code className="my-2"
                    {...props}>

                </code>
            );
        },
        pre: ({ children }) => <pre className="rounded  whitespace-pre-wrap">{children}</pre>,
        a: ({ href, children }) => <a href={href} className="text-blue-600 hover:underline">{children}</a>,
        blockquote: ({ children }) => <blockquote className="border-l-4 border-gray-300 pl-4 italic my-2">{children}</blockquote>,
        hr: () => <hr className="my-4 border-t border-gray-300" />,
        img: ({ src, alt }) => <img src={src} alt={alt} className="max-w-full h-auto my-2" />,
        table: ({ children }) => <table className="table-auto border-collapse my-2">{children}</table>,
        th: ({ children }) => <th className="border border-gray-300 px-4 py-2 font-bold">{children}</th>,
        td: ({ children }) => <td className="border border-gray-300 px-4 py-2">{children}</td>,
    };

    const handleSelectedChatService = (event: React.ChangeEvent<HTMLSelectElement>) => {
        setSelectedChatService(event.target.value as 'ollama' | 'bedrock');
    };

    const handleSubmitCustom = (messageContent: string) => {
        handleSubmit(undefined, messageContent);
    };


    return (
        <div className="flex flex-col h-screen bg-[#f5f6f7]  transition-all duration-300 overflow-y-auto">

            <div className="flex-1 flex flex-col md:flex-row">
                {/* Takes the left side */}
                <SideMenu
                    selectedChatService={selectedChatService}
                    handleSelectedChatService={handleSelectedChatService}
                    isOpen={isSidebarOpen}
                    toggleMenu={toggleSidebar}
                />

                {/* Takes the right full side */}
                <main className={`flex flex-col w-full items-center mx-auto space-y-10 overflow-y-auto my-auto justify-center transition-all duration-300 ease-in-out mt-10`}>

                    <div className="flex w-full flex-col">
                        <div className={`flex justify-center text-[32px] ${messages.length > 0 ? 'hidden' : 'block'}  mx-auto`}>
                            <span className="text-[#fa6f73]  font-['poppins'] font-bold">Org</span>
                            <span className="text-[#a1b3ff]  font-extrabold font-['poppins']">//</span>
                            <span className="text-[#a1b3ff]  font-bold ">Pedia</span>
                        </div>

                        <div className={`font-semibold text-[32px] text-center ${messages.length > 0 ? 'hidden' : 'block'} `}>Unlocking the Potential of Organizational Wisdom</div>

                        {/* Fix this to show columns cleanly on small devices */}

                        <CallToActionItems messages={messages} handleSubmitCustom={handleSubmitCustom} />

                        <div className={`flex flex-1 w-full md:w-[900px] mx-auto pb-20 overflow-hidden`}>
                            <div className="flex  flex-col p-4 space-y-4 justify-items-end ">
                                <ChatMessages messages={messages} markdownComponents={markdownComponents} />
                                <div ref={messagesEndRef} />


                            </div>

                        </div>

                        <div className={`flex justify-center  left-0 align-middle w-full  mx-auto fixed bottom-0 p-4`}>
                            <form onSubmit={handleSubmit} className="flex flex-row shadow-md bg-white rounded-2xl justify-center w-full  md:w-[900px] p-4">
                                <button
                                    type="submit"
                                    className={`text-white rounded-full h-10 w-10 justify-center flex items-center focus:outline-none  ${isLoading
                                        ? 'bg-gray-400 cursor-not-allowed'
                                        : ' hover:bg-gray-200'
                                        }`}
                                    disabled={isLoading}
                                >
                                    <img src={uploadFile} alt="File upload" />
                                </button>
                                <textarea
                                    value={inputValue}
                                    onChange={(e) => {
                                        const newValue = e.target.value;
                                        const newLines = newValue.split('\n').length;
                                        const maxLines = 5;
                                        const minHeight = 36;
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
                                    className="flex-1 bg-white text-gray-700 focus:outline-none p-2 text-2xl"
                                    placeholder="Type your message..."
                                    rows={1}
                                    style={{ resize: 'none', lineHeight: '24px', minHeight: '36px' }}
                                    disabled={isLoading}
                                />
                                <button
                                    type="submit"
                                    className={`text-white rounded-full h-10 w-10 justify-center flex items-center focus:outline-none  ${isLoading 
                                        ? ' bg-gray-400  cursor-not-allowed animate-spin mr-2'
                                        : ' hover:bg-gray-200'
                                        }`}
                                    disabled={isLoading}
                                >   
                                    {isLoading && <img src={sendMessage} className='w-4' />}
                                    {inputValue && <img src={sendMessage} className='w-4' />}
                                </button>
                            </form>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
};

export default ChatComponent;

interface CallToActionItemsProps {
    messages: Message[];
    handleSubmitCustom: (messageContent: string) => void
}


const ChatMessages: React.FC<ChatMessagesProps> = React.memo(({ messages, markdownComponents }) => {
    const messageListRef = useRef<HTMLDivElement>(null);

    const renderMessage = (message: Message, index: number) => (
        <div
            key={index}
            className={`flex flex-col ${message.role === 'user' ? 'justify-start' : 'justify-end'}`}
        >
            {message.role !== 'user' && (
                <div className='mb-4'>
                    <img src={userAssistant} alt="User" className="w-8 h-8 rounded-full"></img>
                </div>
            )}

            <div
                className={`p-3 ${message.role === 'user'
                    ? 'flex max-w-max bg-gray-200 text-black rounded-2xl top-0'
                    : 'bg-white text-gray-500 rounded-lg'
                    }`}
            >
                {message.role === 'user' ? (
                    message.content.replace(/\n/g, '\\n')
                ) : (
                    <ReactMarkdown components={markdownComponents}>{message.content}</ReactMarkdown>
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

const CallToActionItems: FC<CallToActionItemsProps> = ({ messages, handleSubmitCustom }) => {

    return <div className={`text-black md:w-[900px] p-4  ${messages.length > 0 ? 'hidden' : 'block'} flex flex-col justify-center my-auto mx-auto w-full font-semibold text-2xl mt-10`}>
        {/* Section for Executives */}
        <div className="text-black font-medium text-2xl mb-4">For Executive</div>

        {/* Section for Employees */}
        <div className="flex flex-col md:flex-row gap-4 w-full justify-around font-bold ">
            <button
                className="w-full p-4 md:p-10  text-2xl shadow flex flex-col justify-around items-center rounded-[10px] border border-black h-[102px]"
                onClick={() => handleSubmitCustom('Market Trends and Competitive Analysis: AI use case in organization lost knowledge due to employee getting fired or quitting and its impact on long growth to the organzation')}
            >
                <div className="text-black text-sm text-center">Market Trends and Competitive Analysis</div>
            </button>
            <button
                className="w-full p-4 md:p-10 shadow flex flex-col justify-around items-center rounded-[10px] border border-black h-[102px]"
                onClick={() => handleSubmitCustom('Strategic Goals and Business Objectives')}
            >
                <div className="text-black text-sm text-center">Strategic Goals and Business Objectives</div>
            </button>
            <button
                className="w-full p-4 md:p-10 shadow flex flex-col justify-around items-center rounded-[10px] border border-black h-[102px]"
                onClick={() => handleSubmitCustom('Organizational Structure and Key Team Profiles')}
            >
                <div className="text-black text-sm text-center">Organizational Structure and Key Team Profiles</div>
            </button>
        </div>
    </div>;
}

