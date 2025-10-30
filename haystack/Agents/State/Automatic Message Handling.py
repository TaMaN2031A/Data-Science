from haystack.components.agents.state import State

state = State(schema={"user_id": {"type": str}})
print(type(state.data)) # it stores

print("messages" in state.schema)
print(state.schema["messages"]["type"])

messages = state.get("messages", [])
print(type(messages))