// This is the thumbs up/thumbs down rating component for messages in the chat

import { useUserId } from "hooks/user/useUserId";
import { useEffect, useState } from "react";
import { isCommunity, isIDE, isNoChat } from "./ChatConstants";
import { doc, getFirestore, updateDoc } from "firebase/firestore";
import { useParams } from "react-router";
import { MessageButton, MessageButtonContainer, MessageP } from "./ChatStyles";
import { IoIosThumbsUp, IoIosThumbsDown } from "react-icons/io";

const RATING_CONSTANTS = {
    LIKE: 1,
    DISLIKE: -1,
    NONE: 0
};

export const MessageRating = ({ message, chatType, chatMessages }) => {
    const db = getFirestore();
    const userId = useUserId();

    const { urlKey, lessonId, slideId } = useParams();
    const [rating, setRating] = useState(message.ratings[userId]);

    // Update the rating if this user has rated this message
    useEffect(() => {
        if (message.ratings[userId]) {
            setRating(message.ratings[userId]);
        }
    }, [message]);

    // Set the rating for the message in firebase
    const updateRating = (rate) => async () => {
        if (isNoChat(chatType)) {
            // This should never happen
            console.error("MessageRating - Chat type is null");
            return;
        }

        let messageRef;
        if (isIDE(chatType)) {
            // Update the message at chatHistory/{userId}/assns/{urlKey}/messages/{messageId}
            messageRef = doc(db, "chatHistory", userId, "assns", urlKey, "messages", message.id);
        } else {
            // Update the message at chatHistory/{userId}/lessons/{lessonId}/messages/{messageId}
            const lessonKey = lessonId ? lessonId : slideId;
            messageRef = doc(db, "chatHistory", userId, "lessons", lessonKey, "messages", message.id);
        }

        // Update the rating in the frontend for community chat users 
        // since they are not listening to their individual collections
        if (isCommunity(chatType)) {
            const messageIndex = chatMessages.findIndex((msg) => msg.id === message.id);
            chatMessages[messageIndex].ratings[userId] = rate;
            setRating(rate);
        }

        // Update the rating in the database
        const userRating = `ratings.${userId}`;
        await updateDoc(messageRef, { [userRating]: rate });
    };

    if (rating) {
        return (
            <MessageButtonContainer>
                <MessageP>Your rating:</MessageP>
                <MessageButton style={{ cursor: "default" }}>
                    {rating === RATING_CONSTANTS.LIKE ? <IoIosThumbsUp /> : <IoIosThumbsDown />}
                </MessageButton>
            </MessageButtonContainer>
        );
    } else {
        return (
            <MessageButtonContainer>
                <MessageP>Rate this response</MessageP>
                <MessageButton
                    onClick={updateRating(RATING_CONSTANTS.LIKE)}
                    className="btn btn-light mr-1">
                    <IoIosThumbsUp />
                </MessageButton>
                <MessageButton
                    onClick={updateRating(RATING_CONSTANTS.DISLIKE)}
                    className="btn btn-light mr-1">
                    <IoIosThumbsDown />
                </MessageButton>
            </MessageButtonContainer>
        );
    }
}