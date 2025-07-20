import { useEffect, useState } from "react";
import { doc, getFirestore } from "firebase/firestore";
import { useUserId } from "hooks/user/useUserId";
import { useDocumentDataOnce } from "react-firebase-hooks/firestore";
import { setDoc } from "firebase/firestore";
import { moodToast } from "./MoodSurveyPopUp";
import { useParams } from "react-router";

export const useMoodSurveyLoaders = ({ lessonId, currSlideId }) => {
    const db = getFirestore();
    const userId = useUserId();

    // Load the mood survey document for this user
    const moodSurveyDocRef = doc(db, `users/${userId}/docs/moodSurvey`);
    const [moodSurveyDoc, moodSurveyLoading, moodSurveyError] = useDocumentDataOnce(moodSurveyDocRef);

    const [surveyTimes, setSurveyTimes] = useState([]);

    // Load the mood survey slide Id
    useEffect(() => {
        if (moodSurveyLoading) return;
        setSurveyTimes(moodSurveyDoc?.surveyTimes || []);
    }, [moodSurveyLoading]);

    // Logic to determine if the mood survey should be shown
    const showSurvey = (index) => {
        const surveyTime = surveyTimes[index];
        return surveyTime.context === "lessons" &&
            surveyTime.lessonId === lessonId &&
            surveyTime.slideId === currSlideId &&
            !surveyTime.hasShown;
    }

    // Update the hasShown field to be true for this survey time
    const updateSurveyTimes = async (index) => {
        const updatedSurveyTimes = [...surveyTimes];
        updatedSurveyTimes[index].hasShown = true;
        await setDoc(moodSurveyDocRef, { surveyTimes: updatedSurveyTimes });
        setSurveyTimes(updatedSurveyTimes);
    };

    // Show the mood survey when the user reaches the mood survey slide
    useEffect(() => {
        // Return if currSlideId is not set
        if (!currSlideId || !surveyTimes) return;

        // Check if the current slide is a mood survey slide and has not been shown before
        for (let index = 0; index < surveyTimes.length; index++) {
            if (showSurvey(index)) {
                // Show the mood survey
                const currentContext = {
                    lessonId: lessonId,
                    currSlideId: currSlideId
                };
                moodToast({ currentContext });

                // Update the survey times that the mood survey has been shown
                updateSurveyTimes(index);
            }
        }
    }, [currSlideId]);
}

export const useMoodSurveyLoadersAssn = () => {
    const db = getFirestore();
    const userId = useUserId();
    const { urlKey } = useParams();

    // Load the mood survey document for this user
    const moodSurveyDocRef = doc(db, `users/${userId}/docs/moodSurvey`);
    const [moodSurveyDoc, moodSurveyLoading, moodSurveyError] = useDocumentDataOnce(moodSurveyDocRef);

    const [surveyTimes, setSurveyTimes] = useState([]);

    // Load the mood survey slide Id
    useEffect(() => {
        if (moodSurveyLoading) return;
        setSurveyTimes(moodSurveyDoc?.surveyTimes || []);
    }, [moodSurveyLoading]);

    // Logic to determine if the mood survey should be shown
    const showSurvey = (index) => {
        const surveyTime = surveyTimes[index];
        return surveyTime.context === "assns" &&
            surveyTime.assnId === urlKey &&
            !surveyTime.hasShown;
    }

    // Update the hasShown field to be true for this survey time
    const updateSurveyTimes = async (index) => {
        const updatedSurveyTimes = [...surveyTimes];
        updatedSurveyTimes[index].hasShown = true;
        await setDoc(moodSurveyDocRef, { surveyTimes: updatedSurveyTimes });
        setSurveyTimes(updatedSurveyTimes);
    };

    // Show the mood survey when the user reaches the mood survey slide
    const runMoodSurvey = async () => {
        if (!urlKey || !surveyTimes) return;

        // Check if the current slide is a mood survey slide and has not been shown before
        for (let index = 0; index < surveyTimes.length; index++) {
            if (showSurvey(index)) {
                // Show the mood survey
                const currentContext = {
                    assnId: urlKey
                };
                moodToast({ currentContext });

                // Update the survey times that the mood survey has been shown
                updateSurveyTimes(index);
            }
        }
    };

    return { runMoodSurvey };
}