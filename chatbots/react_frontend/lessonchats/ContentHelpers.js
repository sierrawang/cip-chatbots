// Functions to get the current content that the student is viewing

import { parseCommands } from "../lessontypes/KarelCommandsLesson";
import { doc, getDoc, getFirestore } from "firebase/firestore";

export const useContentHelpers = ({ player, lessonData, currSlideId, currSlideData }) => {
    const getCurrentTime = () => {
        if (player) {
            return player.getCurrentTime();
        }
        return 0; // Return 0 if player is not initialized
    };

    const getSplashContent = async (currData) => {
        return `Splash page:\nTitle: ${currData.title}\nAuthors: ${currData.authors}\nCourse: ${currData.course}`;
    }

    const getKarelCommandContent = async (currData) => {
        const commands = parseCommands(currData.commands);
        return `This is an exercise with Karel the robot. The student should use the commands to make the world state look like the goal state.\nThe commands are: ${commands}.\nThe world state is: ${JSON.stringify(currData.startState)}.\nThe goal state is: ${JSON.stringify(currData.goalState)}.`;
    }

    const getCurrentVideoContent = async (currData) => {
        const currentTime = getCurrentTime();
        if (currentTime === 0) return "";

        // Get transcript from firestore transcripts/lessonData.id/items/data.videoId
        try {
            const db = getFirestore();
            const transcriptRef = doc(db, "transcripts", lessonData.id, "items", currSlideId);
            const transcriptDoc = await getDoc(transcriptRef);
            const transcriptData = transcriptDoc.data();
            const transcript = transcriptData.transcript;

            // Find the current sentence based on the current time
            let currentContent = "";
            transcript.forEach(item => {
                // Check if the sentence's start time is within a minute before the current time
                const startTime = item.offset / 1000;
                if (startTime >= currentTime - 60 && startTime <= currentTime) {
                    const content = item.text.replace(/&#39;/g, "'");
                    currentContent += content + " ";
                }
            });

            return currentContent;
        } catch (error) {
            return "";
        }
    }

    const getCurrentLectureVideoContent = async (currData) => {
        const currentContent = await getCurrentVideoContent(currData);
        if (currentContent) {
            return `In this lecture video, the professor just said: "${currentContent.trim()}"`;
        } else {
            return "This is a lecture video, but we are currently unable to get the current video content.";
        }
    }

    const getSpeechBubbleContent = async (currData) => {
        return `Speech bubble that says "${currData.text}"`;
    }

    const getRunnableContent = async (currData) => {
        return "This is a code example that the student can run and watch the output. The code is: \n```" + currData.starterCode + "```";
    }

    const getLearningGoalsContent = async (currData) => {
        let goals = "Lesson Goals: \n";
        for (const goal of currData.learningGoals) {
            goals += "* " + goal.value + "\n";
        }
        return goals;
    }

    // Sierra - no transcript for skippable video as of now 3/13/2024
    const getSkippableVideoContent = async (currData) => {
        const currentContent = await getCurrentVideoContent(currData);
        if (currentContent) {
            return `This is an optional video called ${currData.title}. In the last minute, the professor said: "${currentContent.trim()}"`;
        } else {
            return "This is a optional video, but we are currently unable to get the current video content.";
        }
    }

    const getCompleteContent = async (currData) => {
        let resources = "Resources: \n";
        for (const id in currData.examples) {
            resources += "* Code example: " + currData.examples[id].title + "\n";
        }
        for (const id in currData.readings) {
            resources += "* Textbook chapter: " + currData.readings[id].title + "\n";
        }
        return `This is the conclusion page of the lesson. This page provides optional resources that are related to the lesson. The resources are: \n${resources}`;
    }

    const getCurrentContent = async () => {
        const type = currSlideData.data.type.toLowerCase()
        const currData = currSlideData.data;
        if (type === 'splash') {
            return await getSplashContent(currData);
        }
        if (type === 'karelcommand') {
            return await getKarelCommandContent(currData);
        }
        if (type === 'video') {
            return await getCurrentLectureVideoContent(currData);
        }
        if (type === 'speechbubble') {
            return await getSpeechBubbleContent(currData);
        }
        if (type === 'karelrunnable' || type === 'consolerunnable' || type === 'graphicsrunnable') {
            return await getRunnableContent(currData);
        }
        if (type === 'learninggoals') {
            return await getLearningGoalsContent(currData);
        }
        if (type === 'skippablevideo') {
            return await getSkippableVideoContent(currData);
        }
        if (type === 'complete') {
            return await getCompleteContent(currData);
        }
        return "";
    }

    return {
        getCurrentContent
    };
}