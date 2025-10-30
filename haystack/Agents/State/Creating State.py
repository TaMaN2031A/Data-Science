from haystack.components.agents.state import State

schema = {
    "user_name": {"type": str},
    "documents": {"type": list},
    "count": {"type": int}
}

state = State(
    schema=schema,
    data={"user_name": "Alice", "documents": [], "count": 0}
)

"""Reading from a state"""
user_name = state.get("user_name")

documents = state.get("documents", [])

print(user_name, type(documents))

if state.has("user_name"):
    print(f"User: {state.get('user_name')}")

state.set("user_name", "Bob")
state.set("documents", [{"title": "Doc1", "content": "Content 1"}])

print(state.get("user_name"), state.get("documents"))

# State is schema-DS => THIS WILL CAUSE ERROR
# state.set("user_age", 17)
