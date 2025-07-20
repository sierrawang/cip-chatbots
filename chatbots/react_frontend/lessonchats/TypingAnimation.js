import styled, { keyframes } from 'styled-components';
import { CHATBOT_NAME } from './ChatConstants';
import { chatStyleConstants } from "./ChatStyles";

// Component using styled-components
export const TypingAnimation = () => {
  return (
    <TypingAnimationWrapper>
      <StaticText>{CHATBOT_NAME} is typing</StaticText>
      <TypingDot delay={0.2} />
      <TypingDot delay={0.4} />
      <TypingDot delay={0.6} />
    </TypingAnimationWrapper>
  );
};

// Define the keyframes for the dot animation
const dotAnimation = keyframes`
  0%, 100% {
    opacity: 0;
  }
  50% {
  opacity: 1;
}
`;

// Styled component for the animation wrapper
const TypingAnimationWrapper = styled.div`
  display: flex;
  align-items: center;
  font-size: ${chatStyleConstants.messageFontSize}; 
  background-color: white;
  width: fit-content;
  border-radius: 5px 5px 5px 0px;
  margin-bottom: 0.2rem;
  max-width: 100%;

`;

// Styled component for the static text
const StaticText = styled.span`
  font-size: ${chatStyleConstants.messageFontSize};
  color: ${chatStyleConstants.messageTextColor}; 
`;

// Styled component for the animated dots
const TypingDot = styled.span`
  padding-left: 2px; 
  opacity: 0; 
  animation: ${dotAnimation} 1.5s infinite;
  animation-delay: ${({ delay }) => delay}s; 

  &:after {
  content: '.';
  color: ${chatStyleConstants.messageTextColor};
}
`;