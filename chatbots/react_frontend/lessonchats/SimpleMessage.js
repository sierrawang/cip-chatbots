import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { MessageButtonsDiv, chatStyleConstants } from "./ChatStyles";
import { AI_ID, CHAT_ROLES, isPersonified } from './ChatConstants';
import { MessageRating } from './MessageRating';
import { useUserId } from 'hooks/user/useUserId';
import { MessageAuthor } from './RepliableMessage';

const renderTextWithMarkdownLinks = (text) => {
    // Matches Markdown links and text outside of links, excluding code blocks
    const regex = /(`.*?`|\[.*?\]\(.*?\))/g;
    const parts = text.split(regex);

    return parts.map((part, index) => {
        if (part.startsWith('[') && part.includes('](')) {
            // Extract text and URL from Markdown link
            const match = part.match(/\[(.*?)\]\((.*?)\)/);
            if (match) {
                const [_, text, url] = match;
                return <a key={index} href={url} target="_blank" rel="noopener noreferrer">{text}</a>;
            }
        } else if (part.startsWith('`') && part.endsWith('`')) {
            // Code snippet - render as inline code
            const code = part.slice(1, -1);
            return <code key={index}>{code}</code>;
        }
        return part;
    });
};

export const SimpleMessage = ({ message, chatType, chatMessages }) => {
    const { content, role, authorId, authorName } = message;
    const [isHovered, setIsHovered] = useState(false);
    const userId = useUserId();
    const userIsAuthor = userId === authorId;
    const personified = isPersonified(chatType);

    // Splitting the message into sections based on code blocks
    const sections = content.split('```');

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

    return (
        <StyledMessage
            role={role}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            {!userIsAuthor && personified && <MessageAuthor>{authorName}</MessageAuthor>}
            {sections.map((section, index) => {
                // Odd indices are code, even indices are text
                const isCode = index % 2 !== 0;
                if (isCode) {
                    // Extract the language from the code block, assuming the format is correct
                    const firstNewLineIndex = section.indexOf('\n');
                    const language = section.substring(0, firstNewLineIndex).trim();
                    const code = section.substring(firstNewLineIndex + 1);
                    return (
                        <SyntaxHighlighter key={index} language={language || "python"} customStyle={{ fontSize: '12px', backgroundColor: 'white' }}>
                            {code}
                        </SyntaxHighlighter>
                    );
                } else {
                    // For text, preserve new lines, but trim leading/trailing whitespace/newlines
                    const trimmedSection = section.trim(); // Trim leading and trailing whitespace/newlines
                    if (!trimmedSection) return null; // Don't render empty sections
                    return trimmedSection.split('\n').map((line, lineIndex) => (
                        <React.Fragment key={`${index}-${lineIndex}`}>
                            {renderTextWithMarkdownLinks(line)}
                            <br />
                        </React.Fragment>
                    ));
                }
            })}
            <MessageButtonsDiv>
                {renderRatingComponent()}
            </MessageButtonsDiv>
        </StyledMessage>
    );
};

const StyledMessage = styled.div`
  position: relative;
  padding: 5px;
  width: fit-content;
  margin-bottom: 0.5rem;
  background-color: ${(props) => props.role === CHAT_ROLES.USER ? chatStyleConstants.userMessageBackground : chatStyleConstants.otherMessageBackground};
  align-self: ${(props) => props.role === CHAT_ROLES.USER ? 'end' : 'start'};
  border-radius: ${(props) => props.role === CHAT_ROLES.USER ? '5px 5px 0px 5px' : '5px 5px 5px 0px'};
  max-width: 100%;
  word-wrap: break-word;
  font-size: ${chatStyleConstants.messageFontSize};

  pre, code {
    background-color: #f5f5f5; /* Light grey background for code */
    border-radius: 4px;
    padding: 2px 4px;
  }

  pre {
    margin: 0; // Adjusting the margin for SyntaxHighlighter
    background-color: inherit; // Makes the code block background match the message background
  }
`;