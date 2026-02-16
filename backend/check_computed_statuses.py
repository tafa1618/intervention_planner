
import asyncio
import os
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database import AsyncSessionLocal
from models import Machine, Client, RemoteService, CVAF, SuiviPS, InspectionRate

async def check_statuses():
    async with AsyncSessionLocal() as session:
        query = select(Machine).options(
            selectinload(Machine.client),
            selectinload(Machine.interventions),
            selectinload(Machine.suivi_ps),
            selectinload(Machine.remote_service),
            selectinload(Machine.cvaf),
            selectinload(Machine.inspection_rate)
        )
        
        result = await session.execute(query)
        machines = result.scalars().all()
        
        print(f"Checking {len(machines)} machines...")
        counts = {'operational': 0, 'maintenance': 0, 'critical': 0}
        
        for m in machines:
            status = 'operational'
            reasons = []
            
            # Critical Logic
            has_urgent_intervention = any(i.priority == 'HIGH' for i in m.interventions if i.status == 'PENDING')
            excel_status_raw = str(m.status).lower() if m.status else ""
            is_urgent_excel = any(term in excel_status_raw for term in ["défaut", "urgent", "critique", "critical", "breakdown"])
            
            is_urgent_score = False
            if m.cvaf:
                sos = m.cvaf.sos_score
                insp = m.cvaf.inspection_score
                try:
                    if str(sos) in ['0', '1', '0.0', '1.0'] or str(insp) in ['0', '1', '0.0', '1.0']:
                        is_urgent_score = True
                except: pass

            if is_urgent_excel: 
                status = 'critical'
                reasons.append(f"Excel status: {m.status}")
            elif has_urgent_intervention: 
                status = 'critical'
                reasons.append("High priority intervention")
            elif is_urgent_score:
                status = 'critical'
                reasons.append(f"CVA Score (SOS:{m.cvaf.sos_score}, Insp:{m.cvaf.inspection_score})")
            
            # Maintenance Logic
            if status == 'operational':
                if m.psi_status == 'Non Inspecté':
                    status = 'maintenance'
                    reasons.append("PSI: Non Inspecté")
                elif m.remote_service and m.remote_service.flash_update == '1':
                    status = 'maintenance'
                    reasons.append("Remote Service: Flash Update required")
                elif any(i.priority == 'MEDIUM' for i in m.interventions if i.status == 'PENDING'):
                    status = 'maintenance'
                    reasons.append("Medium priority intervention")

            counts[status] += 1
            if status != 'operational':
                print(f"Machine {m.serial_number}: {status.upper()} - {', '.join(reasons)}")

        print(f"\nFinal Counts: {counts}")

if __name__ == "__main__":
    asyncio.run(check_statuses())
