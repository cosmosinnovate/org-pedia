import { FC } from "react";
import { Message } from "../features/chat/chatSlice";

interface CallToActionItemsProps {
    messages: Message[];
    handleSubmitCustom: (messageContent: string) => void
}


const CallToActionItems: FC<CallToActionItemsProps> = ({ messages, handleSubmitCustom }) => {
    return <div className={`text-black md:w-[900px] p-4  ${messages.length > 0 ? 'hidden' : 'block'} flex flex-col justify-center my-auto mx-auto w-full font-semibold text-2xl mt-10`}>
        <div className="text-black font-medium text-2xl mb-4">For Executive</div>
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


export default CallToActionItems