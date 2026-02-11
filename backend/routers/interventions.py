
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from database import get_db
from models import Intervention
from services.intervention_service import generate_interventions
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(
    prefix="/interventions",
    tags=["interventions"]
)

class InterventionResponse(BaseModel):
    id: int
    machine_id: int
    type: str
    priority: str
    status: str
    description: Optional[str] = None
    date_created: datetime

    class Config:
        orm_mode = True

@router.post("/generate")
async def generate_intervention_plan(db: AsyncSession = Depends(get_db)):
    """
    Triggers the intervention generation logic based on current machine data.
    """
    try:
        count = await generate_interventions(db)
        return {"message": f"Successfully generated {count} interventions.", "count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[InterventionResponse])
async def get_interventions(
    priority: Optional[str] = None,
    status: Optional[str] = None,
    machine_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch interventions with optional filtering.
    """
    stmt = select(Intervention)
    
    if priority:
        stmt = stmt.where(Intervention.priority == priority)
    if status:
        stmt = stmt.where(Intervention.status == status)
    if machine_id:
        stmt = stmt.where(Intervention.machine_id == machine_id)
        
    result = await db.execute(stmt)
    return result.scalars().all()
