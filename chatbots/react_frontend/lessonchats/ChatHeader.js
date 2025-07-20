import styled from 'styled-components';
import { useContext } from 'react';
import { LessonContext } from "../LessonContext";
import { FaTimes } from "react-icons/fa";

export const ChatHeader = () => {
    const { setChatViewState } = useContext(LessonContext);

    return (
        <ChatBar>
            <div>Chat</div>
            <button
                onClick={() => setChatViewState("minimized")}
                className="btn btn-light mr-1"
                style={{
                    margin: "0px",
                }}
            >
                <FaTimes />
            </button>
        </ChatBar>
    );
}

const ChatBar = styled.div`
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    background-color: white;
    padding: 3px;
    padding-left: 10px;
    border-bottom: 1px solid #ccc;
`;