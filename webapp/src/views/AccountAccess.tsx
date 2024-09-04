import { GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import { useAppDispatch } from "../hooks";
import { setUser } from "../features/auth/authSlice";
import { useNavigate } from "react-router-dom";
import { auth } from "../firebaseConfig"; // Import your firebase configuration


// Should be able to log in using google button. 
// Center the button and add a title that says. C
// import { useEffect, useState } from 'react';

const AccountAccess = () => {
    const dispatch = useAppDispatch();
    const navigate = useNavigate()
    const provider = new GoogleAuthProvider();


    const signInAsGuest = () => {
        // Handle guest login logic here
        // You might want to set some default user state or redirect without setting user information
        // dispatch(setUser(null)); // Optionally, you might want to clear the user state
        navigate("/chat");
    };


    const signInWithGoogle = async () => {
        try {
            const result = await signInWithPopup(auth, provider);

            // Get the Google Access Token and user info
            const credential = GoogleAuthProvider.credentialFromResult(result);
            const token = credential?.accessToken;
            console.log(token)
            const user = result.user;

            // Dispatch the user information to Redux
            dispatch(setUser(user));

            // Navigate to the chat page
            navigate("/chat");

        } catch (error) {
            console.error("Error during sign-in:", error);
        }
    };

    return (
        <div className="flex md:flex-row flex-col w-full">
            <div className="flex md:flex-1 h-screen bg-black text-white justify-center mx-auto items-center my-auto">
                <div className="p-4 flex text-center text-4xl text-white w-full justify-center md:w-[500px]">
                    Welcome to Org//Pedia: LLM privacy that meets your private IP
                </div>
            </div>

            <div className="flex md:flex-1  h-screen justify-center mx-auto items-center my-auto">
                <div className="flex flex-col p-4 w-full items-center space-y-6">
                    <label className="font-bold font-['poppins'] text-2xl">Access account</label>

                    <button className="flex text-center text-xl rounded-xl bg-blue-300 text-white p-4 w-full md:w-[400px] justify-center" onClick={signInWithGoogle}
                    >
                        Continue with Google
                    </button>

                    <button className="flex cursor-pointer text-center text-xl rounded-xl bg-blue-300 text-white p-4 w-full md:w-[400px] justify-center"
                    onClick={signInAsGuest}>
                        Continue as Guest
                    </button>
                </div>

            </div>
        </div>)
}

export default AccountAccess;