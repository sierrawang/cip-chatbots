import OpenAI from "openai";
import * as functions from "firebase-functions";
import { ChatCompletionCreateParams } from "openai/resources";

export const openaiClient = new OpenAI({
    organization: "",
    apiKey: ""
});

// The maximum number of messages to send to GPT
const MESSAGES_LIMIT = 10;

// Max number of tokens for the GPT response
export const MAX_TOKENS = 256;

// Reduce the length of the messages to the last MESSAGES_LIMIT messages
const reduceMessages = (messages: any) => {
    if (messages.length <= MESSAGES_LIMIT) {
        return messages;
    }

    // Return the first message + the last MESSAGES_LIMIT - 1 messages
    return [messages[0], ...messages.slice(messages.length - MESSAGES_LIMIT + 1)];
}

// Replace all instances of "Carol" with "Karel"
// Using a regular expression to find "carol" as a whole word, case insensitive
function replaceCarol(input: string): string {
    return input.replace(/\bcarol\b/gi, "Karel");
}

function replaceMaron(input: string): string {
    return input.replace(/\bmaron\b/gi, "Mehran");
}

// Call the GPT chat API
export const callGPTChat = async (model: string, messages: any, jsonResponse?: boolean, max_tokens?: number) => {
    try {
        // Reduce the length of the messages to the last 10 messages
        const reducedMessages = reduceMessages(messages);

        // TO DO - add a way to make sure the length of the messages is short enough!

        const prompt: ChatCompletionCreateParams = {
            messages: reducedMessages,
            model: model
        };

        // Add the max_tokens and response_format if they are provided
        if (max_tokens) {
            prompt.max_tokens = max_tokens;
        }
        if (jsonResponse) {
            prompt.response_format = { type: "json_object" };
        }

        functions.logger.info("callGPTChat", prompt);
        const completion = await openaiClient.chat.completions.create(prompt);

        // Parse the response and return the content
        const choice = completion.choices[0];
        const content = choice?.message?.content || "";

        // String replace instances of "Carol" with "Karel"
        let result = replaceCarol(content);

        // String replace instances of "Maron" with "Mehran"
        result = replaceMaron(result);
        
        functions.logger.info("callGPTChat result", result);

        return result;
    }
    catch (error) {
        functions.logger.error("Error in callGPTChat", error);
        return "I'm sorry, there is an error with the chat service. Please try again later!";
    }
}