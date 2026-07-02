# Prompt for Notes
NOTE_PROMPT = """
Convert the following answer into well-structured revision notes.

Requirements:
- Use headings.
- Use bullet points.
- Highlight important keywords.
- Keep it concise and easy to revise.

Content:
{context}
"""

# Prompt for Summary
SUMMARY_PROMPT = """
Summarize the following topic in simple language.

Requirements:
- Maximum 150 words.
- Explain clearly.
- Mention the most important concepts.

Content:
{context}
"""

# Prompt for Quiz
QUIZ_PROMPT = """
Generate 5 multiple-choice questions from the following content.

Rules:
- Four options (A, B, C, D)
- Mention the correct answer after each question.
- Questions should test understanding.

Content:
{context}
"""