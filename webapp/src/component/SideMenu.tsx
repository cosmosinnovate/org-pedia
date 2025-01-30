import React, { useCallback, useEffect } from 'react';
import sidebarIcon from '../assets/sidebar.png';
import { logoutUser } from '../features/auth/authSlice';
import { useNavigate, useLocation } from 'react-router-dom';
import { baseURL } from '../service';
import { useAppDispatch, useAppSelector } from '../hooks';
import { AppDispatch, RootState } from '../store';
import { MessageResponse, setChat } from '../features/chat/chatSlice';
import { LLMModels } from '../util/model';

interface SideMenuProps {
    selectedLLM: LLMModels;
    handleSelectedLLM: (event: React.ChangeEvent<HTMLSelectElement>) => void;
    isOpen: boolean;
    toggleMenu: () => void;
}

const SideMenu: React.FC<SideMenuProps> = ({ selectedLLM, handleSelectedLLM, isOpen, toggleMenu }) => {
    const navigate = useNavigate()
    const dispatch: AppDispatch = useAppDispatch();
    const { auth: { user }, chat } = useAppSelector((select: RootState) => select)
    const location = useLocation()

    const fetchUserChats = useCallback(async () => {
        try {
            const response = await fetch(`${baseURL}/chats`,
                {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'applicatIon/json',
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
        <div className={`fixed inset-y-0 left-0 transform ${isOpen ? 'translate-x-0' : '-translate-x-full'} transition-transform duration-300 ease-in-out bg-gray-800 text-white w-64 z-50`}>
            <div className="flex flex-col h-full">
                {/* Header */}
                <div className="p-4 border-b border-gray-700">
                    <div className="flex items-center justify-between">
                        <h2 className="text-xl font-semibold">Chats</h2>
                        <button onClick={toggleMenu} className="p-2">
                            <img src={sidebarIcon} alt="sidebar" className="w-6 h-6" />
                        </button>
                    </div>
                </div>

                {/* Model Selection */}
                <div className="p-4 border-b border-gray-700">
                    <select
                        value={selectedLLM}
                        onChange={handleSelectedLLM}
                        className="w-full p-2 bg-gray-700 rounded text-white"
                    >
                        <option value="LLama3.2">LLama 3.2</option>
                        <option value="GPT4">GPT-4</option>
                    </select>
                </div>

                {/* Chat List - Scrollable */}
                <div className="flex-1 overflow-y-auto">
                    <div className="space-y-2 p-4">
                        {chat.chat.map((chatItem) => (
                            <button
                                key={chatItem.id}
                                onClick={() => navigate(`/c/${chatItem.id}`)}
                                className={`w-full text-left p-3 rounded-lg transition-colors duration-200 hover:bg-gray-700
                                    ${location.pathname === `/c/${chatItem.id}` ? 'bg-gray-700' : 'bg-gray-800'}`}
                            >
                                <div className="truncate text-sm">
                                    {chatItem.title || 'Untitled Chat'}
                                </div>
                                {location.pathname === `/c/${chatItem.id}` && (
                                    <div className="text-xs text-gray-400 mt-1">
                                        ID: {chatItem.id}
                                    </div>
                                )}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-gray-700">
                    <button
                        onClick={logUserOut}
                        className="w-full py-2 px-4 bg-red-600 text-white rounded hover:bg-red-700 transition-colors duration-200"
                    >
                        Logout
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SideMenu;
