import os
from dotenv import load_dotenv
from typing import cast
import chainlit as cl
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

@cl.on_chat_start
async def start():
    external_client = AsyncOpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=external_client
    )

    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )

    cl.user_session.set("chat_history", [])  # Fixed variable name (no space)
    cl.user_session.set("config", config)
    
    agent = Agent(
        name="Assistant",
        instructions="You are a helpful assistant.",
        model=model
    )
    
    cl.user_session.set("agent", agent)
    await cl.Message(content="Welcome to the Panaversity AI Assistant! How can I help you today?").send()
    
@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="Thinking...")  # Fixed typo: cl.Messsage -> cl.Message
    await msg.send()
    
    agent:Agent = cast(Agent, cl.user_session.get("agent"))
    config:RunConfig = cast(RunConfig, cl.user_session.get("config"))
    history = cl.user_session.get("chat_history") or []  # Fixed variable name to match what was set
    
    history.append({"role": "user", "content": message.content})
    
    try:
        print("\n[CALLING_AGENT_WITH_CONTEXT]\n", history, "\n")
        
        result = Runner.run_sync(  # Note: If this should be async, consider using run_async instead
            starting_agent=agent,
            input=history,
            run_config=config
        )

        response_conent = result.final_output
        msg.content = response_conent
        await msg.update()

        cl.user_session.set("chat history", result.to_input_list())
        
        print(f"User: {message.content}")
        print(f"Assistant: {response_conent}")
        
    except Exception as e:
        msg.content = f"Error: {str(e)}"
        await msg.update()
        print(f"Error: {str(e)}")