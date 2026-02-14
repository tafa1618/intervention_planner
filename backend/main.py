
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.ingestion import ingest_programmes_data
from routers import interventions, machines
import os

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Ensure data directory exists on startup
    os.makedirs("data", exist_ok=True)

app.include_router(interventions.router)
app.include_router(machines.router)
from routers import auth, admin
app.include_router(auth.router)
app.include_router(admin.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Intervention Planner Backend Running"}

@app.post("/upload-programmes")
async def upload_machines_excel(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    try:
        temp_file = f"/tmp/uploaded_{file.filename}"
        with open(temp_file, "wb") as f:
            f.write(await file.read())
        
        # Process the file
        stats = await ingest_programmes_data(temp_file, db)
        
        # Clean up
        import os
        os.remove(temp_file)
        
        await db.commit()
        return {"message": "File processed successfully", "stats": stats}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}
