// The community chat experience

import { useEffect, useRef, useContext, useState } from 'react';
import { LessonContext } from "../LessonContext";
import styled from 'styled-components';
import { RepliableMessage } from './RepliableMessage';
import { ProfileContext } from '../../../contexts/ProfileContext';
import { MessageInputArea } from './MessageInputArea';
import { getFunctions, httpsCallable } from "firebase/functions";
import { FormattedMessage } from './FormattedMessage';
import { ChatHeader } from './ChatHeader';
import { ChatWindow, MessagesDisplay } from './ChatStyles';
import { CHATBOT_NAME, CHAT_SERVICE_ERROR_MESSAGE, FLAGGED_POST, FLAGGED_POST_MESSAGE, ERROR_TOAST_DURATION, CHAT_ROLES, MESSAGE_LIMIT, MESSAGES_LIMIT_MESSAGE, isPersonified } from './ChatConstants';
import { errorToast } from 'course/forum/components/forumGeneral';
import { RepliableMessageTemp } from './RepliableMessageTemp';

const functions = getFunctions();
// const communityChatEndpoint = httpsCallable(functions, "communityChatEndpoint");
const communityChatEndpointNEW = httpsCallable(functions, "communityChatEndpointNEW");

export const CommunityChat = () => {
    const { userData } = useContext(ProfileContext);
    const userName = userData.displayName;

    const { chatMessages, lessonData, currSlideId, tempMessages, setTempMessages, loadChat, chatType, getCurrentContent } = useContext(LessonContext);

    // Keep track of whether the user is replying to a message, or sending a new message
    const [replyTo, setReplyTo] = useState(null);
    const [currentMessage, setCurrentMessage] = useState("");

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

    // Construct and return an array of the chain of replies that lead to the given message.
    const constructMessages = (messageId) => {
        // Init the return array
        let messages = [];

        // Grab the specified message
        let currentMessage = chatMessages.find(message => message.id === messageId);

        while (currentMessage) {
            // Prepend the message to the array
            messages.unshift({ role: currentMessage.role, content: currentMessage.content });

            // Find the message that this message is replying to
            currentMessage = chatMessages.find(message => message.id === currentMessage.replyTo?.messageId);
        }

        return messages;
    }

    // // This is the storeMessage function for the community chat.
    // // This function was used before the upgrade on 4-30-24
    // const storeMessage = async () => {
    //     // Grab the current message
    //     const query = currentMessage;

    //     // If the user didn't type anything, don't send the message
    //     if (query === "") {
    //         return;
    //     }

    //     // Reset the current message
    //     setCurrentMessage("")

    //     // Grab the message that this message is replying to
    //     const replyInfo = replyTo;
    //     setReplyTo(null);

    //     // Add the message to the tempMessages array so that it appears immediately
    //     setTempMessages([...tempMessages, { role: CHAT_ROLES.USER, content: query }]);

    //     // Get all messages in this reply chain (if any)
    //     let messages;
    //     if (replyInfo) {
    //         messages = constructMessages(replyInfo.messageId);
    //     } else {
    //         messages = [];
    //     }

    //     try {
    //         // Send the message to the backend
    //         const response = await communityChatEndpoint({
    //             chatMessages: messages,
    //             query: query,
    //             lessonId: lessonData.id,
    //             currSlideId: currSlideId,
    //             userName: userName,
    //             aiName: CHATBOT_NAME,
    //             replyTo: replyInfo
    //         });

    //         // If the message was flagged, alert the user
    //         if (response.data === FLAGGED_POST) {
    //             errorToast(FLAGGED_POST_MESSAGE, ERROR_TOAST_DURATION);
    //         }
    //         // The AI will no longer respond to this users messages. 
    //         // Not sure if we have to tell them this.
    //         // else if (response.data === MESSAGE_LIMIT) {
    //         //     errorToast(MESSAGES_LIMIT_MESSAGE, ERROR_TOAST_DURATION);
    //         // }

    //     } catch (error) {
    //         errorToast(CHAT_SERVICE_ERROR_MESSAGE, ERROR_TOAST_DURATION);
    //     }
    // }

    // This is the NEW storeMessage function for the community chat.
    // Changes include:
    // 1. Use GPT-4
    // 2. Make AI always respond to the user (instead of decide)
    // 3. Give AI current context
    // 4. Give AI all messages in the chat (last 10)
    // Change occurred on 4-30-24
    const storeMessageNEW = async () => {
        // Grab the current message
        const query = currentMessage;

        // If the user didn't type anything, don't send the message
        if (query === "") {
            return;
        }

        // Reset the current message
        setCurrentMessage("")

        // Grab the message that this message is replying to
        const replyInfo = replyTo;
        setReplyTo(null);

        // Add the message to the tempMessages array so that it appears immediately
        setTempMessages([...tempMessages,
        {
            role: CHAT_ROLES.USER,
            content: query,
            replyTo: replyInfo
        }]);

        try {
            const currentContent = await getCurrentContent();
            const response = await communityChatEndpointNEW({
                chatMessages: chatMessages,
                query: query,
                lessonId: lessonData.id,
                currSlideId: currSlideId,
                userName: userName,
                aiName: CHATBOT_NAME,
                replyTo: replyInfo,
                currContent: currentContent,
                isPersonified: isPersonified(chatType)
            });

            if (response.data === FLAGGED_POST) {
                // If the message was flagged, alert the user
                errorToast(FLAGGED_POST_MESSAGE, ERROR_TOAST_DURATION);
            } else if (response.data === MESSAGE_LIMIT) {
                // The AI will no longer respond to this users messages. 
                errorToast(MESSAGES_LIMIT_MESSAGE, ERROR_TOAST_DURATION);
            }

        } catch (error) {
            errorToast(CHAT_SERVICE_ERROR_MESSAGE, ERROR_TOAST_DURATION);
        }

    }

    return (
        <ChatWindow>
            {/* The Chat bar on top */}
            <ChatHeader />

            {/* The messages area */}
            <MessagesDisplay
                ref={messagesDisplayRef}
                onScroll={loadMoreMessages}>
                {[...chatMessages].reverse().map((message, index) => (
                    <RepliableMessage
                        key={message.id}
                        message={message}
                        setReplyTo={setReplyTo}
                        chatType={chatType}
                        chatMessages={chatMessages} />
                ))}
                <div ref={messagesEndRef} />
                {[...tempMessages].map((message, index) => (
                    <RepliableMessageTemp
                        key={index + "temp-message"}
                        message={message}
                        chatType={chatType}
                        chatMessages={chatMessages}
                    />
                ))}
            </MessagesDisplay>

            {/* This is the reply to message */}
            {replyTo &&
                <CurrentlyReplying>
                    <CurrentlyReplyingExit onClick={() => setReplyTo(null)}>x</CurrentlyReplyingExit>
                    <CurrentlyReplyingAuthor><strong>{replyTo.authorName}</strong></CurrentlyReplyingAuthor>
                    <CurrentlyReplyingText>
                        <FormattedMessage content={replyTo.content} />
                    </CurrentlyReplyingText>
                </CurrentlyReplying>}

            {/* The user input area */}
            <MessageInputArea
                currentMessage={currentMessage}
                setCurrentMessage={setCurrentMessage}
                sendMessage={storeMessageNEW} />
        </ChatWindow>
    );

};

const CurrentlyReplying = styled.div`
    background-color: #f0f0f0;
    padding: 5px;
    border-bottom: 1px solid #ccc;
    position: relative;
`;

const CurrentlyReplyingAuthor = styled.p`
    font-size: 0.9rem;
    color: #0;
    width: fit-content;
    margin: 0;
`;

const CurrentlyReplyingText = styled.p`
    font-size: 0.9rem;
    color: #555;
    width: 100%;
    margin: 0;
    word-wrap: break-word;
`;


const CurrentlyReplyingExit = styled.button`
    background-color: transparent;
    border: none;
    position: absolute;
    top: 0px;
    right: 0px;
    font-size: 20px;
    color: #555;
    cursor: pointer;
`;

