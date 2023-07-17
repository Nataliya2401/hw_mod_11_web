import time
from ipaddress import ip_address
from typing import Callable
import redis.asyncio as redis
import uvicorn

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session
from sqlalchemy import text

from src.database.db import get_db
from src.routes import contacts, auth, users  # підключення роутів до апі
from src.conf.config import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')  # підключення роутів до апі
app.include_router(users.router, prefix='/api')

ALLOWED_IPS = [ip_address('192.168.1.0'), ip_address('172.16.0.0'), ip_address("127.0.0.1")]


# @app.middleware("http")
# async def limit_access_by_ip(request: Request, call_next: Callable):
#     """
#     The limit_access_by_ip function is a middleware function that limits access to the API by IP address.
#     It checks if the client's IP address is in ALLOWED_IPS, and if not, returns a 403 Forbidden response.
#
#     :param request: Request: Get the client's ip address
#     :param call_next: Callable: Pass the next function in the chain of middleware
#     :return: A json-response object
#     """
#     ip = ip_address(request.client.host)
#     if ip not in ALLOWED_IPS:
#         return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Not allowed IP address"})
#     response = await call_next(request)
#     return response


# @app.on_event("startup")
# async def startup():
#     r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)
#     await FastAPILimiter.init(r)

@app.on_event("startup")
async def startup():
    r = await redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        db=0,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(r)


# @app.middleware('http')
# async def custom_middleware(request: Request, call_next):
#     start_time = time.time()
#     response = await call_next(request)
#
#     during = time.time() - start_time
#     response.headers['performance'] = str(during)
#     return response


# TODO: read
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def main():
    """
    The main function return welcome <Hello!!!> message
    :return: dictionary with message
    """
    return {"msg": "Hello!!!!"}


# @app.get("/api/healthchecker")
# def healthchecker(db: Session = Depends(get_db)):
#     try:
#         # Make request
#         result = db.execute(text("SELECT 1")).fetchone()
#         if result is None:
#             raise HTTPException(status_code=500, detail="Database is not configured correctly")
#         return {"message": "Welcome to FastAPI!"}
#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=500, detail="Error connecting to the database")


if __name__ == "__main__":
    uvicorn.run(app, host=settings.main_host, port=settings.main_port)

# if __name__ == '__main__':
#     uvicorn.run(app, host='0.0.0.0', port=8000)
