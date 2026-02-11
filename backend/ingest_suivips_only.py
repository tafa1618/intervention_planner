
import asyncio
import pandas as pd
import os
import math
from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from database import AsyncSessionLocal
from models import Machine, SuiviPS

async def ingest_suivips_only():
    file_path = "data/Programmes.xlsx"
    async with AsyncSessionLocal() as session:
        print("Starting SuiviPS Ingestion...")
        
        # Get existing serials
        print("Fetching existing machines...")
        result = await session.execute(select(Machine.serial_number))
        existing_serials = set(result.scalars().all())
        print(f"Found {len(existing_serials)} existing machines.")

        # Read specific sheet
        try:
            suivi_df = pd.read_excel(file_path, sheet_name='Suivi_PS')
            print(f"Read {len(suivi_df)} rows from Suivi_PS.")
        except Exception as e:
            print(f"Error reading excel: {e}")
            return

        suivi_inserts = []
        serials_in_sheet = set()
        
        for _, row in suivi_df.iterrows():
            serial = row.get('Serial Number')
            if pd.isna(serial):
                continue
            serial = str(serial).strip()
            
            if serial not in existing_serials:
                continue

            serials_in_sheet.add(serial)

            suivi_data = {
                "serial_number": serial,
                "date": str(row.get('Letter Date')) if not pd.isna(row.get('Letter Date')) else None,
                "client": row.get('Client'),
                "reference_number": str(row.get('Program Number')) if not pd.isna(row.get('Program Number')) else None,
                "ps_type": row.get('Service Letter Type'),
                "status": row.get('Status'),
                "description": row.get('Description'),
                "action_required": None,
                "deadline": str(row.get('Term Date')) if not pd.isna(row.get('Term Date')) else None
            }
             # Clean NaNs
            for k, v in suivi_data.items():
                if isinstance(v, float) and math.isnan(v):
                    suivi_data[k] = None
            
            suivi_inserts.append(suivi_data)

        if suivi_inserts:
            # Delete existing for these serials
            print(f"Deleting existing SuiviPS for {len(serials_in_sheet)} machines...")
            batch_size = 1000
            serials_list = list(serials_in_sheet)
            for i in range(0, len(serials_list), batch_size):
                batch = serials_list[i:i + batch_size]
                await session.execute(delete(SuiviPS).where(SuiviPS.serial_number.in_(batch)))
            
            # Insert new
            print(f"Inserting {len(suivi_inserts)} SuiviPS records...")
            # Chunk inserts
            for i in range(0, len(suivi_inserts), batch_size):
                batch = suivi_inserts[i:i + batch_size]
                await session.execute(insert(SuiviPS).values(batch))
            
            await session.commit()
            print("SuiviPS Ingestion Done.")
        else:
            print("No valid SuiviPS records found to insert.")

if __name__ == "__main__":
    asyncio.run(ingest_suivips_only())
