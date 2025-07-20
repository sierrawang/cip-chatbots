import * as functions from "firebase-functions";
import * as admin from "firebase-admin";
import { YoutubeTranscript } from "youtube-transcript";

// Necessary for fetching the transcript
require("isomorphic-fetch");

// Listen for changes to the /lessons/cip4/lessonsList collection. 
// Whenevr a lesson is added or updated, update all of the video transcripts for that lesson.
export const updateLectureVideoTranscript = functions.firestore
    .document("lessons/cip4/lessonsList/{lessonId}")
    .onWrite(async (change, context) => {
        // const lessonId = context.params.lessonId;
        const lessonData = change.after.data();

        if (lessonData) {
            const transcriptsRef = admin.firestore().collection("transcripts").doc(context.params.lessonId).collection("items");

            // Go through lessonsData.slidesInfo and get the transcript for each video slide
            const slidesInfo = lessonData.slidesInfo;
            if (slidesInfo) {
                for (const slideId in slidesInfo) {
                    const slide = slidesInfo[slideId];
                    if (slide.type === "video") {
                        try {
                            // Get the transcript for the video slide
                            const videoId = slide.videoId;
                            const transcript = await YoutubeTranscript.fetchTranscript(videoId);

                            // Store the transcript in the transcripts collection
                            await transcriptsRef.doc(slideId).set({ transcript: transcript });
                        } catch (error) {
                            functions.logger.error(`Error fetching transcript for video slide ${slideId} in lesson ${context.params.lessonId}: ${error}`);
                        }
                    }
                }
            }
        }
    });