import * as functions from "firebase-functions";
import * as admin from "firebase-admin";
import { parseTipTap, TipTapContent } from "./tiptap_parser";
import { hasCompletedItem, hasCompletedAssignment } from "./user_progress";
import { LookupMaterial } from "./course_material_types";

// Functions for retrieving data from the database

// Retrieve the content of a worked example from firestore
// Returns an object with the content, url, and whether the user has completed this item
const retrieveCodeExample = async (userId: string, item: any) => {
    const contentRef = admin.firestore().collection("lessons").doc("public").collection("lessonsList").doc(item["lessonId"]).collection("itemsList").doc(item["docId"]);
    const content = await contentRef.get();
    const contentData = content.data();
    if (!contentData) {
        return null;
    }
    const contentUrl = contentData["url"];
    const exampleRef = admin.firestore().collection("assns").doc("public").collection("assignments").doc(contentUrl).collection("docs").doc("prompt");
    const example = await exampleRef.get();
    const exampleData = example.data();
    if (!exampleData) {
        return null;
    }

    let result = parseTipTap(exampleData.content as TipTapContent);

    // Download the code from /soln or /starterCode if it exists
    const codeRef = admin.firestore().collection("assns").doc("public").collection("assignments").doc(contentUrl).collection("docs").doc("soln");
    const code = await codeRef.get();
    const codeData = code.data();
    if (codeData) {
        result += "\n\n" + parseTipTap(codeData.content as TipTapContent);
    } else {
        const starterCodeRef = admin.firestore().collection("assns").doc("public").collection("assignments").doc(contentUrl).collection("docs").doc("starterCode");
        const starterCode = await starterCodeRef.get();
        const starterCodeData = starterCode.data();
        if (starterCodeData) {
            result += "\n\n" + parseTipTap(starterCodeData.content as TipTapContent);
        }
    }

    functions.logger.log("CODE EXAMPLE", result);
    const hasCompleted = await hasCompletedItem(userId, item["lessonId"], item["docId"])

    const url = `https://codeinplace.stanford.edu/public/ide/a/${contentUrl}`;
    return { content: result, url: url, hasCompleted: hasCompleted };
}

// Retrieve the transcript of a lecture video from firestore
// Returns an object with the content, url, and whether the user has completed this item
const retrieveLectureVideo = async (userId: string, item: any) => {
    const transcriptRef = admin.firestore().collection("transcripts").doc(item["lessonId"]).collection("items").doc(item["docId"]);
    const transcript = await transcriptRef.get();
    const transcriptData = transcript.data();
    if (!transcriptData) {
        return null;
    }

    const url = `https://codeinplace.stanford.edu/public/learn/${item["lessonId"]}/${item["docId"]}`
    const result = transcriptData.transcript.map((content: any) => content.text).join("\n");
    functions.logger.log("LECTURE VIDEO", result);
    const hasCompleted = await hasCompletedItem(userId, item["lessonId"], item["docId"])
    return { content: result, url: url, hasCompleted: hasCompleted };
}

// Retrieve the content of a Python textbook chapter from firestore
// Returns an object with the content, url, and whether the user has completed this item
const retrievePythonTextbookChapter = async (userId: string, item: any) => {
    const chapterRef = admin.firestore().collection("lessons").doc("public").collection("lessonsList").doc(item["lessonId"]).collection("itemsList").doc(item["docId"]);
    const chapter = await chapterRef.get();
    const chapterData = chapter.data();
    if (!chapterData) {
        return null;
    }

    const stored_url = chapterData["url"];
    if (stored_url.includes("compedu")) {
        return null;
    }
    const file_name = stored_url.split("/").pop();
    const fileRef = admin.firestore().collection("textbook").doc("public").collection("chapters").doc(file_name);
    const file = await fileRef.get();
    const fileData = file.data();
    if (!fileData) {
        return null;
    }

    const result = parseTipTap(fileData.content as TipTapContent);
    functions.logger.log("TEXTBOOK CHAPTER", result);
    const url = `https://codeinplace.stanford.edu/public/textbook/${file_name}`
    const hasCompleted = await hasCompletedItem(userId, item["lessonId"], item["docId"]) // This will always be false because readings never have completion
    return { content: result, url: url, hasCompleted: hasCompleted };
}

// Retrieve the content of a Karel textbook chapter from firestore
// Returns an object with the content, url, and whether the user has completed this item
const retrieveKarelTextbookChapter = async (userId: string, item: any) => {
    const chapterRef = admin.firestore().collection("karel_textbook").doc(item["docId"]);
    const chapter = await chapterRef.get();
    const chapterData = chapter.data();
    if (!chapterData) {
        return null;
    }

    const content = chapterData["content"];
    functions.logger.log("KAREL CHAPTER", content);
    const url = chapterData["url"];
    const hasCompleted = await hasCompletedItem(userId, item["lessonId"], item["docId"]) // SAME HERE - oh wait maybe its fine because lessons do have 
    return { content: content, url: url, hasCompleted: hasCompleted };
}

// Retrieve the specified documentation from firestore
// Returns an object with the content. 
// No url is provided for documentation, and we assume the user has always completed this item
const retrieveDocumentation = async (item: any) => {
    const docRef = admin.firestore().collection("docs").doc("public").collection("libraries").doc(item["lessonId"]);
    const doc = await docRef.get();
    const docData = doc.data();
    if (!docData) {
        return null;
    }

    const result = parseTipTap(docData.content as TipTapContent);
    functions.logger.log("DOCUMENTATION", result);
    return { content: result, url: null, hasCompleted: true }; // no url for documentation
}

// Retrieve the about page this this repo (hardcoded)
// Returns an object with the content, url, and we assume the user has always completed this item
// const retrieveAbout = async () => {
// 	return { content: ABOUT_PAGE, url: ABOUT_URL, hasCompleted: true };
// }

// Retrieve the content of an assignment from firestore
// Returns an object with the content, url, and whether the user has completed this item
const retrieveAssignment = async (userId: string, item: any) => {
    const assignmentRef = admin.firestore().collection("assns").doc("public").collection("assignments").doc(item["docId"]).collection("docs").doc("prompt");
    const assignment = await assignmentRef.get();
    const assignmentData = assignment.data();
    if (!assignmentData) {
        return null;
    }

    const url = `https://codeinplace.stanford.edu/public/ide/a/${item["docId"]}`;
    const result = parseTipTap(assignmentData.content as TipTapContent);
    functions.logger.log("ASSIGNMENT", result);
    const hasCompleted = await hasCompletedAssignment(userId, item["docId"])
    return { content: result, url: url, hasCompleted: hasCompleted };
}

// Retrieve the specified item's content, url, and whether the user has completed this item
export const retrieve_item = async (userId: string, item: LookupMaterial) => {
    switch (item["type"]) {
        case "code example":
            return await retrieveCodeExample(userId, item);
        case "lecture video":
            return await retrieveLectureVideo(userId, item);
        case "python textbook chapter":
            return await retrievePythonTextbookChapter(userId, item);
        case "karel textbook chapter":
            return await retrieveKarelTextbookChapter(userId, item);
        case "code documentation":
            return await retrieveDocumentation(item);
        // case "about page":
        // 	return await retrieveAbout();
        case "assignment":
            return await retrieveAssignment(userId, item);
        default:
            // This should never happen
            functions.logger.error("Invalid item type in context_json (likely due to invalid return by GPT)", item["type"]);
            return null;
    }
}