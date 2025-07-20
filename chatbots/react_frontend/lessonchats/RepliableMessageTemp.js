// Message component that looks like a whatsapp message
// It is on the right side if the user is the author and on the left side if the user is not the author
// It has a reply feature that allows users to reply to a message and only is visible when the user hovers over the message

import styled from "styled-components";
import { FormattedMessage } from "./FormattedMessage";
import { chatStyleConstants } from "./ChatStyles";

export const RepliableMessageTemp = ({ message }) => {
    const { content, replyTo } = message;

    return (
        <RepliableMessageContainerOuter>
            <RepliableMessageContainer>
                {replyTo && <ReplyView replyTo={replyTo} />}
                <MessageContent>
                    <FormattedMessage content={content} />
                </MessageContent>
            </RepliableMessageContainer>

        </RepliableMessageContainerOuter>
    );
};

const ReplyView = ({ replyTo }) => {
    const { content, authorName } = replyTo;

    return (
        <ReplyViewContainer>
            <ReplyViewAuthor>{authorName}</ReplyViewAuthor>
            <ReplyViewContent>
                <FormattedMessage content={content} />
            </ReplyViewContent>
        </ReplyViewContainer>
    );
}

const RepliableMessageContainerOuter = styled.div`
    display: flex;
    flex-direction: column;
    align-items: flex-end;
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
    align-self: flex-end;
    background-color: ${chatStyleConstants.userMessageBackground};
    border-radius: 5px 5px 0px 5px;
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
    background-color: ${chatStyleConstants.userReplyBackground};
    padding: 5px;
    // padding-left: 8px; /* Increased padding to accommodate the border */
    border-radius: 5px;
    position: relative;
    border-left: 3px solid ${chatStyleConstants.replyBorderUser};
    margin-bottom: 3px;
`;

const ReplyViewContent = styled.div`
    color: black;
    font-size: 0.9rem;
`;

const ReplyViewAuthor = styled.div`
    font-size: 0.8rem;
    color: ${chatStyleConstants.replyBorderUser};
`;

