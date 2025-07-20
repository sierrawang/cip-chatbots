// This file contains all of the updated chat endpoints for the chat experiment.
// This update happened on 4/30/24 (california time).
// Functions that were used prior to this update are in chat_endpoints.ts.
//
// This update includes the following changes:
// 1. Basic, grounded, IDE, and community chat endpoints now respond based on the user's chatType as personified or not personified.
// 2. The following additional changes for the community chat endpoint:
//   - The AI always responds to the user (instead of deciding)
//   - The AI is given the current context
//   - The AI is given all messages in the chat (last 10)
//   - It uses GPT-4

import * as functions from "firebase-functions";
import { contructMessages, storeMessage, storeIDEMessage, checkNumLessonMessages, MESSAGES_LIMIT, checkNumAssnMessages, incrementNumMessagesLessons, incrementNumMessagesAssns, FLAGGED_POST } from "./chat_helper_functions";
import { MAX_TOKENS, callGPTChat } from "./chat_openai_client";
import { generateGroundedResponse } from "./rag/rag_logic";
import { CONTEXT_PROMPT, INSTRUCTIONS_PROMPT, CONTEXT_PROMPT_COMMUNITY, PERSONIFIED_EXPLANATION, TOOL_EXPLANATION } from "./chat_prompts";
import { getModeration } from "../gpt_functions";


// This is the endpoint for the basic chatbot: 
// It generates a response to the user using a relatively simple prompt and GPT-4.
export const basicChatEndpointNEW = functions.https.onCall(
    async (
        data: {
            chatMessages: any,
            query: string,
            lessonId: string,
            currSlideId: string,
            userName: string,
            aiName: string,
            currContent: string,
            isPersonified: boolean
        },
        context
    ) => {
        // Make sure the user is authenticated
        const userId = context.auth?.uid;
        if (!userId) { return "" }

        const { chatMessages, query, lessonId, currSlideId, userName, aiName, currContent, isPersonified } = data;

        // Add the query to the database
        await storeMessage(userId, userId, userName, "user", query, currSlideId, null, lessonId, {});
        await incrementNumMessagesLessons(userId, lessonId);

        // Check whether the user has sent too many messages
        if (await checkNumLessonMessages(userId, lessonId)) {
            return MESSAGES_LIMIT;
        }

        // Convert the chat messages to the format needed by GPT
        const messages = contructMessages(chatMessages, query);

        let systemPrompt = CONTEXT_PROMPT + "\n\n";
        systemPrompt += "The student is currently working on a lesson titled: " + lessonId + "\n\n";
        systemPrompt += "The student is currently looking at " + currContent + "\n\n";
        systemPrompt += INSTRUCTIONS_PROMPT + "\n\n";

        if (isPersonified) {
            systemPrompt += PERSONIFIED_EXPLANATION;
        } else {
            systemPrompt += TOOL_EXPLANATION;
        }

        // Prepend a system prompt to the messages
        const messagesPrompt = [{
            role: "system",
            content: systemPrompt
        },
        ...messages];

        functions.logger.info("basicChatEndpoint - calling GPT with messages\n", messagesPrompt);

        // Call the chat completions API
        const content = await callGPTChat("gpt-4", messagesPrompt, undefined, MAX_TOKENS);

        // Add the response to the database
        await storeMessage(userId, "ai", aiName, "assistant", content, currSlideId, null, lessonId, {});

        return content;
    }
);

// This is the endpoint for the grounded chatbot:
// It generates a response to the user by first retrieving relevant course materials
// and then using RAG to generate a response.
export const groundedChatEndpointNEW = functions.https.onCall(
    async (
        data: {
            chatMessages: any,
            query: string,
            currSlideId: string,
            lessonId: string,
            userName: string,
            aiName: string,
            currContent: string,
            isPersonified: boolean
        },
        context
    ) => {
        // Make sure the user is authenticated
        const userId = context.auth?.uid;
        if (!userId) { return "" }

        const { chatMessages, query, lessonId, currSlideId, userName, aiName, currContent, isPersonified } = data;

        // Add the user's most recent message to the database
        await storeMessage(userId, userId, userName, "user", query, currSlideId, null, lessonId, {});
        await incrementNumMessagesLessons(userId, lessonId);

        // Check whether the user has sent too many messages
        if (await checkNumLessonMessages(userId, lessonId)) {
            return MESSAGES_LIMIT;
        }

        // Format the messages into GPT chat API format
        const messages = contructMessages(chatMessages, query);

        // Generate a grounded response!
        const response = await generateGroundedResponse(userId, messages, currContent, lessonId, isPersonified);

        // Add the response to the database
        await storeMessage(userId, "ai", aiName, "assistant", response, currSlideId, null, lessonId, {});

        return response;
    }
);

