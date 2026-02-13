
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional, Any
from database import get_db
from models import Machine, Client, Intervention, CVAF, InspectionRate, RemoteService, SuiviPS
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
        from_attributes = True

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
        from_attributes = True

class ProgramStatusDTO(BaseModel):
    visionLink: bool
    cvaf: Optional[str] = None # 'Active', 'Expired', etc.
    inspection: Optional[str] = None # Date of last inspection
    remoteService: Optional[str] = None # Flash update status
    suiviPs: Optional[int] = 0 # Count of active campaigns

class MachineContextDTO(BaseModel):
    id: int
    serialNumber: str
    model: Optional[str] = None
    client: str
    location: Optional[LocationDTO] = None
    status: str
    programs: ProgramStatusDTO
    
    class Config:
        from_attributes = True

@router.get("/global-search", response_model=List[MachineContextDTO])
async def search_global_context(
    q: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Search for machines by Client Name, Serial Number, or Model.
    Returns a rich context including status from all programs.
    """
    search_term = f"%{q}%"
    
    # Eager load all context
    query = select(Machine).options(
        selectinload(Machine.client),
        selectinload(Machine.cvaf),
        selectinload(Machine.inspection_rate),
        selectinload(Machine.remote_service),
        selectinload(Machine.suivi_ps)
    ).outerjoin(Client).where(
        or_(
            Client.name.ilike(search_term),
            Machine.serial_number.ilike(search_term),
            Machine.model.ilike(search_term)
        )
    )
    
    result = await db.execute(query)
    machines = result.scalars().all()
    
    response = []
    for m in machines:
        # 1. VisionLink Status (Connected if location exists and recent?)
        # For now, if lat/lon is not None, we assume connected/reported.
        is_connected = m.latitude is not None and m.longitude is not None
        
        # 2. CVAF Status
        cvaf_status = None
        if m.cvaf:
            cvaf_status = m.cvaf.cva_type # e.g. "CVA" or "Standard"
        
        # 3. Inspection Status
        inspection_status = None
        if m.inspection_rate:
            # Maybe show last inspection date?
            # Issue: inspection_rate is a list in model (uselist=True)
            # But logic in ingestion treated it as list. Let's take the most recent one?
            # Actually model says: inspection_rate = relationship(..., uselist=True)
            # So we should iterate.
            if m.inspection_rate:
                 # Sort by date? or just take first found?
                 # For simplicity now, just take the first one's date or status
                 inspection_status = m.inspection_rate[0].last_inspect
        
        # 4. Remote Service (Flash Update)
        remote_status = None
        if m.remote_service:
            remote_status = m.remote_service.flash_update
            
        # 5. Suivi PS (Count)
        suivi_count = len(m.suivi_ps) if m.suivi_ps else 0
        
        # Location DTO
        loc_dto = None
        if is_connected:
            loc_dto = LocationDTO(
                lat=m.latitude, 
                lng=m.longitude, 
                address=m.client.name if m.client else ""
            )

        dto = MachineContextDTO(
            id=m.id,
            serialNumber=m.serial_number,
            model=m.model,
            client=m.client.name if m.client else "Unknown",
            location=loc_dto,
            status="active", # Placeholder, logic can be refined
            programs=ProgramStatusDTO(
                visionLink=is_connected,
                cvaf=cvaf_status,
                inspection=inspection_status,
                remoteService=remote_status,
                suiviPs=suivi_count
            )
        )
        response.append(dto)
        
    return response

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
