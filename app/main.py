from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, contacts  # Assuming `app` is the top-level directory
from app.database import engine, SessionLocal
from app import models
from fastapi_limiter import FastAPILimiter
import redis
import os

# Create the database tables based on the models
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI()

# CORS (Cross-Origin Resource Sharing) middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, you can configure specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers for users and contacts
app.include_router(users.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")

# Redis configuration from environment variables
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

# Startup event: Initialize FastAPILimiter with Redis client
@app.on_event("startup")
async def startup():
    redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    redis_client = redis.StrictRedis.from_url(redis_url)
    await FastAPILimiter.init(redis_client)

# Shutdown event: Close the Redis connection
@app.on_event("shutdown")
async def shutdown():
    redis_client = await FastAPILimiter.redis()
    redis_client.connection_pool.disconnect()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
