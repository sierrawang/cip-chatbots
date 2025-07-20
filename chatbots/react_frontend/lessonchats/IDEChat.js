// The IDE Chat experience.

import { MessagesDisplay } from "./ChatStyles";
import { IDEContext } from "../../../ide/contexts/IDEContext";
import { useContext, useState, useRef, useEffect } from "react";
import { SimpleMessage } from "./SimpleMessage";
import { MessageInputArea } from "./MessageInputArea";
import { getFunctions, httpsCallable } from "firebase/functions";
import { CHATBOT_NAME, CHAT_ROLES, MESSAGE_LIMIT, MESSAGES_LIMIT_MESSAGE, CHAT_SERVICE_ERROR_MESSAGE, ERROR_TOAST_DURATION, isPersonified } from "./ChatConstants";
import { ProfileContext } from '../../../contexts/ProfileContext';
import { LeftColTitle } from "ide/LeftCol";
import { TypingAnimation } from "./TypingAnimation";
import { useParams } from "react-router";
import styled from 'styled-components';
import { errorToast } from 'course/forum/components/forumGeneral';
import { parseTipTap } from "./TipTapParser";

const functions = getFunctions();
const ideChatEndpointNEW = httpsCallable(functions, "ideChatEndpointNEW");

export const IDEChat = ({ bottomBarRef }) => {

    const { chatMessages, tempMessages, setTempMessages, loadChat, chatType, codeToRun, projectData, assnData } = useContext(IDEContext);
    const { userData } = useContext(ProfileContext);

    const userName = userData.displayName;

    const [currentMessage, setCurrentMessage] = useState("");
    const [sendEnabled, setSendEnabled] = useState(true);

    // Get the assignment id from the URL
    const { urlKey } = useParams();

    // Reference to the bottom of the messages display
    const messagesEndRef = useRef(null);

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

    // Calculate the height of the bottom nav bar
    // This is only necessary for mobile view, and should have no effect on desktop view
    const [bottomBarHeight, setBottomBarHeight] = useState(0);
    useEffect(() => {
        if (bottomBarRef) {
            const updateBottomBarHeight = () => {
                if (bottomBarRef.current) {
                    setBottomBarHeight(bottomBarRef.current.offsetHeight);
                    console.log('bottomBarRef.current.offsetHeight', bottomBarRef.current.offsetHeight)
                }
            };
            updateBottomBarHeight();
            window.addEventListener('resize', updateBottomBarHeight);
            return () => window.removeEventListener('resize', updateBottomBarHeight);
        }
    }, [bottomBarRef]);

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

        // Add the message to the tempMessages array
        setTempMessages([...tempMessages, { role: CHAT_ROLES.USER, content: query }]);

        try {
            // Grab the current content
            const code = codeToRun?.current;
            const prompt = parseTipTap(assnData?.prompt?.content);

            // Send the message to the backend
            const res = await ideChatEndpointNEW({
                chatMessages: chatMessages,
                query: query,
                assnId: urlKey,
                userName: userName,
                aiName: CHATBOT_NAME,
                code: code,
                assnPrompt: prompt,
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
        <IDEChatWindow bottomBarHeight={bottomBarHeight}>
            <div style={{ borderBottom: "1px solid #ccc" }}>
                <LeftColTitle title="Chat" />
            </div>
            <MessagesDisplay
                ref={messagesDisplayRef}
                onScroll={loadMoreMessages}>
                {[...chatMessages].reverse().map((message, index) => (
                    <SimpleMessage
                        key={message.id}
                        message={message}
                        chatType={chatType}
                        chatMessages={chatMessages}
                    />
                ))}
                {[...tempMessages].map((message, index) => (
                    <SimpleMessage
                        key={index + "temp-message"}
                        message={message}
                        chatType={chatType}
                        chatMessages={chatMessages}
                    />
                ))}
                {!sendEnabled && <TypingAnimation />}
                <div ref={messagesEndRef} />
            </MessagesDisplay>
            <MessageInputArea
                currentMessage={currentMessage}
                setCurrentMessage={setCurrentMessage}
                sendMessage={sendMessage} />
        </IDEChatWindow>
    );
};

const IDEChatWindow = styled.div`
    background-color: white;
    // Subtract the heights of the bottom bar and the top bar
    height: calc(100vh - ${props => props.bottomBarHeight}px - 55px);
    display: flex;
    flex-direction: column;
    position: relative;
    overflow-y: hidden;
`;
