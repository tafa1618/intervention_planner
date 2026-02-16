
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
        # Determine REAL status based on data
        # Colors: Green (operational), Orange (maintenance), Red (critical)
        
        status = 'operational'
        virtual_interventions = []
        
        # 1. Check for Critical (RED)
        # - High priority pending interventions
        has_urgent_intervention = any(i.priority == 'HIGH' for i in m.interventions if i.status == 'PENDING')
        
        # - Specific urgent statuses in Excel
        excel_status_raw = str(m.status).lower() if m.status else ""
        is_urgent_excel = any(term in excel_status_raw for term in ["défaut", "urgent", "critique", "critical", "breakdown"])
        
        if is_urgent_excel:
            virtual_interventions.append({
                "id": -1, "type": "ALERTE", "priority": "HIGH", "status": "PENDING", 
                "description": f"Statut Excel: {m.status}", "date_created": m.last_reported_time
            })
            status = 'critical'
        elif has_urgent_intervention:
            status = 'critical'
        
        # 2. Check for Maintenance (ORANGE) and add program details
        
        # - Inspection (PSI)
        if m.psi_status == 'Non Inspecté':
             virtual_interventions.append({
                "id": -2, "type": "INSPECTION", "priority": "MEDIUM", "status": "PENDING",
                "description": "Machine non inspectée (PSI)", "date_created": None
            })
             if status == 'operational': status = 'maintenance'
        elif m.last_visit:
             # Just info if already inspected? Maybe skip from "interventions" but show in details
             pass

        # - CVAF Status
        if m.cvaf:
            # Format scores for display
            sos = m.cvaf.sos_score if m.cvaf.sos_score is not None else "N/A"
            insp = m.cvaf.inspection_score if m.cvaf.inspection_score is not None else "N/A"
            
            # Logic: If score is 0 or 1, it requires action (Maintenance)
            is_urgent_score = False
            try:
                if str(sos) in ['0', '1', '0.0', '1.0'] or str(insp) in ['0', '1', '0.0', '1.0']:
                    is_urgent_score = True
            except:
                pass

            virtual_interventions.append({
                "id": -3, "type": "CONTRAT CVA", 
                "priority": "MEDIUM" if is_urgent_score else "LOW", 
                "status": "PENDING",
                "description": f"Type: {m.cvaf.cva_type} | SOS: {sos} | Insp: {insp}", 
                "date_created": None
            })
            
            if is_urgent_score and status == 'operational':
                status = 'maintenance'

        # - Active campaigns (Suivi PS)
        if m.suivi_ps:
            for i, ps in enumerate(m.suivi_ps):
                virtual_interventions.append({
                    "id": -100 - i, "type": "CAMPAGNE PS", "priority": "MEDIUM", "status": "PENDING",
                    "description": f"{ps.ps_type}: {ps.description} (Ref: {ps.reference_number})", "date_created": ps.date
                })
                if status == 'operational': status = 'maintenance'
        
        # - Flash Update required (Remote Service)
        if m.remote_service and m.remote_service.flash_update == '1':
            virtual_interventions.append({
                "id": -4, "type": "REMOTE SERVICE", "priority": "MEDIUM", "status": "PENDING",
                "description": "Mise à jour Flash requise", "date_created": None
            })
            if status == 'operational': status = 'maintenance'
            
        # - Medium priority interventions
        has_medium_intervention = any(i.priority == 'MEDIUM' for i in m.interventions if i.status == 'PENDING')
        if has_medium_intervention and status == 'operational':
             status = 'maintenance'
        
        # Combined Interventions (DB + Virtual)
        all_interventions = [
            InterventionDTO(
                id=i.id,
                type=i.type,
                priority=i.priority,
                status=i.status,
                description=i.description,
                date_created=i.date_created
            ) for i in m.interventions if i.status == 'PENDING'
        ] + [InterventionDTO(**vi) for vi in virtual_interventions]

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
            pendingInterventions=all_interventions
        )
        response.append(machine_dto)
        
    return response
