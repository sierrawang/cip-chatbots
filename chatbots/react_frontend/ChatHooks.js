import { useEffect, useRef, useState } from "react";
import { query, collection, doc, getFirestore, orderBy, getDocs, startAfter, limit, getDoc, setDoc, onSnapshot } from "firebase/firestore";
import { AI_ID, CHATBOT_NAME, CHAT_INTRO_SLIDE_ID, CHAT_ROLES, CHAT_TYPES, MESSAGE_RETRIEVAL_LIMIT, NUM_CHATS, isBasic, isButtons, isCommunity, isGrounded, isIDE, isNoChat } from "./lessonchats/ChatConstants";
import { useUserId } from "hooks/user/useUserId";
import firebase from "firebase/compat/app";
import { useParams } from "react-router";
import { getFunctions, httpsCallable } from "firebase/functions";
import { hashString } from 'react-hash-string'

const functions = getFunctions();
const addUserToChatRollout = httpsCallable(functions, "addUserToChatRollout");

// 0: null, // No chat
// 1: grounded
// 2: grounded personified
// 3: basic
// 4: basic personified
// 5: community
// 6: community personified
// 7: buttons
// 8: buttons personified
// 9: ide
// 10: ide personified
export const getChatType = async (courseId) => {
    try {
        const db = getFirestore();
        const userId = useUserId();

        // Load user's chat type at /chatHistory/{userId} chatType field
        const userChatDocRef = doc(db, "chatHistory", userId);
        const userChatDoc = await getDoc(userChatDocRef);
        const userChatData = userChatDoc.data();
        if (userChatData && userChatData.chatType) {
            console.log("Found chat type in chat history", userChatData.chatType)
            return userChatData.chatType;
        }

        // Retrieve the user's sectionId
        const userDocRef = doc(db, "users", userId);
        const userDoc = await getDoc(userDocRef);
        const userDocData = userDoc.data();
        if (!userDocData || !userDocData.sections || !userDocData.sections[courseId]) {
            console.log("User does not have a sectionId");
            return 0;
        }

        // Compute the chat type based on the user's sectionId
        const sections = userDocData.sections;
        const sectionRef = sections[courseId][0];
        const sectionDoc = await getDoc(sectionRef);
        const sectionId = sectionDoc.id;
        const key = sectionId + "saltychat";
        const chatType = Math.abs(hashString(key)) % NUM_CHATS;
        console.log("Computed chat type", chatType);

        // Store the chat type in the user's chat history
        await setDoc(userChatDocRef, { chatType }, { merge: true });
        console.log("Stored chat type in chat history");

        // Return the chat type
        return chatType;

    } catch (e) {
        console.error(e);
        return 0;
    }
}

// Return whether the user is part of the public chat rollout if 
// (1) The chat rollout flag is currently set to true or
// (2) They were already added to the chat rollout
export const isChatRollout = async (userId) => {
    try {
        const db = getFirestore();

        // Rollout info is stored at /chatRollOut/rollout
        const rolloutRef = doc(db, "chatRollOut", "rollout");
        const rolloutDoc = await getDoc(rolloutRef);

        // This should definitely exist - Sierra
        if (rolloutDoc.exists()) {
            const rolloutData = rolloutDoc.data();

            // Get the list of users in the rollout
            const rolloutUsers = rolloutData.users;

            // Check if the user is in the rollout
            const userIndex = rolloutUsers.findIndex(user => user === userId);
            const userExists = userIndex !== -1;
            if (userExists) {
                // If the user is already in the rollout, return true
                return true;
            } else if (rolloutData.rolloutFlag) {
                // If the user is not in the rollout, but the rollout flag is set to true, 
                // add the user to the rollout and return true.
                const added = await addUserToChatRollout({ userId: userId });
                return added.data === true; // Force boolean (for the type checker, even though it is boolean)
            } else {
                return false;
            }
        } else {
            return false;
        }
    } catch (e) {
        console.error(e);
        return false;
    }
}

