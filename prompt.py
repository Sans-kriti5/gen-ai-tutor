"""
Prompt Templates for AI Academic Tutor
"""

# =====================================================
# Zero-Shot Prompt
# =====================================================

EXPLANATION_PROMPT = """
Answer the following question clearly and accurately using only the provided context.

Requirements:
- Use simple language.
- Explain the concept in 5–10 sentences.
- Include a definition.
- Use bullet points whenever appropriate.
- Do not make up information outside the context.

Context:
{context}

Question:
{question}

Answer:
"""

# =====================================================
# Chain-of-Thought Prompt
# =====================================================

COT_PROMPT = """
Use the provided context to answer the question.

Before writing the final answer:
1. Identify the main concept.
2. Explain the important points in a logical order.
3. Give the final explanation in simple language.

Context:
{context}

Question:
{question}

Final Answer:
"""

# =====================================================
# Revision Notes
# =====================================================

NOTE_PROMPT = """
Convert the following answer into revision notes.

Requirements:
- Use headings.
- Use bullet points.
- Highlight important keywords.
- Keep the notes concise.
- Make them suitable for quick revision.

Content:
{context}
"""

# =====================================================
# Chapter Summary
# =====================================================

SUMMARY_PROMPT = """
Summarize the following content.

Requirements:
- Maximum 150 words.
- Use simple language.
- Mention only the most important concepts.
- Keep the summary easy to understand.

Content:
{context}
"""

# =====================================================
# Quiz Generation
# =====================================================

QUIZ_PROMPT = """
Generate 5 multiple-choice questions from the following content.

Requirements:
- Four options (A, B, C, D)
- Mention the correct answer after every question.
- Questions should test conceptual understanding.

Content:
{context}
"""

# =====================================================
# Study Plan
# =====================================================

STUDY_PLAN_PROMPT = """
Create a study plan for the following topic.

Requirements:
- Divide the topic into small learning goals.
- Suggest the order in which to study.
- Mention important concepts.
- Include revision suggestions.
- End with a quick self-test checklist.

Topic:
{context}
"""