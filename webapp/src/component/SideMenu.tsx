import React from 'react';
import sidebarIcon from '../assets/sidebar.png';
import { useDispatch } from 'react-redux';
import { logoutUser } from '../features/auth/authSlice';
import { useNavigate } from 'react-router-dom';

interface SideMenuProps {
  selectedChatService: 'ollama' | 'bedrock';
  handleSelectedChatService: (event: React.ChangeEvent<HTMLSelectElement>) => void;
  isOpen: boolean;
  toggleMenu: () => void;
}

const SideMenu: React.FC<SideMenuProps> = ({ selectedChatService, handleSelectedChatService, isOpen, toggleMenu }) => {
  const navigate = useNavigate()
  const dispatch = useDispatch()

  const logUserOut = () => {
    dispatch(logoutUser())
    navigate('/')
  }

  return (
    <div className="fixed z-50">
      {/* Sidebar Icon - Always visible */}
      <div className={`fixed top-0 left-0 ml-4 mt-4  cursor-pointer  ${isOpen ? 'hidden' : 'bock'}`} onClick={toggleMenu}>
        <img src={sidebarIcon} alt="Sidebar Icon" className="w-8 h-8" />
      </div>

      {/* Sidebar - Visible only on medium screens and above */}
      <div className={`h-screen pt-4 bg-gray-50 border-r border-[#d9d9d9] transition-all duration-300 ease-in-out flex-shrink-0 ${isOpen ? 'block w-64' : 'hidden'
          }`}>

        <div className={`top-0 left-0 ml-4   cursor-pointer "`} onClick={toggleMenu}>
          <img src={sidebarIcon} alt="Sidebar Icon" className="w-8 h-8" />
        </div>

        {isOpen && (
          <nav className="flex flex-col p-4 justify-between h-full">
            <div>
              <div>
              <label className=''>Select LLM Service</label>
              <select
                value={selectedChatService}
                onChange={handleSelectedChatService}
                className="bg-white border border-gray-200 p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 my-2 rounded-md w-full"
                >
                <option value="bedrock">Bedrock</option>
                <option value="ollama">Ollama</option>
              </select>
                </div>

              <div className='mt-20'>
                <div>Today</div>

                <div>Previous search</div>
              </div>
            </div>


            <div className="text-sm font-bold mb-10 justify-start bottom-0 self-start cursor-pointer" onClick={logUserOut}>Log out</div>
          </nav>
        )}
      </div>
    </div>
  );
};

export default SideMenu;
