import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import React from 'react';

export const FormattedMessage = ({ content }) => {
    const sections = content.split('```');

    return (
        <>
            {sections.map((section, index) => {
                // Odd indices are code, even indices are text
                const isCode = index % 2 !== 0;
                if (isCode) {
                    // Extract the language from the code block, assuming the format is correct
                    const firstNewLineIndex = section.indexOf('\n');
                    const language = section.substring(0, firstNewLineIndex).trim();
                    const code = section.substring(firstNewLineIndex + 1);
                    return (
                        <SyntaxHighlighter key={index} language={language || "python"} customStyle={{ fontSize: '12px', backgroundColor: 'white', borderRadius: '4px' }}>
                            {code}
                        </SyntaxHighlighter>
                    );
                } else {
                    // For text, preserve new lines, but trim leading/trailing whitespace/newlines
                    const trimmedSection = section.trim(); // Trim leading and trailing whitespace/newlines
                    if (!trimmedSection) return null; // Don't render empty sections
                    return trimmedSection.split('\n').map((line, lineIndex) => (
                        <React.Fragment key={`${index}-${lineIndex}`}>
                            {line}
                            <br />
                        </React.Fragment>
                    ));
                }
            })}
        </>
    );
}