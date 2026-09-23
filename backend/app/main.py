from fastapi import FastAPI
from app.api.ingest import router
from app.config.settings import settings

app = FastAPI()
app.include_router(router) #Adding the route to app via router


print(settings.app_name)

#this file is the entry point of the application, where we create an instance of the FastAPI class and include the router that defines the API endpoints. The settings are also printed to verify that they are loaded correctly from the .env file.














