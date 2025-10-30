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