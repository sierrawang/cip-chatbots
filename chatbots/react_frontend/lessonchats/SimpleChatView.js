import { useEffect, useRef, useContext, useState } from 'react';
import { LessonContext } from "../LessonContext";
import { TypingAnimation } from "./TypingAnimation";
import { MessageInputArea } from './MessageInputArea';
import { ChatWindow, MessagesDisplay } from './ChatStyles';
import { ChatHeader } from './ChatHeader';
import { SimpleMessage } from './SimpleMessage';

export const SimpleChatView = ({ sendMessage, currentMessage, setCurrentMessage, sendEnabled }) => {

    // Keep track of the page Index from the lesson context
    const { chatMessages, tempMessages, loadChat, chatType } = useContext(LessonContext);

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

    return (
        <ChatWindow>
            {/* The Chat bar on top */}
            <ChatHeader />

            {/* The messages area */}
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

            {/* The user input area */}
            <MessageInputArea
                currentMessage={currentMessage}
                setCurrentMessage={setCurrentMessage}
                sendMessage={sendMessage} />
        </ChatWindow>
    );

};