// Message component that looks like a whatsapp message
// It is on the right side if the user is the author and on the left side if the user is not the author
// It has a reply feature that allows users to reply to a message and only is visible when the user hovers over the message

import { useUserId } from "hooks/user/useUserId";
import styled from "styled-components";
import { FormattedMessage } from "./FormattedMessage";
import { MessageButtonContainer, MessageButtonsDiv, MessageP, chatStyleConstants } from "./ChatStyles";
import { AI_ID } from './ChatConstants';
import { MessageRating } from './MessageRating';
import { useState } from "react";

export const RepliableMessage = ({ message, setReplyTo, chatType, chatMessages }) => {
    const { content, authorId, authorName, messageId, replyTo } = message;
    const userId = useUserId();
    const [isHovered, setIsHovered] = useState(false);
    const userIsAuthor = userId === authorId;

    // Only display MessageRating on hover for AI messages
    const renderRatingComponent = () => {
        if (authorId === AI_ID && isHovered) {
            return <MessageRating
                message={message}
                chatType={chatType}
                chatMessages={chatMessages} />;
        }
        return null;
    };

    // Only display the reply button on hover
    const renderReplyButton = () => {
        if (isHovered) {
            return (
                <MessageButtonContainer>
                    <MessageP
                        onClick={() => { setReplyTo({ messageId, content, authorName }) }}
                        className="btn btn-light mr-1">
                        Reply
                    </MessageP>
                </MessageButtonContainer>
            );
        }
        return null;
    }

    return (
        <RepliableMessageContainerOuter userIsAuthor={userIsAuthor}>
            <RepliableMessageContainer
                userIsAuthor={userIsAuthor}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
            >
                {!userIsAuthor && <MessageAuthor>{authorName}</MessageAuthor>}
                {replyTo && <ReplyView replyTo={replyTo} userIsAuthor={userIsAuthor} />}
                <MessageContent>
                    <FormattedMessage content={content} />
                </MessageContent>
                <MessageButtonsDiv>
                    {renderRatingComponent()}
                    {renderReplyButton()}
                </MessageButtonsDiv>
            </RepliableMessageContainer>

        </RepliableMessageContainerOuter>
    );
};

const ReplyView = ({ replyTo, userIsAuthor }) => {
    const { content, authorName } = replyTo;

    return (
        <ReplyViewContainer userIsAuthor={userIsAuthor}>
            <ReplyViewAuthor userIsAuthor={userIsAuthor}>{authorName}</ReplyViewAuthor>
            <ReplyViewContent>
                <FormattedMessage content={content} />
            </ReplyViewContent>
        </ReplyViewContainer>
    );
}

const RepliableMessageContainerOuter = styled.div`
    display: flex;
    flex-direction: column;
    align-items: ${props => props.userIsAuthor ? 'flex-end' : 'flex-start'};
    width: 100%;
    margin-bottom: 0.5rem;
    &:hover button {
        visibility: visible;
    }
`;

const RepliableMessageContainer = styled.div`
    position: relative;
    display: flex;
    flex-direction: column;
    align-self: ${props => props.userIsAuthor ? 'flex-end' : 'flex-start'};
    background-color: ${props => props.userIsAuthor ? chatStyleConstants.userMessageBackground : chatStyleConstants.otherMessageBackground};
    border-radius: ${props => props.userIsAuthor ? '5px 5px 0px 5px' : '5px 5px 5px 0px'};
    padding: 5px;
    max-width: 100%;
    word-wrap: break-word;
`;

const MessageContent = styled.div`
    color: ${chatStyleConstants.messageTextColor};
    font-size: ${chatStyleConstants.messageFontSize};
`;

export const MessageAuthor = styled.div`
    font-size: ${chatStyleConstants.authorFontSize};
    color: ${chatStyleConstants.authorTextColor};
`;

const ReplyViewContainer = styled.div`
    background-color: ${props => props.userIsAuthor ? chatStyleConstants.userReplyBackground : chatStyleConstants.otherReplyBackground};
    padding: 5px;
    // padding-left: 8px; /* Increased padding to accommodate the border */
    border-radius: 5px;
    position: relative;
    border-left: 3px solid ${props => props.userIsAuthor ? chatStyleConstants.replyBorderUser : chatStyleConstants.replyBorderOther};
    margin-bottom: 3px;
`;

const ReplyViewContent = styled.div`
    color: black;
    font-size: 0.9rem;
`;

const ReplyViewAuthor = styled.div`
    font-size: 0.8rem;
    color: ${props => props.userIsAuthor ? chatStyleConstants.replyBorderUser : chatStyleConstants.replyBorderOther};
`;

