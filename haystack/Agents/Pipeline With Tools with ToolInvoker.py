"""
I'm trying to follow the documentation to build a tool-calling agent with
the help of ToolInvoker.

Code Illustration:
* OpenAIChatGenerator uses an LLM to analyze message & determine whether it
needs to initiate a tool call | return response directly
* ConditionalRouter directs the o/p of the OpenAIChatGenerator to either
(there_are_tools_calls, final_replies)
* ToolInvoker executes the tool call ordered from the LLM.
ComponentTool wraps (SerperDevWebSearch component) which fetches real-time
search results => making it accessible for ToolInvoker to execute it as a
tool. (ToolInvoker is the carpenter, ComponentTool is the hammer that
hits the metal)
* After the ComponentTool provides the output to the ToolInvoker, ToolInvoker
(the carpenter) sends the information (steel chair) to the OpenAIChatGenerator
along with the user original question stoed by the MessageCollector
"""

from haystack import component, Pipeline
from haystack.components.tools import ToolInvoker
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.routers import ConditionalRouter
from haystack.components.websearch import SerperDevWebSearch
from haystack.core.component.types import Variadic
from haystack.dataclasses import ChatMessage
from haystack.tools import ComponentTool

from typing import Any, Dict, List



@component()
class MessageCollector():
    def __init__(self):
        self._messages = []

    @component.output_types(messages=List[ChatMessage])
    def run(self, messages: Variadic[List[ChatMessage]]) -> Dict[str, Any]:
        self._messages.extend([msg for inner in messages for msg in inner])
        return {"messages": self._messages}

    def clear(self):
        self._messages = []

web_tool = ComponentTool(component=SerperDevWebSearch(top_k=3))

routes = [
    {
        "condition": "{{replies[0].tool_calls | length > 0}}",
        "output": "{{replies}}",
        "output_name": "there_are_tool_calls",
        "output_type": List[ChatMessage],
    },
    {
        "condition": "{{replies[0].tool_calls | length == 0}}",
        "output": "{{replies}}",
        "output_name": "final_replies",
        "output_type": List[ChatMessage],
    },
]

# Create the pipeline
tool_agent = Pipeline()
tool_agent.add_component("message_collector", MessageCollector())
tool_agent.add_component("generator", OpenAIChatGenerator(model="gpt-4o-mini", tools=[web_tool]))
tool_agent.add_component("router", ConditionalRouter(routes, unsafe=True))
tool_agent.add_component("tool_invoker", ToolInvoker(tools=[web_tool]))

tool_agent.connect("generator.replies", "router")
tool_agent.connect("router.there_are_tool_calls", "tool_invoker")
tool_agent.connect("router.there_are_tool_calls", "message_collector")
tool_agent.connect("tool_invoker.tool_messages", "message_collector")
tool_agent.connect("message_collector", "generator.messages")

messages = [
    ChatMessage.from_system("You're a helpful agent choosing the right tool when necessary"),
    ChatMessage.from_user("How is the weather in Berlin?")]
result = tool_agent.run({"messages": messages})

print(result["router"]["final_replies"][0].text)