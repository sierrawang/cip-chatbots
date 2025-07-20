import * as functions from "firebase-functions";
import { contructMessages, storeMessage, storeIDEMessage, checkNumLessonMessages, MESSAGES_LIMIT, checkNumAssnMessages, incrementNumMessagesLessons, incrementNumMessagesAssns, FLAGGED_POST } from "./chat_helper_functions";
import { MAX_TOKENS, callGPTChat } from "./chat_openai_client";
import { generateGroundedResponse } from "./rag/rag_logic";
import { AUTO_AI_PROMPT, CONTEXT_PROMPT, EXPLAIN_DIFFERENTLY_PROMPT, INSTRUCTIONS_PROMPT, SUMMARIZE_PROMPT, WHY_IT_MATTERS_PROMPT } from "./chat_prompts";
import { getModeration } from "../gpt_functions";


// This is the endpoint for the basic chatbot: 
// It generates a response to the user using a relatively simple prompt and GPT-4.
export const basicChatEndpoint = functions.https.onCall(
    async (
        data: { chatMessages: any, query: string, lessonId: string, currSlideId: string, userName: string, aiName: string, currContent: string },
        context
    ) => {
        // Make sure the user is authenticated
        const userId = context.auth?.uid;
        if (!userId) { return "" }

        const { chatMessages, query, lessonId, currSlideId, userName, aiName, currContent } = data;

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
        systemPrompt += INSTRUCTIONS_PROMPT;

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
export const groundedChatEndpoint = functions.https.onCall(
    async (
        data: { chatMessages: any, query: string, currSlideId: string, lessonId: string, userName: string, aiName: string, currContent: string },
        context
    ) => {
        functions.logger.log("A. groundedChatEndpoint");

        // Make sure the user is authenticated
        const userId = context.auth?.uid;
        if (!userId) { return "" }

        const { chatMessages, query, lessonId, currSlideId, userName, aiName, currContent } = data;

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
        const response = await generateGroundedResponse(userId, messages, currContent, lessonId, false);

        // Add the response to the database
        await storeMessage(userId, "ai", aiName, "assistant", response, currSlideId, null, lessonId, {});

        return response;
    }
);

// This is the endpoint for the explain differently chatbot button:
// It generates an alternative explanation of the current content that the user is viewing.
export const explainDifferentlyEndpoint = functions.https.onCall(
    async (
        data: { aiName: string, lessonId: string, currSlideId: string, content: string, userName: string, query: string },
        context
    ) => {
        // Make sure the user is authenticated
        const userId = context.auth?.uid;
        if (!userId) { return "" }

        const { aiName, lessonId, currSlideId, content, userName, query } = data;

        // Add the user's most recent message to the database
        await storeMessage(userId, userId, userName, "user", query, currSlideId, null, lessonId, {});
        await incrementNumMessagesLessons(userId, lessonId);

        // Check the number of messages for this lesson
        if (await checkNumLessonMessages(userId, lessonId)) {
            return MESSAGES_LIMIT;
        }

        // Generate a summary
        const prompt = [{
            role: "system",
            content: EXPLAIN_DIFFERENTLY_PROMPT
        },
        { role: "user", content: content }];

        // Call the chat completions API
        const response = await callGPTChat("gpt-4", prompt, undefined, MAX_TOKENS);
        await storeMessage(userId, "ai", aiName, "assistant", response, currSlideId, null, lessonId, {});

        return response;
    }
);

// This is the endpoint for the summary chatbot button:
// It generates a summary of the current content that the user is viewing.
export const getSummary = functions.https.onCall(
    async (
        data: { aiName: string, lessonId: string, currSlideId: string, content: string, userName: string, query: string },
        context
    ) => {
        // Make sure the user is authenticated
        const userId = context.auth?.uid;
        if (!userId) { return "" }

        const { aiName, lessonId, currSlideId, content, userName, query } = data;

        // Add the user's most recent message to the database
        await storeMessage(userId, userId, userName, "user", query, currSlideId, null, lessonId, {});
        await incrementNumMessagesLessons(userId, lessonId);

        // Check the number of messages for this lesson
        if (await checkNumLessonMessages(userId, lessonId)) {
            return MESSAGES_LIMIT;
        }

        // Generate a summary
        const prompt = [{
            role: "system",
            content: SUMMARIZE_PROMPT
        },
        { role: "user", content: content }];

        // Call the chat completions API
        const response = await callGPTChat("gpt-4", prompt, undefined, MAX_TOKENS);
        await storeMessage(userId, "ai", aiName, "assistant", response, currSlideId, null, lessonId, {});

        return response;
    }
);

// This is the endpoint for the why does it matter chatbot button:
// It generates an explanation of why the current content is important.
export const whyItMatters = functions.https.onCall(
    async (
        data: { aiName: string, lessonId: string, currSlideId: string, content: string, userName: string, query: string },
        context
    ) => {
        // Make sure the user is authenticated
        const userId = context.auth?.uid;
        if (!userId) { return "" }

        const { aiName, lessonId, currSlideId, content, userName, query } = data;

        // Add the user's most recent message to the database
        await storeMessage(userId, userId, userName, "user", query, currSlideId, null, lessonId, {});
        await incrementNumMessagesLessons(userId, lessonId);

        // Check the number of messages for this lesson
        if (await checkNumLessonMessages(userId, lessonId)) {
            return MESSAGES_LIMIT;
        }

        // Generate a summary
        const prompt = [{
            role: "system",
            content: WHY_IT_MATTERS_PROMPT
        },
        { role: "user", content: content }];

        // Call the chat completions API
        const response = await callGPTChat("gpt-4", prompt, undefined, MAX_TOKENS);
        await storeMessage(userId, "ai", aiName, "assistant", response, currSlideId, null, lessonId, {});

        return response;
    }
);

// This is the endpoint for the IDE chatbot:
// It generates a response to the user using a relatively simple prompt and GPT-4.
export const ideChatEndpoint = functions.https.onCall(
    async (
        data: { chatMessages: any, query: string, assnId: string, userName: string, aiName: string, code: string, assnPrompt: string },
        context
    ) => {
        // Make sure the user is authenticated
        const userId = context.auth?.uid;
        if (!userId) { return "" }

        const { chatMessages, query, assnId, userName, aiName, code, assnPrompt } = data;

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
        systemPrompt += INSTRUCTIONS_PROMPT;

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

// This is the endpoint for the community chat:
// It first ensures that the user's query is appropriate, adds the query to the database,
// decides whether the AI should respond, and if so, adds the AI's response to the database.
export const communityChatEndpoint = functions.https.onCall(
    async (
        data: {
            chatMessages: any,
            query: string,
            lessonId: string,
            currSlideId: string,
            userName: string,
            aiName: string,
            replyTo: any
        },
        context
    ) => {
        // Make sure the user is authenticated
        const userId = context.auth?.uid;
        if (!userId) { return "" }

        const { chatMessages, query, lessonId, currSlideId, userName, aiName, replyTo } = data;

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

        // Prepend a system prompt to the messages
        const messages_prompt = [{
            role: "system",
            content: AUTO_AI_PROMPT
        },
        ...messages];

        // Call the chat completions API
        const response = await callGPTChat("gpt-4-0125-preview", messages_prompt, true, MAX_TOKENS);

        // Parse the response to see whether the AI chose to respond
        // If the AI chose to respond, add the response to the database
        try {
            const results = JSON.parse(response);
            if (results["respond"]) {
                const content = results["response"];
                const replyInfo = { messageId: messageId, content: query, authorName: userName }
                await storeMessage("community", "ai", aiName, "assistant", content, currSlideId, replyInfo, lessonId, {});
                return content;
            }
        } catch (e) {
            functions.logger.error("autoAIResponse - error parsing response", e);
        }

        return ""
    }
);
