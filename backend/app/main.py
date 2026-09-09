from fastapi import FastAPI
from app.api.ingest import router
from app.config.settings import settings

app = FastAPI()
app.include_router(router) #Adding the route to app via router


print(settings.app_name)
















