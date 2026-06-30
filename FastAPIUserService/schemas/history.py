from pydantic import BaseModel, Field



class HistoryCheckResponse(BaseModel):
    is_view: bool = Field(..., alias="isView")