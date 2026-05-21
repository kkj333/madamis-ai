"""API リクエスト / レスポンスモデル。"""

from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    text: str
    user_id: str | None = None


class ChatResponse(BaseModel):
    reply: str


class InterpretRequest(BaseModel):
    text: str
    user_id: str


class Ingredient(BaseModel):
    name: str = Field(description="Name of the ingredient.")
    quantity: str = Field(
        description="Quantity of the ingredient, including units."
    )


class Recipe(BaseModel):
    """Google genai structured-output repro schema."""

    recipe_name: str = Field(description="The name of the recipe.")
    prep_time_minutes: Optional[int] = Field(
        description="Optional time in minutes to prepare the recipe."
    )
    ingredients: List[Ingredient]
    instructions: List[str]
