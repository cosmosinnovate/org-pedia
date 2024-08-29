import { ToastContainer } from 'react-toastify';
import ChatComponent from './views/ChatComponent';

function App() {
  return (
        <div>
           <ToastContainer
                position="top-right"
                autoClose={5000}
                hideProgressBar={false}
                newestOnTop={false}
                closeOnClick
                rtl={false}
                pauseOnFocusLoss
                draggable
                pauseOnHover
                className="z-50"
            />
          <ChatComponent/>
    </div>
  );
}

export default App
