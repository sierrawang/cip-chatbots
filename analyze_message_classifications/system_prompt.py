SYSTEM_PROMPT = """A student in an introductory computer science course had the following conversation with a chatbot. Classify each message as one of the following categories:
         
CONCEPTUAL: The message is a question about a concept in computer science.
HOMEWORK: The message is a question about how to solve a specific assignment problem. In this case, the student is typically asking the chatbot to write code for them.
AI: The message is a question about artificial intelligence. In this case, the student is typically asking the chatbot whether it is an AI.
GREETING: The message is a greeting like hello or hi.
GRATITUDE: The message is an expression of gratitude.
OTHER: The message does not fit into any of the above categories.

Output a JSON object with the following format:
"""