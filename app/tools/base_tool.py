class BaseTool:

    name: str

    def run(self, state):
        raise NotImplementedError