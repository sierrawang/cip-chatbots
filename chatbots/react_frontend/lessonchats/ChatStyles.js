import styled from 'styled-components';

export const chatStyleConstants = {
    userMessageBackground: '#cfdcff',
    otherMessageBackground: '#daedeb',
    userReplyBackground: '#ebf0ff',
    otherReplyBackground: '#edf5f4',
    replyBorderUser: '#6C63FF',
    replyBorderOther: '#009688',
    messageTextColor: '#000', // black
    authorTextColor: '#555',
    messageFontSize: '16px', // '0.85rem',
    authorFontSize: '0.8rem',
};

export const ChatWindow = styled.div`
    background-color: white;
    height: 100vh;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow-y: hidden;
`;

export const MessagesDisplay = styled.div`
    display: flex;
    background-color: white;
    padding: 10px 10px 0px 10px;
    flex-direction: column;
    flex-grow: 1;
    overflow-y: auto;
    width: 100%;
`;

// Div to hold all of the buttons that are attached to the message
export const MessageButtonsDiv = styled.div`
    position: absolute;
    display: flex;
    flex-direction: row;
    bottom: -1.2rem;
    right: 0;
    z-index: 1000;
`;

// Div to wrap buttons (can wrap them together or separately)
export const MessageButtonContainer = styled.div`
    display: flex;
    flex-direction: row;
    background-color: white;
    border-radius: 5px;
    align-items: center;
    justify-content: center;
    height: fit-content;
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.25);
    padding: 0.15rem;
    margin-right: 0.5rem;
`;

// p tags for message buttons ("Rate this response" and "Your rating:")
export const MessageP = styled.p`
    display: flex;
    font-size: 0.7rem;
    background-color: transparent;
    border: none;
    width: fit-content;
    height: 25px;
    align-items: center;
    justify-content: center;
    color: ${chatStyleConstants.authorTextColor};
    padding: 0 0.1rem 0 0.1rem;
    margin: 0;
`;

// Button style for message buttons
// Include className="btn btn-light mr-1" in the button tag
export const MessageButton = styled.button`
    className: btn btn-light mr-1;
    display: flex;
    background-color: transparent;
    align-items: center;
    justify-content: center;
    border: none;
    color: ${chatStyleConstants.authorTextColor};
    cursor: pointer;
    font-size: 1rem;
    padding: 0.1rem;
    margin: 0;
    width: 25px;
    height: 25px;
`;