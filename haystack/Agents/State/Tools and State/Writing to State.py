from haystack.tools import Tool
from haystack.components.agents.agent import Agent
from haystack.components.generators.chat import HuggingFaceAPIChatGenerator
from haystack.utils.hf import HFGenerationAPIType
from haystack.dataclasses import ChatMessage

def retrieve_documents(query: str) -> dict:
    """Retrieve documents based on a query"""
    return {
        "documents": [
            {"title": "Python is fast", "content": "Python is fast, although it is interpreter-based language"},
            {"title": "Python is the second-best language for any task",
             "content": "Python will be almost always an option to solve your "
                        "technical problems"},
        ],
        "count": 2,
        "query": query
    }

retrieve_tool = Tool(
    name="retrieve",
    description="Retrieve relevant documents",
    parameters={
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"]
    },
    function=retrieve_documents,
    outputs_to_state={
        "documents": {"source": "documents"},
        "result_count": {"source": "count"}, # Maps tool's count to state's result_count
        "last_query": {"source": "query"}
        # Each mapping specifies: source (from tool's o/p) and handler (Optional => custom function for merging values)
    }
)

agent = Agent(
    chat_generator=HuggingFaceAPIChatGenerator(api_type=HFGenerationAPIType.SERVERLESS_INFERENCE_API,
                                  api_params={"model": "Qwen/Qwen2.5-7B-Instruct",
                                             "provider": "together"}),
    tools=[retrieve_tool],
    state_schema={
        "documents": {"type": list},
        "result_count": {"type": int},
        "last_query": {"type": str},
    }
)

result = agent.run(
    messages=[ChatMessage.from_user("Find information about Python")]
)

documents = result["documents"]
result_count = result["result_count"]
last_query = result["last_query"]

print(documents)
print(result_count)
print(last_query)
print(result)