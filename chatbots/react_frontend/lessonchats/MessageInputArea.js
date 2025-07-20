// This is a textarea that adjusts its height to fit the content 
// when the text changes, and when the width changes.

import styled from 'styled-components';
import { useEffect, useRef } from 'react';
import { chatStyleConstants } from './ChatStyles';
import { popLoadingAlert } from 'course/forum/components/forumGeneral';

export const MessageInputArea = ({ currentMessage, setCurrentMessage, sendMessage }) => {

    const MAX_MESSAGE_LENGTH = 2000; // characters

    // References to keep track of the size of the message input area
    const messageInputRef = useRef(null);
    const messageInputWidthRef = useRef(0);

    // Adjust the height of the message input area to fit the content
    const adjustHeight = () => {
        if (messageInputRef.current) {
            requestAnimationFrame(() => {
                try {
                    // Shrink the textarea so that we can get the scrollHeight
                    // This is necessary if the user deleted some text
                    messageInputRef.current.style.height = '5px';

                    // Set the height to the scrollHeight
                    messageInputRef.current.style.height = `${messageInputRef.current.scrollHeight}px`;
                } catch (e) {
                    console.error(e);
                }
            });
        }
    };

    // Adjust the height whenever the message changes
    useEffect(() => {
        adjustHeight();
    }, [currentMessage]);


    // Add a listener to the textarea to adjust the height whenever the width changes
    useEffect(() => {
        const textarea = messageInputRef.current;
        if (textarea) {
            // Initialize the previous width
            messageInputWidthRef.current = textarea.offsetWidth;

            const resizeObserver = new ResizeObserver((entries) => {
                for (let entry of entries) {
                    const currentWidth = entry.target.offsetWidth;

                    // Only update the height if the width has changed
                    if (currentWidth !== messageInputWidthRef.current) {
                        adjustHeight();

                        // Update the previous width for the next observation
                        messageInputWidthRef.current = currentWidth;
                    }
                }
            });

            resizeObserver.observe(textarea);
            return () => resizeObserver.unobserve(textarea);
        }
    }, []);

    const checkMessageLengthAndUpdate = (e) => {
        if (e.target.value.length <= MAX_MESSAGE_LENGTH) {
            setCurrentMessage(e.target.value);
        } else {
            popLoadingAlert("Message must be 500 characters or less.");
        }

    }

    return (
        <MessageInputContainer>
            <StyledTextArea
                ref={messageInputRef}
                placeholder="Type your message..."
                value={currentMessage}
                onChange={(e) => checkMessageLengthAndUpdate(e)}
                onKeyPress={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault(); // Prevent new line on Enter key
                        sendMessage();
                    }
                }}
            />
            <button className="btn btn-primary" style={{ marginLeft: '10px', height: 'fit-content', alignSelf: 'end' }} onClick={sendMessage}>Send</button>
        </MessageInputContainer>
    );

};

const MessageInputContainer = styled.div`
    display: flex;
    background-color: white;
    border-top: 1px solid #ccc;
    padding: 10px;
    width: 100%;
    bottom: 0;
    align-items: center;
`;

const StyledTextArea = styled.textarea`
    border: none;
    width: 100%;
    outline: none;
    flex: 1;
    resize: none;
    font-size: ${chatStyleConstants.messageFontSize};
    line-height: 1.5;
    overflow-y: hidden;
    height: auto;
    min-height: 28px;
    padding-top: calc((28px - 1.5em) / 2);
    padding-bottom: calc((28px - 1.5em) / 2);
    display: block;
`;
