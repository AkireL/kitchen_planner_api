from langchain.tools import tool


@tool("get_weather", description="Get weather for a given city")
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


tools = [get_weather]
