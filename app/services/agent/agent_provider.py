from app.services.agent.graph import make_graph


class ChatAgentProvider:
    def build(self, checkpointer):
        return make_graph(config={"checkpointer": checkpointer})
