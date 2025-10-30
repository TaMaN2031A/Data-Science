
from haystack.utils.hf import HFGenerationAPIType
from haystack.components.agents import Agent
from haystack.components.generators.chat import HuggingFaceAPIChatGenerator
from haystack.components.websearch import SerperDevWebSearch
from haystack.dataclasses import Document, ChatMessage
from haystack.tools.component_tool import ComponentTool
from haystack.utils import Secret

from typing import List

web_search = SerperDevWebSearch(top_k=3)
web_tool = ComponentTool(component=web_search,
                         name="web_search",
                         description="Search the web for current information like weather, news, or facts.")
tool_calling_agent = Agent(
    chat_generator=HuggingFaceAPIChatGenerator(api_type=HFGenerationAPIType.SERVERLESS_INFERENCE_API,
                                  api_params={"model": "Qwen/Qwen2.5-7B-Instruct",
                                             "provider": "together"},
                                  token=Secret.from_env_var("HF_TOKEN")),
    system_prompt="""You're a helpful agent. When asked about current information like weather, news, or facts, 
                     use the web_search tool to find the information and then summarize the findings.
                     When you get web search results, extract the relevant information and present it in a clear, 
                     concise manner""",
    tools=[web_tool]
)

user_message = ChatMessage.from_user("How is the weather in Berlin")
result = tool_calling_agent.run(messages=[user_message])
print(result["messages"][-1].text)