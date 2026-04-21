from app.services.agent.agent import make_graph


class ChatAgentProvider:
    def build(self, checkpointer):
        return make_graph(config={"checkpointer": checkpointer})
