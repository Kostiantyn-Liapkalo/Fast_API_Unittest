import time
from pathlib import Path

import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.conf.config import settings
from src.database.db import get_db
from src.routes import contacts, auth

app = FastAPI(swagger_ui_parameters={"operationsSorter": "method"}, title='Contact book')


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are needed by your app,
    like connecting to databases or initializing caches.

    :return: A list of tasks to be run
    """
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)
    await FastAPILimiter.init(r)


origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    The add_process_time_header function is a middleware function that adds the time it took to process
    the request as a header in the response. This can be used to measure performance of an application.

    :param request: Request: Access the request object
    :param call_next: Call the next function in the middleware chain
    :return: A response object
    """
    start_time = time.time()
    print(request.client)
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["performance"] = str(process_time)
    return response


templates = Jinja2Templates(directory='templates')
BASE_DIR = Path(__file__).parent
app.mount('/static', StaticFiles(directory=BASE_DIR / 'static'), name='static')


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    The root function is the entry point for the web application.
    It returns a TemplateResponse object, which renders an HTML template using Jinja2.
    The template is located in templates/index.html and uses data from request to render itself.

    :param request: Request: Get the request object for the current request
    :return: A templateresponse, which is a type of response
    """
    return templates.TemplateResponse('index.html', {"request": request})


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    """
    The healthchecker function is a simple function that checks if the database is configured correctly.
    It does this by executing a SQL query and checking if it returns any results. If it doesn't, then we know something's wrong.

    :param db: Session: Pass the database session to the function
    :return: A dictionary with a message
    """
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix="/api")
