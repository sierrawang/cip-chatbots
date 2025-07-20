// This button toggles the chat feature on and off for the public course.
// The button only works for Sierra, TJ, and Chris.

import { doc, getDoc, getFirestore } from "firebase/firestore";
import { getFunctions, httpsCallable } from "firebase/functions";
import { useEffect, useState } from "react";

const functions = getFunctions();
const setChatRolloutFlag = httpsCallable(functions, "setChatRolloutFlag");
const canToggleRollout = httpsCallable(functions, "canToggleRollout");

export const PublicRolloutButton = () => {
    const [validUser, setValidUser] = useState(false);
    const [currentRolloutFlag, setCurrentRolloutFlag] = useState(false);

    // Load the current rollout flag value from the database
    useEffect(() => {
        const loadRolloutFlag = async () => {
            try {
                const db = getFirestore();
                const rolloutRef = doc(db, "chatRollOut", "rollout");
                const rolloutDoc = await getDoc(rolloutRef);
                const rolloutData = rolloutDoc.data();
                console.log(rolloutData);
                setCurrentRolloutFlag(rolloutData.rolloutFlag);
            } catch (e) {
                console.error(e);
            }
        }
        loadRolloutFlag();
    }, []);

    // Determine whether the current user can toggle the rollout flag
    useEffect(() => {
        const checkUser = async () => {
            try {
                const res = await canToggleRollout();
                setValidUser(res.data === true); // Force boolean for type checker
            } catch (e) {
                console.error(e);
            }
        }
        checkUser();
    }, []);

    // Toggle the rollout flag in the database
    const toggleRolloutFlag = async () => {
        try {
            const newRolloutFlag = !currentRolloutFlag;
            // Update the flag in the database
            const res = await setChatRolloutFlag({ flag: newRolloutFlag });
            if (res.data) {
                // Update the state
                setCurrentRolloutFlag(newRolloutFlag);
            }
        } catch (e) {
            console.error(e);
        }
    }

    const renderRolloutFlag = () => {
        if (currentRolloutFlag) {
            return "On";
        } else {
            return "Off";
        }
    }

    if (!validUser) {
        return null;
    } else {
        return (
            <button
                onClick={toggleRolloutFlag}
                className="btn btn-light mr-1"
                style={{
                    marginTop: "10px",
                }}>
                Toggle Public Chat Rollout Flag: {renderRolloutFlag()}
            </button>
        );
    }
}
