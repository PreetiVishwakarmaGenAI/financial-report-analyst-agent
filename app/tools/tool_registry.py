class ToolRegistry:

    def __init__(self):
        self.tools = {}

    def register(self, tool):
        self.tools[tool.name] = tool

    def get_tool(self, name):
        return self.tools.get(name)

    def list_tools(self):
        """
        Returns all registered tools.
        """
        return list(self.tools.values())

    def get_tools_description(self) -> str:
        """
        Returns a formatted string that can be injected
        into the Planner prompt.
        """

        descriptions = []

        for tool in self.tools.values():
            descriptions.append(
                f"- {tool.name}: {tool.description}"
            )

        return "\n".join(descriptions)