from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func, text
from database import get_db
from models import User, Machine, Client, RemoteService, CVAF, SuiviPS, InspectionRate
from routers.auth import get_current_admin_user, get_password_hash
from pydantic import BaseModel
from typing import List

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin_user)]
)

# --- Schemas ---
class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str # Temporary password
    role: str = "user"

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: int

    class Config:
        from_attributes = True

class StatsResponse(BaseModel):
    total_machines: int
    connected_machines: int # With VisionLink or RemoteService
    machines_with_remote: int
    machines_with_vl: int
    clients_count: int

# --- Endpoints ---

@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    stmt = select(User).where(User.email == user.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email, 
        full_name=user.full_name, 
        password_hash=hashed_password, 
        role=user.role
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.get("/users", response_model=List[UserResponse])
async def list_users(db: Session = Depends(get_db)):
    stmt = select(User)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/stats", response_model=StatsResponse)
async def get_system_stats(db: Session = Depends(get_db)):
    # Total Machines
    total_machines = await db.scalar(select(func.count(Machine.id)))
    
    # Clients
    clients_count = await db.scalar(select(func.count(Client.id)))

    # Machines with Remote Service (flash_update is not null)
    remote_count = await db.scalar(select(func.count(RemoteService.id)))

    # Machines with VisionLink (roughly implied by having coordinates or specific VL columns if we had them distinct)
    # For now, let's use location is not null as a proxy for "Connected/Located"
    connected_count = await db.scalar(select(func.count(Machine.id)).where(Machine.location != None))
    
    # Or strict VL check if we have a VL table? We don't have a dedicated VL table, it's mixed in Machine.
    # Let's count those with valid coordinates as "Connected"
    
    return {
        "total_machines": total_machines or 0,
        "connected_machines": connected_count or 0,
        "machines_with_remote": remote_count or 0,
        "machines_with_vl": connected_count or 0, # Placeholder
        "clients_count": clients_count or 0
    }
