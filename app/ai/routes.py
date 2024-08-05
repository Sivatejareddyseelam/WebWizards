from typing import List, Union
from uuid import uuid4
#from fastapi import FastAPI
from models import seo_optimizer
#from fastapi import HTTPException
from pydantic import BaseModel, Field
from enum import Enum


class Engine(str, Enum):
    openai= "chat gpt"
    gemini = "gemini pro vision"

class Image(BaseModel):
    url: str
    id: str


class Request(BaseModel):
    engine: Engine = Field(max_length=50,
                                 default="gemini pro vision",
                               description="AI engine to be used")
    focus_words: Union[str, None] = Field(default=None)
    text : Union[str, None] = Field(default=None)
    images: Union[List[Image], None] = Field(
                                 default=None,
                               description="list of images")
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "engine": "gemini pro vision",
                    "focus_words": "word1, word2, word3",
                    "text": "A very nice text",
                    "images": [{"url": "https://prospectsinfluentialnew.cgcolors.co/wp-content/uploads/2024/04/WallpapersMania_vol158-028-1024x640.jpg",
                                "id": "image1"}, {"url": "https://prospectsinfluentialnew.cgcolors.co/wp-content/uploads/2024/04/WallpapersMania_vol158-028-1024x640.jpg",
                                "id": "image2"}]
                }
            ]
        }
    }

class Response(BaseModel):
    text: dict


async def root():
    """
    defining the root
    """
    return {"greeting":"Welcome to seo_optimizer"}



async def get_engines():
    return {"models": ['chat gpt', 'gemini pro vision']}



async def get_composite_call(req: Request) -> Response:
    client = seo_optimizer(req.engine)
    response = await client.get_composite(req.text, req.focus_words, req.images)
    return Response(text=response)



async def get_meta_tile(req: Request) -> Response:
    client = seo_optimizer(req.engine)
    response = await client.get_meta_title(req.text, req.focus_words, req.images)
    return Response(text=response)



async def get_meta_description(req: Request) -> Response:
    client = seo_optimizer(req.engine)
    response = await client.get_meta_description(req.text, req.focus_words, req.images)
    return Response(text=response)



async def get_meta_alt_tags(req: Request) -> Response:
    client = seo_optimizer(req.engine)
    response = await client.get_alt_tags(req.text, req.focus_words, req.images)
    return Response(text=response)



async def get_fb_og_tile(req: Request) -> Response:
    client = seo_optimizer(req.engine)
    response = await client.get_fb_og_title(req.text, req.focus_words, req.images)
    return Response(text=response)



async def get_fb_og_description(req: Request) -> Response:
    client = seo_optimizer(req.engine)
    response = await client.get_fb_og_description(req.text, req.focus_words, req.images)
    return Response(text=response)



async def get_fb_composite_call(req: Request) -> Response:
    client = seo_optimizer(req.engine)
    response = await client.get_fb_composite(req.text, req.focus_words, req.images)
    return Response(text=response)



async def get_x_og_tile(req: Request) -> Response:
    client = seo_optimizer(req.engine)
    response = await client.get_x_og_title(req.text, req.focus_words, req.images)
    return Response(text=response)



async def get_x_og_description(req: Request) -> Response:
    client = seo_optimizer(req.engine)
    response = await client.get_x_og_description(req.text, req.focus_words, req.images)
    return Response(text=response)



async def get_x_composite_call(req: Request) -> Response:
    client = seo_optimizer(req.engine)
    response = await client.get_x_composite(req.text, req.focus_words, req.images)
    return Response(text=response)



async def get_social_composite_call(req: Request) -> Response:
    client = seo_optimizer(req.engine)
    response = await client.get_social_composite(req.text, req.focus_words, req.images)
    return Response(text=response)