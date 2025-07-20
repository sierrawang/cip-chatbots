// The different chat experience types

import { BasicChat } from "./BasicChat";
import { GroundedChat } from "./GroundedChat";
import { ButtonsChat } from "./ButtonsChat";
import { IDEChat } from "./IDEChat";
import { CommunityChat } from "./CommunityChat";

export const CHATBOT_NAME = "Chat"; // Cai, Codey, Code Queen, Grumpy Chat, Potato

// Intro messages for basic and grounded
export const CHAT_INTRO_MESSAGE = `This is your space to ask questions and discuss the content as you work through the lesson. Happy learning! 🌱`;
export const CHAT_INTRO_MESSAGE_PERSONIFIED = `Hello! I'm ${CHATBOT_NAME}, the AI chatbot for Code in Place. I'm here to answer questions and discuss the content as you work through the lesson. Happy learning! 🌱`;

// Intro messages for community
export const COMMUNITY_INTRO_MESSAGE = `This is your space to connect with other students who are working through this lesson alongside you. Don't hesitate to ask questions or help out others. Let's learn and grow together! 🌱`;
export const COMMUNITY_INTRO_MESSAGE_PERSONIFIED = `Hello! I'm ${CHATBOT_NAME}, the AI chatbot for Code in Place. This is your space to connect with other students who are working through this lesson alongside you. Don't hesitate to ask questions or help out others. Let's learn and grow together! 🌱`

// Intro messages for buttons
export const BUTTONS_CHAT_INTRO_MESSAGE = `Use the buttons below to get a different explanation of the material or learn why it matters. Happy learning! 🌱`;
export const BUTTONS_CHAT_INTRO_MESSAGE_PERSONIFIED = `Hello! I'm ${CHATBOT_NAME}, the AI chatbot for Code in Place. I'm here to help you understand the content as you work through the lesson. Use the buttons below if you want me to explain the material differently or explain why it matters. Happy learning! 🌱`;

// Intro messages for IDE chat
export const IDE_CHAT_INTRO_MESSAGE = `This is your space to ask questions and discuss the content as you work through the assignment. Happy learning! 🌱`;
export const IDE_CHAT_INTRO_MESSAGE_PERSONIFIED = `Hello! I'm ${CHATBOT_NAME}, the AI chatbot for Code in Place. I'm here to answer questions and discuss the content as you work through the assignment. Happy learning! 🌱`;

const CHAT_NAMES = {
    NO_CHAT: "No chat",
    GROUNDED: "Grounded",
    GROUNDED_PERSONIFIED: "Grounded Personified",
    BASIC: "Basic",
    BASIC_PERSONIFIED: "Basic Personified",
    COMMUNITY: "Community",
    COMMUNITY_PERSONIFIED: "Community Personified",
    BUTTONS: "Buttons",
    BUTTONS_PERSONIFIED: "Buttons Personified",
    IDE: "IDE",
    IDE_PERSONIFIED: "IDE Personified",
}

export const NUM_CHATS = 11;

export const CHAT_TYPES = {
    0: null, // No chat
    1: { name: CHAT_NAMES.GROUNDED, component: <GroundedChat />, intro_message: CHAT_INTRO_MESSAGE },
    2: { name: CHAT_NAMES.GROUNDED_PERSONIFIED, component: <GroundedChat />, intro_message: CHAT_INTRO_MESSAGE_PERSONIFIED },
    3: { name: CHAT_NAMES.BASIC, component: <BasicChat />, intro_message: CHAT_INTRO_MESSAGE },
    4: { name: CHAT_NAMES.BASIC_PERSONIFIED, component: <BasicChat />, intro_message: CHAT_INTRO_MESSAGE_PERSONIFIED },
    5: { name: CHAT_NAMES.COMMUNITY, component: <CommunityChat />, intro_message: COMMUNITY_INTRO_MESSAGE },
    6: { name: CHAT_NAMES.COMMUNITY_PERSONIFIED, component: <CommunityChat />, intro_message: COMMUNITY_INTRO_MESSAGE_PERSONIFIED },
    7: { name: CHAT_NAMES.BUTTONS, component: <ButtonsChat />, intro_message: BUTTONS_CHAT_INTRO_MESSAGE },
    8: { name: CHAT_NAMES.BUTTONS_PERSONIFIED, component: <ButtonsChat />, intro_message: BUTTONS_CHAT_INTRO_MESSAGE_PERSONIFIED },
    9: { name: CHAT_NAMES.IDE, component: <IDEChat />, intro_message: IDE_CHAT_INTRO_MESSAGE },
    10: { name: CHAT_NAMES.IDE_PERSONIFIED, component: <IDEChat />, intro_message: IDE_CHAT_INTRO_MESSAGE_PERSONIFIED }
};

