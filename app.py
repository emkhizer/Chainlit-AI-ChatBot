import os # os library ko import kar rahe hain jo operating system ke saath kaam karne ke liye
from dotenv import load_dotenv # dotenv se load_dotenv function import kar rahe hain jo .env file se variables load karta hai
from typing import cast # typing se cast function import kar rahe hain jo type conversion ke liye use hota hai
import chainlit as cl # chainlit library ko cl naam se import kar rahe hain jo web-based chat interface banane ke liye hai
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel # agents library se zaroori classes import kar rahe hain
from agents.run import RunConfig # agents.run se RunConfig class import kar rahe hain jo configuration ke liye hai

load_dotenv() # .env file se environment variables load kar rahe hain system mein

gemini_api_key = os.getenv("GEMINI_API_KEY") # environment variable se GEMINI_API_KEY ka value get kar rahe hain

# Agar API key nahi mila to error throw karenge
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY set nahi hai. Please ensure karen ke ye aap ke .env file mein define hai.")

@cl.on_chat_start # Chainlit ka decorator hai jo chat start hone pe trigger hota hai
async def start(): # Async function define kar rahe hain jo chat start pe chalega
    external_client = AsyncOpenAI( # AsyncOpenAI client create kar rahe hain
        api_key=gemini_api_key, # API key pass kar rahe hain authentication ke liye
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/", # Gemini API ka base URL set kar rahe hain
    )

    model = OpenAIChatCompletionsModel( # OpenAI compatible model create kar rahe hain
        model="gemini-2.0-flash", # Model name specify kar rahe hain (Gemini 2.0 Flash)
        openai_client=external_client # Client pass kar rahe hain model ko
    )

    config = RunConfig( # Configuration object create kar rahe hain
        model=model, # Model pass kar rahe hain config mein
        model_provider=external_client, # Model provider set kar rahe hain
        tracing_disabled=True # Tracing disable kar rahe hain performance ke liye
    )

    cl.user_session.set("chat_history", []) # User session mein empty chat history list set kar rahe hain
    cl.user_session.set("config", config) # User session mein config object store kar rahe hain
    
    agent = Agent( # Agent object create kar rahe hain
        name="Assistant", # Agent ka naam "Assistant" set kar rahe hain
        instructions="You are a helpful assistant.", # Agent ko instructions de rahe hain ke woh helpful assistant hai
        model=model # Model pass kar rahe hain agent ko
    )
    
    cl.user_session.set("agent", agent) # User session mein agent object store kar rahe hain
    await cl.Message(content="Welcome to the Panaversity AI Assistant! How can I help you today?").send() # Welcome message send kar rahe hain user ko
    
@cl.on_message # Chainlit ka decorator hai jo message receive hone pe trigger hota hai
async def main(message: cl.Message): # Async function define kar rahe hain jo message handle karega
    msg = cl.Message(content="Thinking...") # "Thinking..." message create kar rahe hain
    await msg.send() # Message send kar rahe hain user ko dikhane ke liye ke processing ho rahi hai
    
    agent:Agent = cast(Agent, cl.user_session.get("agent")) # User session se agent object get kar rahe hain aur type cast kar rahe hain
    config:RunConfig = cast(RunConfig, cl.user_session.get("config")) # User session se config object get kar rahe hain aur type cast kar rahe hain
    history = cl.user_session.get("chat_history") or [] # User session se chat history get kar rahe hain, agar nahi hai to empty list
    
    history.append({"role": "user", "content": message.content}) # User ka message chat history mein add kar rahe hain
    
    try: # Try block start kar rahe hain error handling ke liye
        print("\n[CALLING_AGENT_WITH_CONTEXT]\n", history, "\n") # Debug ke liye history print kar rahe hain console mein
        
        result = Runner.run_sync( # Runner.run_sync method call kar rahe hain agent ko run karne ke liye
            starting_agent=agent, # Starting agent pass kar rahe hain
            input=history, # Chat history input ke tor pe pass kar rahe hain
            run_config=config # Run configuration pass kar rahe hain
        )

        response_conent = result.final_output # Result se final output get kar rahe hain
        msg.content = response_conent # Message ka content update kar rahe hain response se
        await msg.update() # Message update kar rahe hain UI mein

        cl.user_session.set("chat history", result.to_input_list()) # Chat history update kar rahe hain session mein
        
        print(f"User: {message.content}") # Console mein user ka message print kar rahe hain
        print(f"Assistant: {response_conent}") # Console mein assistant ka response print kar rahe hain
        
    except Exception as e: # Exception catch kar rahe hain agar koi error aaye
        msg.content = f"Error: {str(e)}" # Error message set kar rahe hain
        await msg.update() # Error message update kar rahe hain UI mein
        print(f"Error: {str(e)}") # Console mein error print kar rahe hain