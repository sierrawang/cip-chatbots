import * as admin from "firebase-admin";

// Format the chat messages into the format needed by GPT
export const contructMessages = (chatMessages: any, query: string) => {
    const messages = chatMessages.reverse().map((message: any) => {
        return {
            role: message.role,
            content: message.content
        };
    });
    messages.push({ role: "user", content: query });

    return messages;
}

// The maximum number of messages that a user can send to GPT in one lesson
const MAX_NUMBER_OF_MESSAGES = 200;

// Flag when the user has sent too many messages
export const MESSAGES_LIMIT = "MESSAGE_LIMIT";

// Flag when the user has sent an inappropriate message
export const FLAGGED_POST = "FLAGGED_POST";

// Get the number of messages made by this user for this lesson.
const getNumLessonMessages = async (userId: string, lessonId: string) => {
    const chatRef = admin.firestore().collection("chatHistory").doc(userId).collection("lessons").doc(lessonId);
    const doc = await chatRef.get();
    if (!doc.exists) {
        return 0;
    }
    const data = doc.data();
    return data?.numMessages || 0;
}

// Get the number of messages made by this user for this assignment.
const getNumAssnMessages = async (userId: string, assnId: string) => {
    const chatRef = admin.firestore().collection("chatHistory").doc(userId).collection("assns").doc(assnId);
    const doc = await chatRef.get();
    if (!doc.exists) {
        return 0;
    }
    const data = doc.data();
    return data?.numMessages || 0;
}

// Check whether the user has sent too many messages for a lesson
export const checkNumLessonMessages = async (userId: string, lessonId: string) => {
    const numMessages = await getNumLessonMessages(userId, lessonId);
    return numMessages > MAX_NUMBER_OF_MESSAGES;
}

// Check whether the user has sent too many messages for an assignment
export const checkNumAssnMessages = async (userId: string, assnId: string) => {
    const numMessages = await getNumAssnMessages(userId, assnId);
    return numMessages > MAX_NUMBER_OF_MESSAGES;
}

// Increment the number of messages made by this user for this lesson.
export const incrementNumMessagesLessons = async (userId: string, lessonId: string) => {
    const chatRef = admin.firestore().collection("chatHistory").doc(userId).collection("lessons").doc(lessonId);
    await chatRef.set({ numMessages: admin.firestore.FieldValue.increment(1) }, { merge: true });
}

// Increment the number of messages made by this user for this assignment.
export const incrementNumMessagesAssns = async (userId: string, assnId: string) => {
    const chatRef = admin.firestore().collection("chatHistory").doc(userId).collection("assns").doc(assnId);
    await chatRef.set({ numMessages: admin.firestore.FieldValue.increment(1) }, { merge: true });
}

// Store a message in the database
export const storeMessage = async (userId: string, authorId: string, userName: string, role: string, content: string, currSlideId: string, replyTo: any, lessonId: string, ratings: any) => {
    const chatRef = admin.firestore().collection("chatHistory").doc(userId).collection("lessons").doc(lessonId).collection("messages");
    const docRef = await chatRef.add({
        authorId: authorId,
        authorName: userName,
        role: role,
        content: content,
        currSlideId: currSlideId,
        replyTo: replyTo,
        timestamp: admin.firestore.FieldValue.serverTimestamp(),
        ratings: ratings
    });

    return docRef.id;
}

// Store a message in the database
export const storeIDEMessage = async (userId: string, authorId: string, userName: string, role: string, content: string, assnId: string, ratings: any) => {
    const chatRef = admin.firestore().collection("chatHistory").doc(userId).collection("assns").doc(assnId).collection("messages");
    await chatRef.add({
        authorId: authorId,
        authorName: userName,
        role: role,
        content: content,
        timestamp: admin.firestore.FieldValue.serverTimestamp(),
        ratings: ratings
    });
}
