from datetime import datetime
from typing import Dict
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    environment: str
    timestamp: datetime
    model_loaded: bool
    model_path: str
    db_connected: bool
    details: Dict[str, str]
