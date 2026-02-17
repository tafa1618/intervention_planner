
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
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

class ClientStatsDTO(BaseModel):
    name: str
    count: int

def calculate_machine_status_and_interventions(m: Machine):
    """
    Central logic to determine machine status and synthesize virtual interventions.
    """
    status = 'operational'
    virtual_interventions = []
    
    # helper for scores
    def is_low_score(val):
        if val is None: return False
        s_val = str(val).strip().lower()
        if s_val in ['0', '1', '0.0', '1.0', '0/1']:
            return True
        if '/' in s_val:
            parts = [p.strip() for p in s_val.split('/')]
            if parts[0] == '0' and len(parts) > 1 and parts[1] != '0':
                return True
        return False

    # 1. Check for Critical (RED)
    has_urgent_intervention = any(i.priority == 'HIGH' for i in m.interventions if i.status == 'PENDING')
    excel_status_raw = str(m.status).lower() if m.status else ""
    is_urgent_excel = any(term in excel_status_raw for term in ["défaut", "urgent", "critique", "critical", "breakdown"])
    
    # CVA Logic (RED if 0/1)
    is_urgent_cva_score = False
    if m.cvaf:
        sos = m.cvaf.sos_score
        insp = m.cvaf.inspection_score
        if is_low_score(sos) or is_low_score(insp):
            is_urgent_cva_score = True

    if is_urgent_excel:
        virtual_interventions.append({
            "id": -1, "type": "ALERTE", "priority": "HIGH", "status": "PENDING", 
            "description": f"Statut Excel: {m.status}", "date_created": m.last_reported_time
        })
        status = 'critical'
    elif has_urgent_intervention:
        status = 'critical'
    elif is_urgent_cva_score:
        status = 'critical'

    # 2. Virtual Interventions Details
    if m.cvaf:
        virtual_interventions.append({
            "id": -3, "type": "CONTRAT CVA", 
            "priority": "HIGH" if is_urgent_cva_score else "LOW", 
            "status": "PENDING",
            "description": f"Type: {m.cvaf.cva_type} | SOS: {m.cvaf.sos_score or 'N/A'} | Insp: {m.cvaf.inspection_score or 'N/A'}", 
            "date_created": None
        })

    if m.psi_status == 'Non Inspecté':
         virtual_interventions.append({
            "id": -2, "type": "INSPECTION", "priority": "MEDIUM", "status": "PENDING",
            "description": "Machine non inspectée (PSI)", "date_created": None
        })
         if status == 'operational': status = 'maintenance'

    if m.suivi_ps:
        for i, ps in enumerate(m.suivi_ps):
            virtual_interventions.append({
                "id": -100 - i, "type": "CAMPAGNE PS", "priority": "LOW", "status": "PENDING",
                "description": f"{ps.ps_type}: {ps.description} (Ref: {ps.reference_number})", "date_created": ps.date
            })

    if m.remote_service and m.remote_service.flash_update == '1':
        virtual_interventions.append({
            "id": -4, "type": "REMOTE SERVICE", "priority": "MEDIUM", "status": "PENDING",
            "description": "Mise à jour Flash requise", "date_created": None
        })
        if status == 'operational': status = 'maintenance'
        
    # Medium priority interventions
    has_medium_intervention = any(i.priority == 'MEDIUM' for i in m.interventions if i.status == 'PENDING')
    if has_medium_intervention and status == 'operational':
         status = 'maintenance'

    # Combine
    all_interventions = [
        InterventionDTO(
            id=i.id, type=i.type, priority=i.priority, status=i.status,
            description=i.description, date_created=i.date_created
        ) for i in m.interventions if i.status == 'PENDING'
    ] + [InterventionDTO(**vi) for vi in virtual_interventions]

    return status, all_interventions

@router.get("/global-search", response_model=List[MachineContextDTO])
async def search_global_context(
    q: str,
    db: AsyncSession = Depends(get_db)
):
    search_term = f"%{q}%"
    query = select(Machine).options(
        selectinload(Machine.client),
        selectinload(Machine.interventions),
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
        is_connected = m.latitude is not None and m.longitude is not None
        status, _ = calculate_machine_status_and_interventions(m)
        
        cvaf_status = m.cvaf.cva_type if m.cvaf else None
        inspection_status = m.inspection_rate[0].last_inspect if m.inspection_rate else None
        remote_status = m.remote_service.flash_update if m.remote_service else None
        suivi_count = len(m.suivi_ps) if m.suivi_ps else 0
        
        loc_dto = LocationDTO(lat=m.latitude, lng=m.longitude, address=m.client.name if m.client else "") if is_connected else None

        dto = MachineContextDTO(
            id=m.id,
            serialNumber=m.serial_number,
            model=m.model,
            client=m.client.name if m.client else "Unknown",
            location=loc_dto,
            status=status,
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
    query = select(Machine).options(
        selectinload(Machine.client),
        selectinload(Machine.interventions),
        selectinload(Machine.suivi_ps),
        selectinload(Machine.remote_service),
        selectinload(Machine.cvaf),
        selectinload(Machine.inspection_rate)
    )
    
    if serialNumber:
        query = query.where(Machine.serial_number == serialNumber)
    if search:
        search_term = f"%{search}%"
        query = query.outerjoin(Client).where(
            or_(Machine.serial_number.ilike(search_term), Machine.model.ilike(search_term), Client.name.ilike(search_term))
        )
        
    result = await db.execute(query.limit(limit).offset(skip))
    machines = result.scalars().all()
    
    response = []
    for m in machines:
        status, interventions = calculate_machine_status_and_interventions(m)
        lat = m.latitude if m.latitude else 0.0
        lng = m.longitude if m.longitude else 0.0
        
        response.append(MachineDTO(
            id=m.id,
            serialNumber=m.serial_number,
            model=m.model,
            client=m.client.name if m.client else "Unknown Client",
            location=LocationDTO(lat=lat, lng=lng, address=m.client.name if m.client else ""),
            status=status,
            pendingInterventions=interventions
        ))
    return response

@router.get("/clients", response_model=List[ClientStatsDTO])
async def get_all_clients(db: AsyncSession = Depends(get_db)):
    """Returns a list of all unique clients with their machine counts."""
    query = (
        select(Client.name, func.count(Machine.id).label("count"))
        .join(Machine, Machine.client_id == Client.id)
        .group_by(Client.name)
        .order_by(Client.name)
    )
    result = await db.execute(query)
    rows = result.all()
    
    return [ClientStatsDTO(name=row[0], count=row[1]) for row in rows]
