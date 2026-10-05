from  fastapi import FastAPI, Request, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import  Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

posts: list[dict] = [
    {
        "id": 1,
        "author": "Corey Schafer",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "author": "Jane Doe",
        "title": "Python is Great for Web Development",
        "content": "Python is a great language for web development, and FastAPI makes it even better.",
        "date_posted": "April 21, 2025",
    },
]

@app.get("/", name="home", include_in_schema=False)
def home(request: Request ):
    return templates.TemplateResponse(request,"home.html", {"posts": posts, "title" : "Home Page"})

@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            title = post["title"][:50]
            return templates.TemplateResponse(request, "post.html", {"post": post, "title": title})
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POST NOT FOUND")

@app.get("/api/posts", include_in_schema=False)
def get_posts():
    return posts

@app.get("/api/posts/{post_id}")
def get_posts(post_id: int):
    for post in posts:
        if post.get("id") ==  post_id:
            return post

    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POST NOT FOUND")

@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message},
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )



# @app.exception_handler(RequestValidationError)
# def valdiation_exception_handler(request: Request, exception: RequestValidationError):
#     if request.url.path.startwith("/api"):
#         return JSONResponse(
#             status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
#             content={"detail": exception.error()}
#         )
    
#     return templates.TemplateResponse(
#         request,
#         "error.html",
#         {
#             "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
#             "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
#             "message": "Invalid request. Please check your input and try again.",
#         },
#         status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
#     )