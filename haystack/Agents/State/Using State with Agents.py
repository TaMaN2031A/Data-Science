from haystack.components.agents.agent import Agent
from haystack.components.generators.chat import HuggingFaceAPIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.tools import Tool

# Define a simple calculation tool
def calculate(expression: str) -> dict:
    """Evaluate a mathematical expression"""
    result = eval(expression, {"__builtins__": {}})
    return {"result": result}

# Create a tool that writes to state
calculate_tool = Tool(
    name="calculator",
    description="Evaluate basic math expressions",
    parameters={
        "type": "object",
        "properties": {"expression": {"type": "string"}},
        "required": ["expression"]
    },
    function=calculate,
    outputs_to_state={"calc_result": {"source": "result"}}
)

agent = Agent(
    chat_generator=HuggingFaceAPIChatGenerator("mistralai/Mistral-7B-Instruct-v0.2"),
    tools=[calculate_tool],
    state_schema={"calc_result": {"type": int}}
)

result = agent.run(
    messages=[ChatMessage.from_user("Calculate 15 + 27")]
)

print(result)