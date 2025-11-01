from haystack.tools import Tool
from haystack.components.agents.agent import Agent
from haystack.components.generators.chat import HuggingFaceAPIChatGenerator
from haystack.utils.hf import HFGenerationAPIType
from haystack.dataclasses import ChatMessage


def get_user_info() -> dict:
    """Get user information."""
    return {"name": "Alice", "email": "alice@example.com", "role": "admin"}

info_tool = Tool(
    name="Get user Information",
    description="Amazing tool that helps the LLMs to get the user information queried by "
                "the user",
    parameters={"type": "object", "properties": {}},
    function=get_user_info,
    outputs_to_state={
        "user_info": {}
    }
)

agent = Agent(
    chat_generator=HuggingFaceAPIChatGenerator(api_type=HFGenerationAPIType.SERVERLESS_INFERENCE_API,
                                  api_params={"model": "Qwen/Qwen2.5-7B-Instruct",
                                             "provider": "together"}),
    tools=[info_tool],
    state_schema={
        "user_info": {"type": dict}
    },
    system_prompt=(
        "You MUST ALWAYS use tools if available.\n"
        "If user asks anything that can be fulfilled by a tool: CALL THE TOOL."
    )
)

result = agent.run(
    messages=[ChatMessage.from_user("Get the user information from the tools available")]
)

print(result)

user_info = result["user_info"]
print(user_info)
print(user_info["name"], user_info["email"], user_info["role"])