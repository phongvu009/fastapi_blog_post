# Import the FastAPI pieces used to serve the app, render templates,
# and return consistent API or HTML error responses.
from  fastapi import FastAPI, Request, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import  Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from schemas import PostCreate, PostResponse

# Create the FastAPI application instance that exposes the routes below.
app = FastAPI()

# Serve static assets such as CSS, JavaScript, and images from the static folder.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates let the app render HTML pages using Jinja2 files from the templates folder.
templates = Jinja2Templates(directory="templates")

# Simple in-memory blog data used while the app is running.
# In a real project, this would usually come from a database.
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

# Render the home page and pass the post list into the Jinja template.
@app.get("/", name="home", include_in_schema=False)
def home(request: Request ):
    return templates.TemplateResponse(request,"home.html", {"posts": posts, "title" : "Home Page"})

# Render an individual blog post page for browser users.
@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            title = post["title"][:50]
            return templates.TemplateResponse(request, "post.html", {"post": post, "title": title})
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POST NOT FOUND")

# API endpoint returning all posts as JSON using the PostResponse schema.
@app.get("/api/posts", response_model=list[PostResponse])
def get_posts():
    return posts

# API endpoint returning a single post by ID or a 404 response.
@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_posts(post_id: int):
    for post in posts:
        if post.get("id") ==  post_id:
            return post

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POST NOT FOUND")

@app.post("/api/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post( post: PostCreate):
    new_id = max( p["id"] for p in posts) + 1 if posts else 1
    new_post = {
        "id": new_id,
        "author": post.author,
        "content": post.content,
        "date_posted": "April 23, 2025"
    }
    posts.append(new_post)
    return new_post



# Handle framework-level HTTP errors with a different response for API vs browser pages.
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


# Return validation errors in JSON for API calls and a friendly HTML page for browser requests.
@app.exception_handler(RequestValidationError)
def valdiation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()}
        )
    
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
    )