import math
from haystack.components.agents import Agent
from haystack.dataclasses import ChatMessage
from haystack.tools import Tool
from haystack.components.generators.chat import HuggingFaceAPIChatGenerator
from haystack.utils.hf import HFGenerationAPIType
# Tool 1: Calculate factorial
def factorial(n: int) -> dict:
    """Calculate the factorial of a number."""
    result = math.factorial(n)
    return {"result": result}

factorial_tool = Tool(
    name="factorial",
    description="Calculate the factorial of a number",
    parameters={
        "type": "object",
        "properties": {"n": {"type": "integer"}},
        "required": ["n"]
    },
    function=factorial,
    outputs_to_state={"factorial_result": {"source": "result"}}
)

# Tool 2: Perform calculation
def calculate(expression: str) -> dict:
    """Evaluate a mathematical expression."""
    result = eval(expression, {"__builtins__": {}})
    return {"result": result}

calculator_tool = Tool(
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

# Create agent with both tools
agent = Agent(
    chat_generator=HuggingFaceAPIChatGenerator(api_type=HFGenerationAPIType.SERVERLESS_INFERENCE_API,
                                  api_params={"model": "Qwen/Qwen2.5-72B-Instruct",
                                             "provider": "together"}),
    tools=[calculator_tool, factorial_tool],
    state_schema={
        "calc_result": {"type": int},
        "factorial_result": {"type": int}
    }
)

# Run the agent
result = agent.run(
    messages=[ChatMessage.from_user("Calculate the factorial of 5, then multiply it by 2")]
)

# Access state values from result
print(result)
factorial_result = result["factorial_result"]
calc_result = result["calc_result"]

# Access conversation messages
for message in result["messages"]:
    print(f"{message.role}: {message.text}")