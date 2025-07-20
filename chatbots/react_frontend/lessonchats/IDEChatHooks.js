import { useEffect, useRef, useState } from "react";
import { query, collection, doc, getFirestore, orderBy, getDocs, startAfter, limit, getDoc, setDoc, onSnapshot, addDoc } from "firebase/firestore";
import { AI_ID, CHATBOT_NAME, CHAT_ROLES, CHAT_TYPES, MESSAGE_RETRIEVAL_LIMIT, isIDE, isNoChat } from "./ChatConstants";
import { useUserId } from "hooks/user/useUserId";
import firebase from "firebase/compat/app";
import { getChatType, isChatRollout } from "../ChatHooks";
import { useParams } from "react-router";

// This hook is used to load the chat messages for the IDE chat.
// It is extremely similar to the useChatLoaders hook, but it is specifically for the IDE chat.
export const useIDEChatLoaders = ({ selectedTab, courseId }) => {

    const db = getFirestore();
    const userId = useUserId();
    const teachNow = isTeachNow();

    // Initialize the chat type
    const [chatType, setChatType] = useState(0);
    useEffect(() => {
        const loadChatType = async () => {
            const chatType = await getChatType(courseId);
            setChatType(chatType);
        }
        loadChatType();
    }, []);


    // Determine if the IDE chat is valid based on the following conditions:
    //  1. The chat type is not null
    //      AND
    //  2. The chat type name is IDE
    //      AND
    //  3. A. The courseId is cip4
    //      OR
    //     B. The courseId is public 
    //          AND
    //          i. The chatRollout flag is set to true 
    //              OR
    //          ii. The user has been flagged as part of the chat roll out
    //  4. Otherwise, the IDE chat is not valid
    const [chatValid, setChatValid] = useState(false);
    useEffect(() => {
        if(teachNow) return setChatValid(false);
        const loadChatValid = async () => {
            if (isNoChat(chatType) || !isIDE(chatType)) {
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

    // Get the assignment id from the URL
    const { urlKey } = useParams();
    const urlKeySafe = urlKey ? urlKey : "default";

    // Reference to the user's chat collection for this assignment
    const userChatCollection = collection(db, "chatHistory", userId, "assns", urlKeySafe , "messages");

    // Variables to maintain the chat messages that the user sees
    const [tempMessages, setTempMessages] = useState([]);
    const [chatMessages, setChatMessages] = useState([]);

    // The last loaded message doc (used to load more messages)
    const [lastMessageDoc, setLastMessageDoc] = useState(null);

    // Variables to keep track of whether the user has unread messages
    const [unreadMessageFlag, setUnreadMessageFlag] = useState(false);
    const chatTimestampRef = doc(db, "users", userId, "chatDetails", urlKeySafe)

    // Keep track of the chat view state because the listener hook cannot access the latest state
    const selectedTabRef = useRef(selectedTab);
    useEffect(() => {
        if (!chatValid) { return; }
        selectedTabRef.current = selectedTab;
    }, [selectedTab, chatValid]);

    // Need a pointer because the listener hook cannot access the latest state
    const tempMessagesRef = useRef(tempMessages);
    useEffect(() => {
        if (!chatValid) { return; }
        tempMessagesRef.current = tempMessages;
    }, [tempMessages, chatValid]);

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
        const timestamp = firebase.firestore.Timestamp.now();
        await setDoc(chatTimestampRef, { timestamp }, { merge: true });
    }

    // Update the unread message flag if the chat is open
    const updateUnreadMessageFlag = async () => {
        if (selectedTabRef.current !== "Chat") {
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
            currSlideId: null,
            ratings: {}
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
        if (selectedTab !== "Chat" && (!timestamp || timestamp < lastMessage.timestamp)) {
            setUnreadMessageFlag(true);
        }
    }

    // Load the chat history when the lesson is first loaded
    useEffect(() => {
        if (!chatValid) { return; }
        // Load the chat history from the database
        const loadChatHistory = async () => {
            await loadChat();
        }
        loadChatHistory();
    }, [chatValid]);

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
        if (!chatValid) { return; }
        const querySnapshot = query(userChatCollection, orderBy("timestamp", "desc"), limit(MESSAGE_RETRIEVAL_LIMIT));
        const unsubscribe = onSnapshot(querySnapshot, individualChatListener);
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



const isTeachNow = () => {
    const paths = window.location.pathname.split("/")
    return (paths.length >= 3 && paths[2] === "peer");
  }