// This is the endpoint for the IDE chatbot:
// It generates a response to the user using a relatively simple prompt and GPT-4.
export const ideChatEndpointNEW = functions.https.onCall(
    async (
        data: {
            chatMessages: any,
            query: string,
            assnId: string,
            userName: string,
            aiName: string,
            code: string,
            assnPrompt: string,
            isPersonified: boolean
        },
        context
    ) => {
        // Make sure the user is authenticated
        const userId = context.auth?.uid;
        if (!userId) { return "" }

        const { chatMessages, query, assnId, userName, aiName, code, assnPrompt, isPersonified } = data;

        // Add the query to the database
        await storeIDEMessage(userId, userId, userName, "user", query, assnId, {});
        await incrementNumMessagesAssns(userId, assnId);

        // Check whether the user has sent too many messages
        if (await checkNumAssnMessages(userId, assnId)) {
            return MESSAGES_LIMIT;
        }

        // Convert the chat messages to the format needed by GPT
        const messages = contructMessages(chatMessages, query);

        // Construct the system prompt
        let systemPrompt = CONTEXT_PROMPT + "\n\n";
        if (assnPrompt) {
            systemPrompt += "Here are the homework assignment instructions:\n\n";
            systemPrompt += assnPrompt + "\n\n";
        } else {
            systemPrompt += "The student is currently working on a creative project.\n";
        }
        systemPrompt += "Here is the student's current code:\n```\n";
        systemPrompt += code + "\n```\n";
        systemPrompt += INSTRUCTIONS_PROMPT + "\n\n";

        if (isPersonified) {
            systemPrompt += PERSONIFIED_EXPLANATION;
        } else {
            systemPrompt += TOOL_EXPLANATION;
        }

        // Prepend a system prompt to the messages
        const messagesPrompt = [{
            role: "system",
            content: systemPrompt
        },
        ...messages];

        // Call the chat completions API
        const content = await callGPTChat("gpt-4", messagesPrompt, undefined, MAX_TOKENS);

        // Add the response to the database
        await storeIDEMessage(userId, "ai", aiName, "assistant", content, assnId, {});

        return content;
    }
);

// When the front end that connected to this endpoint was pushed to prod (4/30?), it broke because the endpoint pointed to communityTEST but the frontend listened to community.
// Sierra caught this bug and changed the endpoint to community at 11pm on 5/4/24.
// On the bright side, only 2 students tried to use the chat feature during this time. Their messages (and the AI response) can be seen in communityTEST. 
export const communityChatEndpointNEW = functions.https.onCall(
    async (
        data: {
            chatMessages: any,
            query: string,
            lessonId: string,
            currSlideId: string,
            userName: string,
            aiName: string,
            replyTo: any,
            currContent: string,
            isPersonified: boolean
        },
        context
    ) => {
        // Make sure the user is authenticated
        const userId = context.auth?.uid;
        if (!userId) { return "" }

        const { chatMessages, query, lessonId, currSlideId, userName, aiName, replyTo, currContent, isPersonified } = data;

        // Check the query for moderation
        const isFlagged = await getModeration(query);
        if (isFlagged) {
            return FLAGGED_POST;
        }

        // Add the query to the database
        const messageId = await storeMessage("community", userId, userName, "user", query, currSlideId, replyTo, lessonId, {});
        await incrementNumMessagesLessons(userId, lessonId);

        // Check whether the user has sent too many messages
        if (await checkNumLessonMessages(userId, lessonId)) {
            return MESSAGES_LIMIT;
        }

        // Convert the chat messages to the format needed by GPT
        const messages = contructMessages(chatMessages, query);

        let systemPrompt = CONTEXT_PROMPT_COMMUNITY + "\n\n";
        systemPrompt += "The student is currently working on a lesson titled: " + lessonId + "\n\n";
        systemPrompt += "The student is currently looking at " + currContent + "\n\n";
        systemPrompt += INSTRUCTIONS_PROMPT + "\n\n";

        if (isPersonified) {
            systemPrompt += PERSONIFIED_EXPLANATION;
        } else {
            systemPrompt += TOOL_EXPLANATION;
        }

        // Prepend a system prompt to the messages
        const messagesPrompt = [{
            role: "system",
            content: systemPrompt
        },
        ...messages];

        // Call the chat completions API
        const content = await callGPTChat("gpt-4", messagesPrompt, undefined, MAX_TOKENS);

        // Add the response to the database
        const replyInfo = { messageId: messageId, content: query, authorName: userName }
        await storeMessage("community", "ai", aiName, "assistant", content, currSlideId, replyInfo, lessonId, {});

        return content;
    }
);
