function extractText(content) {
    if (typeof content === "object" && !Array.isArray(content)) {
        if ("text" in content) {
            return content.text || "";
        } else if ("content" in content) {
            return extractText(content.content) + " \\n ";
        } else {
            return "";
        }
    } else if (Array.isArray(content)) {
        return content.reduce((acc, item) => acc + extractText(item), "");
    }
    return "";
}

function parseTable(data) {
    const tableRows = data.content || [];
    const table = [];

    for (const row of tableRows) {
        const tableCells = row.content || [];
        const parsedRow = tableCells.map(cell => extractText(cell));
        table.push(parsedRow);
    }

    return table;
}

function formatTextTable(table) {
    const colWidths = table[0].map((_, i) => Math.max(...table.map(row => row[i].length)));

    let textTable = "";
    for (const row of table) {
        textTable += row.map((cell, i) => cell.padEnd(colWidths[i])).join(" | ") + "\n";
        textTable += colWidths.map(width => "-".repeat(width)).join("-+-") + "\n";
    }
    return textTable.slice(0, -colWidths.map(width => "-".repeat(width)).join("-+-").length - 1);
}

function extractHeading(entry) {
    const results = [];
    if (entry.content) {
        for (const item of entry.content) {
            if (item.text) {
                results.push(item.text);
            }
        }
    }
    return results.join(" ") + "\n";
}

export function parseTipTap(contentDict) {
    const typesToSkip = ["image", "iframe", "karelworld", "resizableImage"];
    let resultString = "";
    if (!contentDict || !("content" in contentDict) || !contentDict.content) {
        return resultString;
    }

    try {
        const contentArray = contentDict.content;
        for (const entry of contentArray) {
            if (entry.type && typesToSkip.includes(entry.type)) {
                continue;
            }

            if (entry.type === "heading") {
                const heading = extractHeading(entry);
                resultString += heading;
                continue;
            }

            if (entry.type === "table") {
                const parsedTable = parseTable(entry);
                const textTable = formatTextTable(parsedTable);
                resultString += textTable + "\n";
                continue;
            }

            if (entry.type === "paragraph" || entry.type === "codeBlock" || entry.type === "orderedList" || entry.type === "bulletList" || entry.type === "blockquote") {
                if (!entry.content) {
                    continue;
                }
                for (const item of entry.content) {
                    if ("text" in item) {
                        resultString += item.text + " ";
                    } else if ("content" in item) {
                        resultString += extractText(item.content) + " ";
                    } else if (item.type === "runnable-code") {
                        const content = item.attrs?.code || "";
                        resultString += content + " ";
                    }
                }
                resultString += "\n";
                continue;
            }

            if (entry.type === "runnable-karel" || entry.type === "runnable-code" || entry.type === "runnable-graphics") {
                const content = entry.attrs?.code || "";
                resultString += content + "\n";
                continue;
            }
        }
        return resultString;
    } catch (e) {
        console.error("Error processing content:", e);
        return resultString;
    }
}
