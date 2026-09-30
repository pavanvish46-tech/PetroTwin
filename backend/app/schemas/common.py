from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Literal

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    model_config = ConfigDict(from_attributes=True)

class WellSummary(BaseModel):
    well_id: str
    field: str
    status: str
    latest_state: dict[str, Any]

class PredictionRequest(BaseModel):
    well_id: str
    scenario: dict[str, float | int] = Field(default_factory=dict)

class PredictionResponse(BaseModel):
    well_id: str
    prediction_type: str
    value: float
    lower_bound: float | None = None
    upper_bound: float | None = None
    model_version: str
    status: str = "ok"

class SimulationRequest(BaseModel):
    well_id: str
    scenario: dict[str, float | int]

class OptimizationRequest(BaseModel):
    well_id: str

class DecisionRequest(BaseModel):
    status: Literal["approved", "modified", "rejected"]
    decision_note: str | None = None

class RecommendationResponse(BaseModel):
    id: int
    well_id: str
    status: str
    strategy_name: str
    scenario: dict[str, Any]
    result: dict[str, Any]
    explanation: dict[str, Any]
