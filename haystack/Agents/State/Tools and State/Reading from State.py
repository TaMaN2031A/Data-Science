from haystack.tools import Tool
from haystack.components.agents.agent import Agent
from haystack.components.generators.chat import HuggingFaceAPIChatGenerator
from haystack.utils.hf import HFGenerationAPIType
from haystack.dataclasses import ChatMessage

def search_documents(query: str, user_context: str) -> dict:
    """Search documents using query and user context."""
    return {
        "results": [f"Found results for '{query}' (user: {user_context})"],
    }

search_tool = Tool(
    name="search",
    description="Search documents",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "user_context": {"type": "string"},
        },
        "required": ["query"],
    },
    function=search_documents,
    inputs_from_state={"user_name": "user_context"}
)

agent = Agent(
    chat_generator=HuggingFaceAPIChatGenerator(api_type=HFGenerationAPIType.SERVERLESS_INFERENCE_API,
                                  api_params={"model": "Qwen/Qwen2.5-7B-Instruct",
                                             "provider": "together"}),
    tools=[search_tool],
    state_schema={
        "user_name": {"type": str},
        "search_results": {"type": list}
    }
)

result = agent.run(
    messages=[ChatMessage.from_user("Search for Python tutorials")],
    user_name="Alice"
)

print(result)