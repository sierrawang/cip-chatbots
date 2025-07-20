// firebase functions for controlling slow rollout of the chat in the public course
import * as functions from "firebase-functions";
import * as admin from "firebase-admin";

const sierraUid = "l04twJpALibcNjVdSWWEeBuAYC72";
const tjUid = "ZpLvkKW72JgHrq9bJWeovNXLfsi1";
const chrisUid = "9fLSKXY6QXdMSRpl2osilNDoKV73";

// Only allow Sierra, TJ, and Chris to toggle the chat rollout flag
export const canToggleRollout = functions.https.onCall(
    async (
        data: any,
        context
    ) => {
        functions.logger.log("canToggleRollout called", data);

        // Only Sierra, TJ, and Chris can set the chat rollout flag
        const userId = context.auth?.uid;
        if (!userId || (userId !== sierraUid && userId !== tjUid && userId !== chrisUid)) {
            return false;
        } else {
            return true;
        }
    }
);

// Set the chat rollout flag (stored at /chatRollOut/rollout in the field rolloutFlag)
export const setChatRolloutFlag = functions.https.onCall(
    async (
        data: { flag: boolean },
        context
    ) => {
        // Only Sierra, TJ, and Chris can set the chat rollout flag
        const userId = context.auth?.uid;
        if (!userId || (userId !== sierraUid && userId !== tjUid && userId !== chrisUid)) {
            return false;
        }

        // Update the chat rollout flag in the database
        const { flag } = data;
        await admin.firestore().doc("/chatRollOut/rollout").set({ rolloutFlag: flag }, { merge: true });

        return true;
    }
);

// Add a user to the chat rollout (stored at /chatRollOut/rollout in the field users list)
export const addUserToChatRollout = functions.https.onCall(
    async (
        data,
        context
    ) => {
        // Verify that the user is authenticated
        const uid = context.auth?.uid;
        if (!uid) {
            return false;
        }

        const chatRollout = await admin.firestore().doc("/chatRollOut/rollout").get();
        if (chatRollout.exists) {
            const chatRolloutData = chatRollout.data()!;

            // Verify that the chatRollout flag is set
            if (!chatRolloutData.rolloutFlag) {
                return false;
            }

            // Add the user to the chat rollout users list (if not already present)
            const { userId } = data;
            const users = chatRolloutData.users;
            if (!users.includes(userId)) {
                users.push(userId);
                await admin.firestore().doc("/chatRollOut/rollout").set({ users: users }, { merge: true });
            }
            return true;
        } else {
            return false;
        }
    }
);