export const useChatLoaders = ({ currSlideId, chatViewState, courseId }) => {

    const db = getFirestore();
    const userId = useUserId();

    // Initialize the chat type
    const [chatType, setChatType] = useState(0);
    useEffect(() => {
        const loadChatType = async () => {
            const chatType = await getChatType(courseId);
            setChatType(chatType);
        }
        loadChatType();
    }, []);

    // Determine if the lessons chat is valid based on the following conditions:
    //  1. The chat type is not null
    //      AND
    //  2. The chat type name is not IDE
    //      AND
    //  3. A. The courseId is cip4
    //      OR
    //     B. The courseId is public 
    //          AND
    //          i. The chatRollout flag is set to true 
    //              OR
    //          ii. The user has been flagged as part of the chat roll out
    //  4. Otherwise, the lessons chat is not valid
    const [chatValid, setChatValid] = useState(false);
    useEffect(() => {
        const loadChatValid = async () => {
            if (isNoChat(chatType) || isIDE(chatType)) {
                setChatValid(false);
            } else if (courseId === "cip4") {
                setChatValid(true);
            } else if (courseId === "public") {
                const chatRollout = await isChatRollout(userId);
                setChatValid(chatRollout);
            } else {
                setChatValid(false);
            }
        }
        loadChatValid();
    }, [chatType]);

    // Get the lessonId from the URL
    const { lessonId, slideId } = useParams();
    const lessonKey = lessonId ? lessonId : slideId;

    // Reference to the user's chat collection for this lesson
    const userChatCollection = collection(db, "chatHistory", userId, "lessons", lessonKey, "messages");

    // Variables to maintain the chat messages that the user sees
    const [tempMessages, setTempMessages] = useState([]);
    const [chatMessages, setChatMessages] = useState([]);

    // The last loaded message doc (used to load more messages)
    const [lastMessageDoc, setLastMessageDoc] = useState(null);

    // Variables to keep track of whether the user has unread messages
    const [unreadMessageFlag, setUnreadMessageFlag] = useState(false);

    // Reference to the user's chat timestamp for this lesson
    const chatTimestampRef = doc(db, "users", userId, "chatDetails", lessonKey)

    // Need a pointer because the listener hook cannot access the latest state
    const chatViewStateRef = useRef(chatViewState);
    useEffect(() => {
        if (!chatValid) { return; }
        chatViewStateRef.current = chatViewState;
    }, [chatViewState, chatValid]);

    // Need a pointer because the listener hook cannot access the latest state
    const tempMessagesRef = useRef(tempMessages);
    useEffect(() => {
        if (!chatValid) { return; }
        tempMessagesRef.current = tempMessages;
    }, [tempMessages, chatValid]);

    // Need a pointer because the listener hook cannot access the latest state
    const currSlideIdRef = useRef(currSlideId);
    useEffect(() => {
        if (!chatValid) { return; }
        currSlideIdRef.current = currSlideId;
    }, [currSlideId, chatValid]);

    // Need a pointer because the listener hook cannot access the latest state
    const chatMessagesRef = useRef(chatMessages);
    useEffect(() => {
        if (!chatValid) { return; }
        chatMessagesRef.current = chatMessages;
    }, [chatMessages, chatValid]);

    // Load the chat timestamp from the database
    // The timestamp represents the last time the user saw the chat
    const loadChatTimestamp = async () => {
        const chatTimestampDoc = await getDoc(chatTimestampRef);
        if (chatTimestampDoc.exists()) {
            const chatTimestampData = chatTimestampDoc.data();
            const timestamp = chatTimestampData.timestamp;
            return timestamp;
        } else {
            return null;
        }
    }

    // Update the chat timestamp in the database
    const setChatTimestamp = async () => {
        if (chatValid) {
            const timestamp = firebase.firestore.Timestamp.now();
            await setDoc(chatTimestampRef, { timestamp }, { merge: true });
        }
    }

    // Update the unread message flag if the chat is open
    const updateUnreadMessageFlag = async () => {
        if (chatViewStateRef.current === "minimized") {
            // Update the unread message flag if the chat is minimized
            setUnreadMessageFlag(true);
        } else {
            // Update the timestamp if the chat is open
            await setChatTimestamp();
        }
    }

    // Add the intro message to the user's collection
    const loadIntroMessage = async () => {
        const introMessage = {
            id: "intro",
            authorId: AI_ID,
            authorName: CHATBOT_NAME,
            content: CHAT_TYPES[chatType].intro_message,
            role: CHAT_ROLES.ASSISTANT,
            timestamp: firebase.firestore.Timestamp.now(),
            replyTo: null,
            currSlideId: CHAT_INTRO_SLIDE_ID,
            ratings: {}
        }

        // Add the into message to the chatMessages array
        if (isCommunity(chatType)) {
            setChatMessages([introMessage]);
            await updateUnreadMessageFlag();
        }

        // Add the intro message to the database
        const docRef = doc(userChatCollection, "intro");
        await setDoc(docRef, introMessage);

        // Update the last message doc
        const docSnap = await getDoc(docRef);
        setLastMessageDoc(docSnap);
    }

    // Load chat history from the database
    // startAfterDoc is the last message that was loaded, so we can load the next set of messages
    const loadChat = async () => {

        // If we have loaded all the messages, return
        if (lastMessageDoc && lastMessageDoc.data().id === "intro") {
            return;
        }

        // Load the messages from the given starting point if it exists, otherwise load the most recent messages
        let querySnapshot = null;
        if (lastMessageDoc !== null) {
            querySnapshot = query(userChatCollection, orderBy("timestamp", "desc"), startAfter(lastMessageDoc), limit(MESSAGE_RETRIEVAL_LIMIT));
        } else {
            querySnapshot = query(userChatCollection, orderBy("timestamp", "desc"), limit(MESSAGE_RETRIEVAL_LIMIT));
        }

        // Get the messages from the query snapchot
        const messages = await getDocs(querySnapshot);

        // There are no messages
        if (messages.empty && chatMessages.length === 0) {
            await loadIntroMessage();
            return;
        }

        // Update the messages array
        let loadedMessages = []
        messages.forEach(doc => {
            let newMessage = doc.data();
            newMessage.id = doc.id;
            loadedMessages.push(newMessage);
        });

        // Update the last message doc
        setLastMessageDoc(messages.docs[messages.docs.length - 1]);

        // Add the loaded messages to the chat messages array
        setChatMessages(prevMessages => {
            return [...prevMessages, ...loadedMessages];
        });

        // Update the unread message flag if the chat is minimized
        const timestamp = await loadChatTimestamp();
        const lastMessage = loadedMessages[loadedMessages.length - 1];
        if (chatViewState === "minimized" && (!timestamp || timestamp < lastMessage.timestamp)) {
            setUnreadMessageFlag(true);
        }
    }

    // Load the chat history when the lesson is first loaded
    useEffect(() => {
        // If the chat type is null, the user does not have a chat
        if (!chatValid) { return; }

        // Load the chat history from the database
        const loadChatHistory = async () => {
            await loadChat();
        }
        loadChatHistory();
    }, [chatValid])

    // Flag to skip the first call to onSnapshot, which is the initial load of the chat history
    let firstCall = true;

    // Remove a message from the tempMessages array once it has been loaded into the database
    const removeTempMessage = (messageData) => {
        // If this message is in the tempMessages array, remove it    
        for (let i = 0; i < tempMessagesRef.current.length; i++) {
            if (messageData.content === tempMessagesRef.current[i].content && messageData.authorId === userId) {
                setTempMessages(prevTempMessages => {
                    let newTempMessages = [...prevTempMessages];
                    newTempMessages.splice(i, 1);
                    return newTempMessages;
                });
                break;
            }
        }
    }

    // Logic to listen for new messages to posted to an individual chat
    const individualChatListener = (querySnapshot) => {
        // Skip the first call to onSnapshot, which is the initial load of the chat history
        if (firstCall) {
            firstCall = false;
            return;
        }

        // For each new message, add it to the chat messages array
        querySnapshot.docChanges().forEach(async (change) => {
            if (change.type === "added") {
                console.log("New message: ", change.doc.data());
                const messageData = change.doc.data();

                // Remove the message from the tempMessages array
                removeTempMessage(messageData);

                // Add the new message to the chat messages array
                setChatMessages(prevMessages => { return [{ ...messageData, id: change.doc.id }, ...prevMessages]; });

                await updateUnreadMessageFlag();
            } else if (change.type === "modified") {
                // Update the message in the chat messages array
                const messageData = change.doc.data();
                const messageIndex = chatMessagesRef.current.findIndex(message => message.id === change.doc.id);
                if (messageIndex !== -1) {
                    setChatMessages(prevMessages => {
                        let newMessages = [...prevMessages];
                        newMessages[messageIndex] = { ...messageData, id: change.doc.id };
                        return newMessages;
                    });
                }
            }
        })
    }

    // Set up listener for new messages for individual chat users
    useEffect(() => {
        if (!chatValid || !(isBasic(chatType) || isGrounded(chatType) || isButtons(chatType))) {
            return;
        }

        const querySnapshot = query(userChatCollection, orderBy("timestamp", "desc"), limit(MESSAGE_RETRIEVAL_LIMIT));
        const unsubscribe = onSnapshot(querySnapshot, individualChatListener);
        return () => {
            unsubscribe()
        }
    }, [chatValid]);

    // Remove the message from the tempMessages array and add it to the chatMessages array
    const updateChatMessages = async (messageData) => {
        if (messageData.currSlideId === currSlideIdRef.current) {
            setChatMessages(prevMessages => { return [messageData, ...prevMessages]; });
            await updateUnreadMessageFlag();
        }
    }

    // Logic to listen for new messages to posted to the community chat
    const communityChatListener = (querySnapshot) => {
        if (firstCall) {
            firstCall = false;
            console.log("First call");
            return;
        }

        // For each new message, add it to the chat messages array
        querySnapshot.docChanges().forEach(async (change) => {
            console.log("HEARD A CHANGE", change.type, change.doc.data());

            // Users are not able to delete messages, so this means
            // that we are at MESSAGE_RETRIEVAL_LIMIT capacity
            if (change.type === "removed") {
                console.log("At MESSAGE_RETRIEVAL_LIMIT capacity");
                return;
            }

            // Don't add the message if it doesn't have a timestamp yet
            // This assumes that the only modification to a message is the addition of a timestamp
            if (!change.doc.data().timestamp) {
                console.log("No timestamp");
                return;
            }

            const messageData = change.doc.data();
            const messageIndex = chatMessagesRef.current.findIndex(message => message.id === change.doc.id);
            if (messageIndex !== -1) {
                // Update the message in the chat messages array
                // (This is the case when the rating of a message changes)
                setChatMessages(prevMessages => {
                    let newMessages = [...prevMessages];
                    newMessages[messageIndex] = { ...messageData, id: change.doc.id };
                    return newMessages;
                });
            } else {
                // Remove the message from the tempMessages array
                removeTempMessage(messageData);

                // Add the message to the chat messages array
                await updateChatMessages({ ...messageData, id: change.doc.id });
                const newMessageDoc = doc(userChatCollection, change.doc.id);
                await setDoc(newMessageDoc, messageData);
            }
        })
    }

    // Set up listener for new messages for community chat users
    useEffect(() => {
        if (!chatValid || !isCommunity(chatType)) { return; }

        const communityChatCollection = collection(db, "chatHistory", "community", "lessons", lessonKey, "messages");
        const querySnapshot = query(communityChatCollection, orderBy("timestamp", "desc"), limit(MESSAGE_RETRIEVAL_LIMIT));
        const unsubscribe = onSnapshot(querySnapshot, communityChatListener);

        return () => {
            unsubscribe()
        }
    }, [chatValid]);

    if (!chatValid) {
        return {
            chatType: 0,
            chatMessages: [],
            tempMessages: [],
            setTempMessages: () => { },
            unreadMessageFlag: false,
            setUnreadMessageFlag: () => { },
            setChatTimestamp: () => { },
            loadChat: async () => { }
        }
    } else {
        return {
            chatType,
            chatMessages,
            tempMessages,
            setTempMessages,
            unreadMessageFlag,
            setUnreadMessageFlag,
            setChatTimestamp,
            loadChat
        };
    }

}