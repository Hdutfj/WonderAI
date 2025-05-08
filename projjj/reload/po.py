import chainlit as cl
import os
from dotenv import load_dotenv
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled
from typing import Optional, Dict

load_dotenv()
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
GITHUB_CLIENT_ID=os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET=os.getenv("GITHUB_CLIENT_SECRET")
GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT ID")
GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET")
set_tracing_disabled(True)

provider= AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/",
)


@cl.password_auth_callback
async def login(username: str, password: str) -> Optional[cl.User]:
    if (username, password) == ("admin@gmail.com", "112233"):
        return cl.User(identifier="Admin", metadata={"role": "admin"})
    return None
    
@cl.oauth_callback
async def github_login(provider_id:str, token:str, raw_user_data:Dict[str,str], default_user:cl.User)-> Optional[cl.User]:
    print(f"Logging into the Github","="*9)
    print(f"provider_id,{provider_id}")
    print(f"token,{token}")
    print(f"raw_user_data,{raw_user_data}")

    try:
        # Implement your login verification logic here
        return default_user
    except Exception as e:
        print(f"GitHub login failed: {e}")
        return None
    
@cl.oauth_callback
async def google_login(provider_id:str, token:str, raw_user_data:Dict[str,str], default_user:cl.User )->Optional[cl.User]:
    print(f"logging to google","="*9)
    print(f"provider_id,{provider_id}")
    print(f"token,{token}")
    print(f"raw_user_data,{raw_user_data}")

    try:
        return default_user
    except Exception as e:
        print(f"Google login failed: {e}")
        return None  
    
@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("history", [])
    await cl.Message(content="HaseebAcademy Your Assistant, How can i help you?").send()

@cl.on_message
async def handle_message(message: cl.Message):
    if "continue without an account" in message.content.lower():
        await cl.Message(content="You must be logged in to use this assistant.").send()
        return

    history=cl.user_session.get("history")
    history.append({"role":"user", "content": message.content})

    agent= Agent(
        name="John Assistant",
        instructions=("You are a helpful assistant, your name is HaseebAcademy. Respond warmly. If someone says 'I love you', reply with 'I love you too ❤️'. "
            "If someone says 'done', reply 'Hurrah! 🎉'. Personalize responses. Calm angry users."
        ),
        model=OpenAIChatCompletionsModel(model="gemini-1.5-flash", openai_client=provider),
    )

    result=await Runner.run(agent, input=history)
    history.append({"role":"assistant", "content": result.final_output})
    cl.user_session.set("history", history)
    await cl.Message(content=result.final_output).send()
    
    full_history="\n".join([f"{m['role'].capitalize()}: {m['content'][:55].strip()}....."for m in history])
    await cl.Message(content=f"History:{full_history}").send()




           