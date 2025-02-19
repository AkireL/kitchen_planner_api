from fastapi import FastAPI
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address


def config_rate_limit(app: FastAPI) -> None:
    limiter = Limiter(key_func=get_remote_address, default_limits=["5/minute"])
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)