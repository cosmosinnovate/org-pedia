
// Should be able to log in using google button. 
// Center the button and add a title that says. C
const AccountAccess =() => {
    return <div className="flex md:flex-row flex-col">
        <div className="flex flex-1 h-screen bg-black text-white justify-center mx-auto items-center my-auto">
            <div className="p-4 flex text-center text-4xl text-white w-full justify-center md:w-[500px]">
                Welcome to Org//Pedia: LLM privacy that meets your private IP
                </div>
        </div>
        <div className="flex flex-1 h-screen justify-center mx-auto items-center my-auto">
            <div className="flex flex-col p-4 w-full items-center space-y-6">
                <label className="font-bold font-['poppins'] text-2xl">Access account</label>

                <button className="flex text-center text-xl rounded-xl bg-blue-300 text-white p-4 w-full md:w-[400px] justify-center">
                    Continue with Google
                </button>

                <a href="/chat" className="flex cursor-pointer text-center text-xl rounded-xl bg-blue-300 text-white p-4 w-full md:w-[400px] justify-center">
                    Continue as Guest
                </a>
            </div>
            
        </div>
    </div>
}


export default AccountAccess;