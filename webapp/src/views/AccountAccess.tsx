import { GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import { useAppDispatch } from "../hooks";
import { setUser, User } from "../features/auth/authSlice";
import { useNavigate } from "react-router-dom";
import { auth } from "../firebaseConfig"; // Import your firebase configuration
import { baseURL } from "../service";


const AccountAccess = () => {
    const dispatch = useAppDispatch();
    const navigate = useNavigate()
    const provider = new GoogleAuthProvider();

    const signInWithGoogle = async () => {
        try {
            const result = await signInWithPopup(auth, provider);
            const credential = GoogleAuthProvider.credentialFromResult(result);
            const token = credential?.accessToken;
            const user = result.user;

            const userData = {
                user_google_id: user.uid,
                display_name: user.displayName,
                email: user.email,
                photo_url: user.photoURL,
                access_token: token
            };

            const response = await fetch(`${baseURL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData),
            });

            const data = await response.json();
            if (response.ok) {
                console.log(data);
                const user: User = {
                    id: data.user.id,
                    email: data.user.email,
                    photo_url: data.user.photo_url,
                    exp: data.user.exp,
                    display_name: data.user.display_name,
                    access_token: data.user.access_token,
                    user_google_id: data.user.user_google_id,
                }
                dispatch(setUser(user));
                localStorage.setItem('access_token', data.access_token as string);
                navigate("/", {replace: true});
            } else {
                console.error('Error during sign-in:', data.error);
            }

        } catch (error) {
            console.error("Error during sign-in:", error);
        }
    };

    return (
        <div className="flex md:flex-row flex-col w-full h-screen">
            <div className="fixed top-0 right-0 w-[60px] h-[10px] bg-blue-500 skew-y-[45deg] translate-x-1/6 -translate-y-1/2"></div>
            <div className="fixed top-2 right-0.5 w-[10px] h-[10px] bg-blue-500 skew-y-[45deg] translate-x-1/6 -translate-y-1/2"></div>
            <div className="flex flex-col bg-gradient-to-b from-[#edf0ff] to-[#f0c6c6] h-full md:h-screen w-full md:flex-1  text-black justify-center mx-auto items-center my-auto">

            <div className={`flex justify-center text-[32px]  'block'}  mx-auto`}>
              <span className="text-[#fa6f73]  font-bold">Org</span>
              <span className="text-[#a1b3ff]  font-extrabold ">//\</span>
              <span className="text-[#a1b3ff]  font-bold ">Pedia</span>
            </div>
                <div className="p-4 font-['Inter'] font flex text-center text-6xl  w-full justify-center font-bold">
                    Clear data is key to not wasting time!
                </div>
            </div>

            <div className="flex w-full h-full md:h-screen b md:flex-1 justify-center mx-auto items-center my-auto">
                <div className="flex flex-col p-4 w-full items-center space-y-6">
                    <label className="font-bold font-['inter'] text-2xl">Want clear decision making?</label>
                    <button className="flex font-['inter'] font-medium text-center text-xl rounded-lg bg-blue-500 text-gray-50 p-4 w-full md:w-[400px] justify-center" onClick={signInWithGoogle}
                    >
                        Continue with Google
                    </button>

                </div>

            </div>
        </div>)
}

export default AccountAccess;