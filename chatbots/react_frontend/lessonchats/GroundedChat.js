// The RAG chat experience

import { SimpleChatView } from "./SimpleChatView";
import { getFunctions, httpsCallable } from "firebase/functions";
import { useState, useContext } from "react";
import { LessonContext } from "../LessonContext";
import { ProfileContext } from '../../../contexts/ProfileContext';
import { CHATBOT_NAME, CHAT_ROLES, CHAT_SERVICE_ERROR_MESSAGE, MESSAGE_LIMIT, MESSAGES_LIMIT_MESSAGE, ERROR_TOAST_DURATION, isPersonified } from "./ChatConstants";
import { errorToast } from "course/forum/components/forumGeneral";

const functions = getFunctions();
const groundedChatEndpointNEW = httpsCallable(functions, "groundedChatEndpointNEW");

export const GroundedChat = () => {

    const [sendEnabled, setSendEnabled] = useState(true);
    const [currentMessage, setCurrentMessage] = useState("");

    const { chatMessages, lessonData, currSlideId, tempMessages, setTempMessages, getCurrentContent, chatType } = useContext(LessonContext);

    const { userData } = useContext(ProfileContext);
    const userName = userData.displayName;

    const sendMessage = async () => {
        // If send is disabled, don't send the message
        if (!sendEnabled) {
            return;
        }

        // Disable the send button until the message is sent
        setSendEnabled(false);

        // Grab the current message
        const query = currentMessage;

        // If the user didn't type anything, don't send the message
        if (query === "") {
            return;
        }

        // Clear the input field
        setCurrentMessage("")

        // Add the message to the tempMessages array so that it appears immediately
        setTempMessages([...tempMessages, { role: CHAT_ROLES.USER, content: query }]);

        const currContent = await getCurrentContent();

        try {
            // Send the message to the backend
            const res = await groundedChatEndpointNEW({
                chatMessages: chatMessages,
                query: query,
                lessonId: lessonData.id,
                currSlideId: currSlideId,
                userName: userName,
                aiName: CHATBOT_NAME,
                currContent: currContent,
                isPersonified: isPersonified(chatType)
            });

            if (res.data === MESSAGE_LIMIT) {
                errorToast(MESSAGES_LIMIT_MESSAGE, ERROR_TOAST_DURATION);
            }
        } catch (error) {
            errorToast(CHAT_SERVICE_ERROR_MESSAGE, ERROR_TOAST_DURATION);
        }

        // Enable the send button
        setSendEnabled(true);
    }


    return (
        <SimpleChatView
            sendMessage={sendMessage}
            currentMessage={currentMessage}
            setCurrentMessage={setCurrentMessage}
            sendEnabled={sendEnabled}
        />
    );
};