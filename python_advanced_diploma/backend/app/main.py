from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .api import tweets, users, media

app = FastAPI()

# Подключаем роутеры
app.include_router(tweets.router)
app.include_router(users.router)
app.include_router(media.router)

# Подключаем статические файлы (для доступа к медиа)
app.mount("/media", StaticFiles(directory="media"), name="media")


@app.get("/")
async def root():
    return {"message": "Twitter-like API"}
