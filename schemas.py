# Pydantic schemas define the shape of blog data for validation and serialization.
from pydantic import BaseModel, ConfigDict, Field

# Shared fields used by both creation and response models.
class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1, max_length=50)

# Input model for creating a new blog post.
class PostCreate(PostBase):
    pass

# Output model returned from the API; includes the generated ID and publication date.
class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_posted: str

