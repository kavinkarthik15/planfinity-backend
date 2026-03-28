from pydantic import BaseModel, Field


class Transaction(BaseModel):
	user_id: str = Field(..., examples=["user1"])
	amount: float = Field(..., examples=[400])
	system_category: str = Field(..., examples=["food"])
	date: str = Field(..., examples=["2026-03-21"])
