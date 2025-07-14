# Chainlit-AI-ChatBot
Ye code ek complete Chainlit-based AI assistant application hai. Main components:
Setup Section:

Libraries import kar rahe hain
Environment variables load kar rahe hain
API key validation kar rahe hain

Chat Start Function (@cl.on_chat_start):

Jab user chat start karta hai to ye function trigger hota hai
AI client, model, aur configuration setup karta hai
User session mein zaroori objects store karta hai
Welcome message send karta hai

Message Handler (@cl.on_message):

Har user message pe ye function trigger hota hai
"Thinking..." message dikhata hai processing ke doran
User session se stored objects retrieve karta hai
User message ko history mein add karta hai
Agent ko run karta hai response generate karne ke liye
Response ko UI mein update karta hai
Error handling bhi karta hai

Key Features:

Session-based chat history maintain karta hai
Async operations use karta hai smooth experience ke liye
Error handling properly karta hai
Console mein debug information print karta hai
