import * as admin from "firebase-admin";

// Functions for determining user progress

// Determine whether the user has completed the lesson item
export const hasCompletedItem = async (userId: string, lessonId: string, docId: string) => {
    // Return true if lessonId is null
    if (!lessonId) {
        return true;
    }

    // Look up the student's progress in the database
    const completionRef = admin.firestore().collection("users").doc(userId).collection("cip4").doc("lessonsProgress")
    const completion = await completionRef.get();
    const completionData = completion.data();
    if (!completionData) {
        // The student has not completed any items
        return false;
    } else if (completionData[lessonId]) {
        // The student has completed the entire lesson
        return true;
    } else if (completionData[`${lessonId}/${docId}`]) {
        // The student has completed the specific slide
        return true;
    } else {
        // The student has not completed the item
        return false;
    }
}

// Determine whether the user has completed the assignment
export const hasCompletedAssignment = async (userId: string, docId: string) => {
    const completionRef = admin.firestore().collection("users").doc(userId).collection("cip4").doc("assnProgress")
    const completion = await completionRef.get();
    const completionData = completion.data();
    if (!completionData) {
        return false;
    }
    return completionData[docId];
}