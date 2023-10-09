from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from tortoise import Tortoise

from databases.redis import RedisClient
from services.auth import auth_service
from services.id import id_service
from services.location import location_service
from session import SingletonSession
from settings import config


@asynccontextmanager
async def manage_session(app: FastAPI):
    RedisClient.get_client()
    SingletonSession.get_session()
    await Tortoise.init(
        db_url=config["POSTGRES_HOST"]
        or "postgres://postgres:postgres@localhost:5432/postgres",
        modules={"models": ["models.tables"]},
        use_tz=True,
    )
    await Tortoise.generate_schemas()
    yield
    await SingletonSession.close_session()
    await Tortoise.close_connections()


app = FastAPI(lifespan=manage_session)

app.mount("/auth", auth_service)
app.mount("/id", id_service)
app.mount("/location", location_service)

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
