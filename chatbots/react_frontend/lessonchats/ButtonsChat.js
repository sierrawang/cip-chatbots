// The buttons chat experience

import { getFunctions, httpsCallable } from "firebase/functions";
import { ChatWindow } from './ChatStyles';
import { ChatHeader } from "./ChatHeader";
import { useContext, useEffect, useRef, useState } from "react";
import { LessonContext } from "../LessonContext";
import { MessagesDisplay } from "./ChatStyles";
import { SimpleMessage } from "./SimpleMessage";
import { TypingAnimation } from "./TypingAnimation";
import styled from 'styled-components';
import { CHATBOT_NAME, ERROR_TOAST_DURATION, MESSAGES_LIMIT_MESSAGE, MESSAGE_LIMIT, CHAT_SERVICE_ERROR_MESSAGE, CHAT_ROLES } from "./ChatConstants";
import { errorToast } from "course/forum/components/forumGeneral";
import { ProfileContext } from "../../../contexts/ProfileContext";

const functions = getFunctions();
const explainDifferently = httpsCallable(functions, "explainDifferentlyEndpoint");
// const getSummary = httpsCallable(functions, "getSummary");
const whyItMatters = httpsCallable(functions, "whyItMatters");

const EXPLAIN_DIFFERENTLY_STR = "Explain it differently.";
// const GET_SUMMARY_STR = "What just happened?";
const WHY_IT_MATTERS_STR = "Why does it matter?";

