import React, { useCallback, useEffect } from 'react';
import sidebarIcon from '../assets/sidebar.png';
import { logoutUser } from '../features/auth/authSlice';
import { useNavigate } from 'react-router-dom';
import { baseURL } from '../service';
import { useAppDispatch, useAppSelector } from '../hooks';
import { AppDispatch, RootState } from '../store';
import { MessageResponse, setChat } from '../features/chat/chatSlice';

interface SideMenuProps {
    selectedChatService: 'ollama' | 'bedrock';
    handleSelectedChatService: (event: React.ChangeEvent<HTMLSelectElement>) => void;
    isOpen: boolean;
    toggleMenu: () => void;
    className?: string; // Add className prop
}

const SideMenu: React.FC<SideMenuProps> = ({ selectedChatService, handleSelectedChatService, isOpen, toggleMenu }) => {
    const navigate = useNavigate()
    const dispatch: AppDispatch = useAppDispatch();
    const { auth: { user }, chat } = useAppSelector((select: RootState) => select)

    const fetchUserChats = useCallback(async () => {
        try {
            const response = await fetch(`${baseURL}/chats`, {
                headers: {
                    'Content-Type': 'application/json',  // Fixed typo here
                    'Authorization': `Bearer ${user?.access_token as string}`
                }
            })

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const fetchedChats: MessageResponse[] = await response.json();
            dispatch(setChat(fetchedChats))

        } catch (e) {
            throw Error(`Something happened: ${e}`)
        }
    }, [dispatch, user?.access_token])

    useEffect(() => {
        fetchUserChats()
    }, [fetchUserChats])

    const logUserOut = () => {
        dispatch(logoutUser())
        navigate('/')
    }

    return (
        <div className={`fixed z-50 h-screen flex p-4 sidebar-transition`}>
            {/* Collapsed Stripe */}
            <div className={`h-full  border-r border-[#d9d9d9] transition-all duration-300 ease-in-out ${isOpen ? 'w-64' : 'w-12'}`}>
                {/* Toggle Button - Always visible */}
                <div className="p-2 cursor-pointer hover:bg-gray-200 transition-colors" onClick={toggleMenu}>
                    <img
                        src={sidebarIcon}
                        alt="Toggle Sidebar"
                        className="w-8 h-8 float-end"
                    />
                </div>

                {isOpen && (
                    <nav className="overflow-y-auto h-[calc(100vh-4rem)] pt-4">
                        <div className="flex-1 overflow-hidden">
                            {/* LLM Selection */}
                            <div>
                                <label>Select LLM Service</label>
                                <select
                                    value={selectedChatService}
                                    onChange={handleSelectedChatService}
                                    className="bg-white border border-gray-200 p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 my-2 rounded-md w-full"
                                >
                                    <option value="ollama">Ollama</option>
                                </select>
                            </div>

                            {/* Scrollable Chat History */}
                            <div className="mt-4 h-[calc(100vh-200px)]">  {/* Adjusted height calculation */}
                                <div className='mb-4'>Today</div>
                                <div className="overflow-y-auto h-full pr-2">  {/* Added scroll container */}
                                    {chat.chat ? chat.chat.map((m: MessageResponse) => (
                                        <div
                                            key={m.id}
                                            className='p-2 mb-2 bg-gray-100 hover:bg-gray-200 rounded-md cursor-pointer text-gray-600 truncate'
                                            onClick={() => navigate(`/o/chat/${m.id}`)}
                                        >
                                            {m?.title || 'Untitled Chat'}
                                        </div>
                                    )) : (
                                        <div className="text-gray-500">No chat history</div>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Logout Button */}
                        <div className="text-sm font-bold mb-10 cursor-pointer hover:text-blue-600 mt-10" onClick={logUserOut}>
                            Log out
                        </div>
                    </nav>
                )}
            </div>
        </div>
    );
};

export default SideMenu;