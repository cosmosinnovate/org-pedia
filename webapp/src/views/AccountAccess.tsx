import { GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import { useAppDispatch } from "../hooks";
import { setUser } from "../features/auth/authSlice";
import { useNavigate } from "react-router-dom";
import { auth } from "../firebaseConfig"; // Import your firebase configuration
import { baseURL } from "../service";


// Should be able to log in using google button. 
// Center the button and add a title that says. C
// import { useEffect, useState } from 'react';

const AccountAccess = () => {
    const dispatch = useAppDispatch();
    const navigate = useNavigate()
    const provider = new GoogleAuthProvider();


    const signInAsGuest = () => {
        dispatch(setUser(null)); // Optionally, you might want to clear the user state
        navigate("/chat");
    };

    const signInWithGoogle = async () => {
        try {
            const result = await signInWithPopup(auth, provider);

            // Get the Google Access Token and user info
            const credential = GoogleAuthProvider.credentialFromResult(result);
            const token = credential?.accessToken;
            const user = result.user;

            const userData = {
                user_id: user.uid,
                display_name: user.displayName,
                email: user.email,
                photo_url: user.photoURL,
                access_token: token
            };

            // Make a request to your backend API to create or retrieve the user
            const response = await fetch(`${baseURL}/auth`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData),
            });

            const data = await response.json();
            console.log(data)

            if (response.ok) {
                // User created or retrieved successfully
                console.log(data);
                // Dispatch the user information to Redux
                dispatch(setUser(data.user));
                // Navigate to the chat page
                navigate("/chat");
            } else {
                // Handle error
                console.error('Error during sign-in:', data.error);
            }

        } catch (error) {
            console.error("Error during sign-in:", error);
        }
    };

    return (
        <div className="flex md:flex-row flex-col w-full">
            <div className="absolute top-0 right-0 w-[60px] h-[10px] bg-blue-500 skew-y-[45deg] translate-x-1/6 -translate-y-1/2"></div>
            <div className="absolute top-2 right-0.5 w-[10px] h-[10px] bg-blue-500 skew-y-[45deg] translate-x-1/6 -translate-y-1/2"></div>

            <div className="flex md:flex-1 h-screen bg-black text-white justify-center mx-auto items-center my-auto">
                <div className="p-4 flex text-center text-4xl text-white w-full justify-center md:w-[500px]">
                    Welcome to Org//Pedia
                </div>
            </div>

            <div className="flex md:flex-1  h-screen justify-center mx-auto items-center my-auto">
                <div className="flex flex-col p-4 w-full items-center space-y-6">
                    <label className="font-bold font-['poppins'] text-2xl">Access account</label>

                    <button className="flex font-semibold text-center text-xl rounded-xl bg-blue-500 text-gray-50 p-4 w-full md:w-[400px] justify-center" onClick={signInWithGoogle}
                    >
                        Continue with Google
                    </button>

                    <button className="flex font-semibold cursor-pointer text-center text-xl rounded-xl bg-gray-300 text-black p-4 w-full md:w-[400px] justify-center"
                        onClick={signInAsGuest}>
                        Continue as Guest
                    </button>
                </div>

            </div>
        </div>)
}

export default AccountAccess;