export const ButtonsChat = () => {
    const { chatMessages, currSlideId, lessonData, getCurrentContent, setTempMessages, tempMessages, loadChat, chatType } = useContext(LessonContext);

    // Reference to the bottom of the messages display
    const messagesEndRef = useRef(null)

    // State to track whether the send button is enabled
    const [sendEnabled, setSendEnabled] = useState(true);

    const { userData } = useContext(ProfileContext);
    const userName = userData.displayName;

    // Reference to the messages display
    const messagesDisplayRef = useRef(null);

    // State to track whether we are loading more messages
    const [isLoadingMessages, setIsLoadingMessages] = useState(false);

    // Position from the bottom of the messages display - only used when loading more messages
    const [scrollPositionFromBottom, setScrollPositionFromBottom] = useState(0);

    // Scroll to the bottom of the messages display when the messages array changes
    useEffect(() => {
        if (!isLoadingMessages) {
            messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
        } else {
            adjustScrollPosition(scrollPositionFromBottom);
        }
    }, [chatMessages, tempMessages]);

    // Record the distance from the bottom of the messages display
    const recordScrollPosition = () => {
        const container = messagesDisplayRef.current;
        const position = container.scrollHeight - container.scrollTop - container.clientHeight;
        setScrollPositionFromBottom(position);
    };

    // Adjust the scroll position to maintain the same distance from the bottom
    const adjustScrollPosition = (scrollPositionFromBottom) => {
        const container = messagesDisplayRef.current;
        container.scrollTop = container.scrollHeight - container.clientHeight - scrollPositionFromBottom;
    };

    // Load more messages when the user scrolls to the top of the messages display
    const loadMoreMessages = async (e) => {
        const { scrollTop } = e.target;
        if (scrollTop === 0 && !isLoadingMessages) {
            setIsLoadingMessages(true);
            recordScrollPosition();
            await loadChat();
            setIsLoadingMessages(false);
        }
    }

    // Call the explain differently endpoint
    const callExplainDifferently = async () => {
        // Prevent multiple calls
        if (!sendEnabled) return;

        // Disable the send button until the message is sent
        setSendEnabled(false);

        // Get the current content that the user is looking at
        const currentContent = await getCurrentContent();

        try {
            setTempMessages([...tempMessages, { role: CHAT_ROLES.USER, content: EXPLAIN_DIFFERENTLY_STR }]);

            // Call the explain differently endpoint
            const res = await explainDifferently({
                aiName: CHATBOT_NAME,
                lessonId: lessonData.id,
                currSlideId: currSlideId,
                content: currentContent,
                userName: userName,
                query: EXPLAIN_DIFFERENTLY_STR
            });

            if (res.data === MESSAGE_LIMIT) {
                errorToast(MESSAGES_LIMIT_MESSAGE, ERROR_TOAST_DURATION);
            }
        } catch (error) {
            errorToast(CHAT_SERVICE_ERROR_MESSAGE, ERROR_TOAST_DURATION);
        }

        setSendEnabled(true);
    }

    // Call the get summary endpoint
    // const callGetSummary = async () => {
    //     // Prevent multiple calls
    //     if (!sendEnabled) return;

    //     // Disable the send button until the message is sent
    //     setSendEnabled(false);

    //     // Get the current content that the user is looking at
    //     const currentContent = await getCurrentContent();

    //     try {
    //         setTempMessages([...tempMessages, { role: CHAT_ROLES.USER, content: GET_SUMMARY_STR }]);

    //         // Call the get summary endpoint
    //         const res = await getSummary({
    //             aiName: CHATBOT_NAME,
    //             lessonId: lessonData.id,
    //             currSlideId: currSlideId,
    //             content: currentContent,
    //             userName: userName,
    //             query: GET_SUMMARY_STR
    //         });

    //         if (res.data === MESSAGE_LIMIT) {
    //             errorToast(MESSAGES_LIMIT_MESSAGE, ERROR_TOAST_DURATION);
    //         }
    //     } catch (error) {
    //         errorToast(CHAT_SERVICE_ERROR_MESSAGE, ERROR_TOAST_DURATION);
    //     }

    //     setSendEnabled(true);
    // }

    const callWhyItMatters = async () => {
        // Prevent multiple calls
        if (!sendEnabled) return;

        // Disable the send button until the message is sent
        setSendEnabled(false);

        // Get the current content that the user is looking at
        const currentContent = await getCurrentContent();

        try {
            setTempMessages([...tempMessages, { role: CHAT_ROLES.USER, content: WHY_IT_MATTERS_STR }]);

            // Call the get summary endpoint
            const res = await whyItMatters({
                aiName: CHATBOT_NAME,
                lessonId: lessonData.id,
                currSlideId: currSlideId,
                content: currentContent,
                userName: userName,
                query: WHY_IT_MATTERS_STR
            });

            if (res.data === MESSAGE_LIMIT) {
                errorToast(MESSAGES_LIMIT_MESSAGE, ERROR_TOAST_DURATION);
            }
        } catch (error) {
            errorToast(CHAT_SERVICE_ERROR_MESSAGE, ERROR_TOAST_DURATION);
        }

        setSendEnabled(true);
    }

    return (
        <ChatWindow>
            <ChatHeader />
            <MessagesDisplay
                ref={messagesDisplayRef}
                onScroll={loadMoreMessages}>
                {[...chatMessages].reverse().map((message, index) => (
                    <SimpleMessage
                        key={message.id}
                        message={message}
                        chatType={chatType}
                        chatMessages={chatMessages} />
                ))}
                {[...tempMessages].map((message, index) => (
                    <SimpleMessage
                        key={index + "temp-message"}
                        message={message}
                        chatType={chatType}
                        chatMessages={chatMessages} />
                ))}
                {!sendEnabled && <TypingAnimation />}
                <div ref={messagesEndRef} />
            </MessagesDisplay>
            <ButtonsContainer>
                <AIButton onClick={() => callExplainDifferently()}>{EXPLAIN_DIFFERENTLY_STR}</AIButton>
                <AIButton onClick={() => callWhyItMatters()}>{WHY_IT_MATTERS_STR}</AIButton>
            </ButtonsContainer>
        </ChatWindow>
    );
};

const ButtonsContainer = styled.div`
    display: flex;
    justify-content: space-between;
    padding: 5px;
    background-color: white;
    border-top: 1px solid #e0e0e0;
`;

const AIButton = styled.button`
    background-color: #e84393;
    color: white;
    padding: 10px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    width: 100%;
    margin: 5px;
    &:hover {
        background-color: #d63069;
    }
`;