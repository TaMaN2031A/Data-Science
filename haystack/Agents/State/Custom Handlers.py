from haystack.components.agents.state import State
"""Define custom handlers for specific merge behavior"""

def custom_merge(current_value, new_value):
    """Custom handler that merges and sorts lists"""
    current_value = current_value or []
    new_list = new_value if isinstance(new_value, list) else [new_value]
    return sorted(current_value + new_list)

schema = {
    "numbers": {"type": list, "handler": custom_merge}
}

state = State(schema=schema)
state.set("numbers", [3, 1])
state.set("numbers", [4, 2])
print(state.get("numbers"))

"""Override handlers for individual operations"""

def concatenate_strings(current, new):
    return f"{current}--{new}" if current else new

schema = {"user_name": {"type": str}}
state = State(schema=schema)

state.set("user_name", "Alice")
print(state.get("user_name"))
state.set("user_name", "Bob")
print(state.get("user_name"))
state.set("user_name", "Charlie", handler_override=concatenate_strings)
print(state.get("user_name"))
state.set("user_name", "David")
print(state.get("user_name"))