# Handlers control how values are merged when set() is called on an existing
# key.
# State provides two default handlers: merge_lists, replace_values
# merge_lists => combines the lists (default for list types)
# replace_values => overwrites the existing values (default for non-list)

from haystack.components.agents.state.state_utils import merge_lists, replace_values
from haystack.components.agents.state import State

schema = {
    "documents": {"type": list}, # default handler is merge_lists
    "user_name": {"type": str},  # default is replace_values
    "count": {"type": int}       # default is replace_values
}

state = State(schema=schema)

state.set("documents", [1, 2])
state.set("documents", [3, 4])

print(state.get("documents"))
# [1, 2, 3, 4]

state.set("user_name", "Alice")
state.set("user_name", "Bob")
print(state.get("user_name"))
# Bob