export const MESSAGE_RETRIEVAL_LIMIT = 25;

export const CHAT_INTRO_SLIDE_ID = "unique-chatbot-intro-slide-1997";

export const AI_ID = "ai";
export const CHAT_ROLES = {
    USER: "user",
    ASSISTANT: "assistant"
}

export const MESSAGE_LIMIT = "MESSAGE_LIMIT";
export const FLAGGED_POST = "FLAGGED_POST";
export const MESSAGES_LIMIT_MESSAGE = "Message limit reached. Chat will resume in the next lesson!";
export const FLAGGED_POST_MESSAGE = "Your message has been flagged for inappropriate content. It will not be posted to the chat.";
export const CHAT_SERVICE_ERROR_MESSAGE = "There was an error with the chat service. Please try again.";
export const ERROR_TOAST_DURATION = 10000;

// chatType is No Chat or not defined
export const isNoChat = (chatType) => {
    return !chatType || CHAT_TYPES[chatType] === null;
}

export const isIDE = (chatType) => {
    return !isNoChat(chatType) &&
        (CHAT_TYPES[chatType].name === CHAT_NAMES.IDE ||
            CHAT_TYPES[chatType].name === CHAT_NAMES.IDE_PERSONIFIED);
}

export const isCommunity = (chatType) => {
    return !isNoChat(chatType) &&
        (CHAT_TYPES[chatType].name === CHAT_NAMES.COMMUNITY ||
            CHAT_TYPES[chatType].name === CHAT_NAMES.COMMUNITY_PERSONIFIED);
}

export const isButtons = (chatType) => {
    return !isNoChat(chatType) &&
        (CHAT_TYPES[chatType].name === CHAT_NAMES.BUTTONS ||
            CHAT_TYPES[chatType].name === CHAT_NAMES.BUTTONS_PERSONIFIED);
}

export const isGrounded = (chatType) => {
    return !isNoChat(chatType) &&
        (CHAT_TYPES[chatType].name === CHAT_NAMES.GROUNDED ||
            CHAT_TYPES[chatType].name === CHAT_NAMES.GROUNDED_PERSONIFIED);
}

export const isBasic = (chatType) => {
    return !isNoChat(chatType) &&
        (CHAT_TYPES[chatType].name === CHAT_NAMES.BASIC ||
            CHAT_TYPES[chatType].name === CHAT_NAMES.BASIC_PERSONIFIED);
}

export const isPersonified = (chatType) => {
    return !isNoChat(chatType) &&
        (CHAT_TYPES[chatType].name === CHAT_NAMES.GROUNDED_PERSONIFIED ||
            CHAT_TYPES[chatType].name === CHAT_NAMES.BASIC_PERSONIFIED ||
            CHAT_TYPES[chatType].name === CHAT_NAMES.COMMUNITY_PERSONIFIED ||
            CHAT_TYPES[chatType].name === CHAT_NAMES.BUTTONS_PERSONIFIED ||
            CHAT_TYPES[chatType].name === CHAT_NAMES.IDE_PERSONIFIED);
}