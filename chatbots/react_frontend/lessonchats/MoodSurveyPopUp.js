import { useUserId } from "hooks/user/useUserId";
import { addDoc, collection, getFirestore, serverTimestamp } from "firebase/firestore";
import styled from "styled-components";
import Swal from "sweetalert2";
import withReactContent from "sweetalert2-react-content";

// Necessary to use react within the mood toast
const MoodToast = withReactContent(Swal);

// Mood options for the mood survey
const moodOptions = [
    { emoji: '😞', mood: 1 },
    { emoji: '😕', mood: 2 },
    { emoji: '😐', mood: 3 },
    { emoji: '🙂', mood: 4 },
    { emoji: '🥳', mood: 5 }
];

const EmojiButtonsDiv = styled.div`
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-around;
    height: fit-content;
`;

const EmojiButton = styled.button`
    align-items: center;
    justify-content: center;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    width: 40px;
    height: 40px;
    font-size: 24px;
    margin: 0;
    background-color: #f8f9fa;

    &:hover {
        background-color: #e9ecef;
    }
`;

// Mood toast for the mood survey
export const moodToast = ({ currentContext }) => {
    const userId = useUserId();
    const db = getFirestore();

    // Add the result to the moodSurveys/ collection in the database
    const storeSurveyResult = async (mood) => {
        try {
            const moodSurveysRef = collection(db, 'moodSurveys');
            const result = {
                userId: userId,
                mood: mood,
                timestamp: serverTimestamp(),
                context: currentContext
            }
            await addDoc(moodSurveysRef, result);
        } catch (error) {
            console.error('Error storing mood survey result: ', error);
        }
    };

    MoodToast.fire({
        title: 'How are you feeling?',
        html: (
            <EmojiButtonsDiv>
                {moodOptions.map(({ emoji, mood }) => (
                    <EmojiButton
                        key={mood}
                        onClick={() => {
                            MoodToast.close();

                            // Store the mood survey result in the database
                            storeSurveyResult(mood);
                        }}
                    >
                        {emoji}
                    </EmojiButton>
                ))}
            </EmojiButtonsDiv>
        ),
        showConfirmButton: false,
        toast: true,
        position: 'top-end',
        showCloseButton: true,
    });
};
