"""
Few-Shot Examples for AI Academic Tutor

These examples help Gemini understand the expected
format and style of answers.
"""

FEW_SHOT_EXAMPLES = """
Example 1

Question:
What is LAN?

Answer:
Definition:
A Local Area Network (LAN) is a computer network that connects devices within a limited geographical area such as a home, office, school, or laboratory.

Key Points:
- Covers a small geographical area.
- Provides high-speed communication.
- Easy to install and maintain.
- Commonly used in offices and educational institutions.

--------------------------------------------

Example 2

Question:
Explain WAN.

Answer:
Definition:
A Wide Area Network (WAN) is a network that connects multiple LANs over large geographical distances using communication links.

Key Points:
- Covers large geographical areas.
- Connects cities, countries, or continents.
- Uses leased communication lines or the Internet.
- Example: The Internet.

--------------------------------------------

Example 3

Question:
Explain the OSI Model.

Answer:
Definition:
The OSI (Open Systems Interconnection) Model is a seven-layer reference model used to understand how data travels through a network.

Layers:
1. Physical Layer
2. Data Link Layer
3. Network Layer
4. Transport Layer
5. Session Layer
6. Presentation Layer
7. Application Layer

Important Points:
- Standardizes network communication.
- Helps troubleshoot networking problems.
- Each layer performs a specific function.

--------------------------------------------

Example 4

Question:
What is TCP/IP?

Answer:
Definition:
TCP/IP (Transmission Control Protocol/Internet Protocol) is the standard communication protocol suite used for data transmission over the Internet.

Key Points:
- TCP ensures reliable communication.
- IP handles addressing and routing.
- Widely used in modern computer networks.
- Forms the foundation of Internet communication.

--------------------------------------------

Use the same structure and style when answering the user's question.
"""