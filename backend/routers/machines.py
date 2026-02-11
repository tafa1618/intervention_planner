
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional, Any
from database import get_db
from models import Machine, Client, Intervention
from pydantic import BaseModel

router = APIRouter(
    prefix="/machines",
    tags=["machines"]
)

# Pydantic Models for Response
class InterventionDTO(BaseModel):
    id: int
    type: str
    priority: str
    status: str
    description: Optional[str] = None
    date_created: Any # datetime

    class Config:
        orm_mode = True

class LocationDTO(BaseModel):
    lat: float
    lng: float
    address: Optional[str] = None

class MachineDTO(BaseModel):
    id: int
    serialNumber: str
    model: Optional[str] = None
    client: str 
    location: LocationDTO
    status: str
    pendingInterventions: List[InterventionDTO] = []
    
    class Config:
        orm_mode = True

@router.get("/", response_model=List[MachineDTO])
async def get_machines(
    skip: int = 0, 
    limit: int = 1000, 
    serialNumber: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch all machines with client name and pending interventions.
    Optimized with eager loading.
    """
    # Use selectinload to eagerly fetch relationships properly in async
    query = select(Machine).options(
        selectinload(Machine.client),
        selectinload(Machine.interventions)
    )
    
    if serialNumber:
        query = query.where(Machine.serial_number == serialNumber)

    if search:
        search_term = f"%{search}%"
        query = query.outerjoin(Client).where(
            or_(
                Machine.serial_number.ilike(search_term),
                Machine.model.ilike(search_term),
                Client.name.ilike(search_term)
            )
        )
        
    stmt = query.limit(limit).offset(skip)
    
    result = await db.execute(stmt)
    machines = result.scalars().all()
    
    # Transform to DTO format expected by frontend
    response = []
    for m in machines:
        # Determine status (mock logic based on fields or intervention count)
        status = 'operational'
        if m.psi_status == 'Non Inspecté':
            status = 'maintenance'
        
        # Check if there are breakdown interventions? (e.g. SOS high priority)
        has_urgent = any(i.priority == 'HIGH' for i in m.interventions)
        if has_urgent:
             status = 'critical' # visual indicator

        # Location fallback
        lat = m.latitude if m.latitude else 0.0
        lng = m.longitude if m.longitude else 0.0
        
        # Address fallback
        address = m.client.name if m.client else "Unknown Location"

        machine_dto = MachineDTO(
            id=m.id,
            serialNumber=m.serial_number,
            model=m.model,
            client=m.client.name if m.client else "Unknown Client",
            location=LocationDTO(lat=lat, lng=lng, address=address),
            status=status,
            pendingInterventions=[
                InterventionDTO(
                    id=i.id,
                    type=i.type,
                    priority=i.priority,
                    status=i.status,
                    description=i.description,
                    date_created=i.date_created
                ) for i in m.interventions if i.status == 'PENDING'
            ]
        )
        response.append(machine_dto)
        
    return response
