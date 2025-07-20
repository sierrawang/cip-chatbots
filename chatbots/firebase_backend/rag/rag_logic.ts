import * as functions from "firebase-functions";
import { MAX_TOKENS, callGPTChat } from "../chat_openai_client";
import { CONTEXT_PROMPT, GENERATION_PROMPT1, GENERATION_PROMPT2, GENERATION_PROMPT3, INSTRUCTIONS_PROMPT, PERSONIFIED_EXPLANATION, RETRIEVAL_PROMPT1, RETRIEVAL_PROMPT2, TOOL_EXPLANATION } from "../chat_prompts";
import { MATERIALS_LOOKUP_TABLE } from "./course_material_lookup_table";
import { prioritizeMaterials } from "./course_material_selection";
import { retrieve_item } from "./retrieval_functions";
import { CourseMaterial, LookupMaterial, MaterialDescription } from "./course_material_types";

// Logic that performs the context retrieval and generation of grounded responses

// (3) Generate a JSON of the relevant context to answer these messages
const generateContextJSON = async (messages: any, currContent: string) => {
	const system_prompt = `${RETRIEVAL_PROMPT1}\n${currContent}\n\n${RETRIEVAL_PROMPT2}`;

	const retrieval_prompt = [{
		role: "system",
		content: system_prompt
	},
	...messages];

	// Call the chat completions API
	const context = await callGPTChat("gpt-4-0125-preview", retrieval_prompt, true, MAX_TOKENS);
	functions.logger.log("returned context", context);

	try {
		const context_json = JSON.parse(context);
		functions.logger.log("context_json", context_json);
		return context_json;
	} catch (error) {
		functions.logger.error("Failed to parse context JSON:", error);
		return {};
	}
}

// (6)
// Return a list of the retrieved relevant context based on the provided json
// Specifically, returns the content, url, title, type, and whether the user has completed each item
const getContextFromDatabase = async (userId: string, prioritized_materials: LookupMaterial[]) => {
	// Each element of context_json defines a document in the database that we need to retrieve
	const results: Array<{ content: string; url: any; hasCompleted: boolean; title: string; type: string }> = [];
	for (const item of prioritized_materials) {
		const result = await retrieve_item(userId, item);
		if (result) {
			const context = { ...result, title: item["title"], type: item["type"] };
			results.push(context);
		}
	}
	return results;
}

// (4)
const lookupMaterials = (item: MaterialDescription): LookupMaterial[] => {
	let materials: LookupMaterial[] = [];
	const lookup_materials = MATERIALS_LOOKUP_TABLE.filter(
		(material: LookupMaterial) => material.type === item.type && material.tags === item.concept
	);
	materials = materials.concat(lookup_materials);
	return materials;
}

// (2)
// 1. Determines the relevant context for the student's query
// 2. Returns a list of the pieces of relevant context 
//    (content, url, title, type, and whether the user has completed each item)
const retrieveRelevantContext = async (userId: string, messages: any, lessonId: string, currContent: string) => {
	const context_json = await generateContextJSON(messages, currContent);

	// If the context_json does not contain a "shouldReference" field, or if it is false, return an empty list
	if (!("shouldReference" in context_json) || !context_json["shouldReference"] || !context_json["materials"]) {
		return [];
	}

	// Look up the materials based on the returned JSON
	const materials = lookupMaterials(context_json["materials"]);
	functions.logger.log("materials", materials);

	// Prioritize the materials based on the lesson
	const prioritized_materials = prioritizeMaterials(materials, lessonId);
	functions.logger.log("prioritized_materials", prioritized_materials);

	// Retrieve the relevant context from the database
	const context = await getContextFromDatabase(userId, prioritized_materials);
	functions.logger.log("context", context);

	return context;
}

// Construct a prompt which incorporates the relevant context,
// this prompt is used to generate a grounded response
const constructGenerationPrompt = (materials: CourseMaterial[], currContent: string, isPersonified: boolean): string => {
	let prompt = CONTEXT_PROMPT + "\n\n";
	prompt += GENERATION_PROMPT1;
	prompt += currContent + "\n\n";

	if (materials.length > 0) {
		prompt += GENERATION_PROMPT2;
		for (const material of materials) {
			const content = material.content.replace(/&#39;/g, "'");
			prompt += `
        {
            "title": "${material.title}",
            "type": "${material.type}",
            "url": "${material.url}",
            "hasCompleted": "${material.hasCompleted}"
            "content": "${content}"
        },`
		}
		prompt += "\n\n";

		prompt += GENERATION_PROMPT3 + "\n\n";
	} else {
		prompt += INSTRUCTIONS_PROMPT + "\n\n";
	}

	if (isPersonified) {
		prompt += PERSONIFIED_EXPLANATION;
	} else {
		prompt += TOOL_EXPLANATION;
	}

	return prompt;
}

// Call GPT to generate the final (grounded) response
const generateResponse = async (systemPrompt: string, messages: any) => {
	const generation_prompt = [{
		role: "system",
		content: systemPrompt
	},
	...messages];

	// Call the chat completions API
	const response = await callGPTChat("gpt-4", generation_prompt, undefined, MAX_TOKENS);
	return response;
}

// (1) This function generates a grounded response based on the chat conversation.
export const generateGroundedResponse = async (userId: string, messages: any, currContent: string, lessonId: string, isPersonified: boolean) => {
	// Retrieve the relevant context from the database (code in place firestore)
	const relevantContext = await retrieveRelevantContext(userId, messages, lessonId, currContent);

	// Construct a prompt which incorporates the relevant context
	const systemPrompt = constructGenerationPrompt(relevantContext, currContent, isPersonified);

	// Call GPT to generate a response
	const response = await generateResponse(systemPrompt, messages);
	return response;
}
