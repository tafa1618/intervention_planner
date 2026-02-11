
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_, and_
from models import Machine, Intervention, Client, CVAF, SuiviPS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_interventions(session: AsyncSession):
    """
    Analyzes Machine data (CVAF, Inspection Rate, Suivi_PS) and generates Interventions.
    """
    logger.info("Starting Intervention Generation...")
    
    # 1. Clear existing PENDING interventions to regenerate fresh ones (optional strategy)
    # OR we can just add new ones. For now, let's clear PENDING to avoid duplicates/stale data.
    logger.info("Clearing existing PENDING interventions...")
    await session.execute(delete(Intervention).where(Intervention.status == 'PENDING'))
    
    intervention_count = 0
    
    # Fetch all machines with their related data
    # We might need to optimize this with joinedload if the dataset is huge, 
    # but for 10k machines it might be okay or we can process in chunks.
    # For simplicity/speed in MVP, let's query specific conditions directly in SQL.

    # Better approach: Construct payloads and bulk insert.
    
    # 1. CVAF
    stmt_cvaf = select(Machine.id, CVAF.inspection_score, CVAF.sos_score).join(
        CVAF, Machine.serial_number == CVAF.serial_number
    ).where(
        or_(
            CVAF.inspection_score == '0/1',
            CVAF.sos_score == '0/1'
        )
    )
    result_cvaf = await session.execute(stmt_cvaf)
    
    interventions_to_add = []
    
    for row in result_cvaf.all():
        mach_id, insp_score, sos_score = row
        reasons = []
        if insp_score == '0/1':
            reasons.append("Inspection manquante")
        if sos_score == '0/1':
            reasons.append("Analyse SOS manquante")
            
        interventions_to_add.append(Intervention(
            machine_id=mach_id,
            type='CVAF',
            priority='HIGH',
            status='PENDING',
            description=f"Action requise : {', '.join(reasons)}"
        ))

    # 2. Inspection Rate (High Priority)
    # Trigger: psi_status == 'Non Inspecté'
    logger.info("Analyzing Inspection Rate rules...")
    stmt_insp = select(Machine.id).where(Machine.psi_status == 'Non Inspecté')
    result_insp = await session.execute(stmt_insp)
    
    for row in result_insp.all():
        interventions_to_add.append(Intervention(
            machine_id=row[0],
            type='INSPECTION',
            priority='HIGH',
            status='PENDING',
            description="Machine non inspectée (Programme Inspection Rate)"
        ))

    # 3. Suivi PS (Low Priority / Opportunistic)
    # Trigger: Entry in SuiviPS table
    logger.info("Analyzing Suivi PS rules...")
    from models import SuiviPS
    
    # Get machines that have at least one SuiviPS record
    # distinct machines
    # Get machines that have at least one SuiviPS record with Status 'Open'
    # distinct machines
    stmt_suivi = select(
        Machine.id, 
        SuiviPS.reference_number, 
        SuiviPS.ps_type, 
        SuiviPS.deadline, 
        SuiviPS.description
    ).join(
        SuiviPS, Machine.serial_number == SuiviPS.serial_number
    ).where(
        SuiviPS.status == 'Open'
    )
    result_suivi = await session.execute(stmt_suivi)
    
    for row in result_suivi.all():
        mach_id, ref_num, ps_type, deadline, desc = row
        
        # Format: "PS {Number} - {Type} (End: {Date}) - {Desc}"
        formatted_desc = f"PS {ref_num or '?'} - {ps_type or ''}"
        if deadline:
            formatted_desc += f" (Fin: {deadline})"
        if desc:
            formatted_desc += f" - {desc}"

        interventions_to_add.append(Intervention(
            machine_id=mach_id,
            type='SUIVI_PS',
            priority='LOW',
            status='PENDING',
            description=formatted_desc
        ))

    # Bulk Insert
    if interventions_to_add:
        logger.info(f"Generated {len(interventions_to_add)} interventions.")
        session.add_all(interventions_to_add)
        await session.commit()
    else:
        logger.info("No interventions generated.")
        
    return len(interventions_to_add)
