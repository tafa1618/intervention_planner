
import pandas as pd
import os
import math
from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from models import Machine, Client

async def ingest_programmes_data(file_path: str, session: AsyncSession) -> dict:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    print("Reading Excel file...")
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        raise ValueError(f"Error reading excel: {e}")

    row_count = len(df)
    print(f"Found {row_count} rows.")

    # Create Clients first (or update if exists)
    clients_dict = {} # external_id -> Client object

    # Use unique external_ids
    client_rows = df[['ID client', 'Nom de compte client', 'Numéro de compte client']].drop_duplicates(subset=['ID client'])
    
    client_inserts = []
    for _, row in client_rows.iterrows():
        ext_id = row['ID client']
        if pd.isna(ext_id):
            continue
        try:
            ext_id = int(ext_id)
        except:
             continue # skip invalid IDs

        name = row['Nom de compte client']
        acc_num = row['Numéro de compte client']
        
        client_inserts.append({
            "external_id": str(ext_id),
            "name": str(name) if not pd.isna(name) else "Unknown",
            "account_number": str(acc_num) if not pd.isna(acc_num) else None
        })
    
    clients_processed = 0
    if client_inserts:
        print(f"Inserting {len(client_inserts)} clients...")
        stmt = insert(Client).values(client_inserts)
        stmt = stmt.on_conflict_do_update(
            index_elements=['external_id'],
            set_=dict(name=stmt.excluded.name, account_number=stmt.excluded.account_number)
        )
        await session.execute(stmt)
        clients_processed = len(client_inserts)
    
    # Fetch all clients back to get their internal IDs
    result = await session.execute(select(Client))
    db_clients = result.scalars().all()
    client_map = {c.external_id: c.id for c in db_clients}

    # Prepare Machines
    machine_inserts = []
    print("Processing machines...")
    for _, row in df.iterrows():
        serial = row.get('N° série du matériel')
        if pd.isna(serial):
            continue
        serial = str(serial).strip()
        
        ext_client_id = row.get('ID client')
        client_db_id = None
        if not pd.isna(ext_client_id):
            try:
                client_db_id = client_map.get(str(int(ext_client_id)))
            except:
                pass

        lat = row.get('LATITUDE')
        lon = row.get('LONGITUDE')
        
        # location_wkt = None
        # valid_coords = False
        # if not pd.isna(lat) and not pd.isna(lon):
        #     try:
        #         lat = float(lat)
        #         lon = float(lon)
        #         if -90 <= lat <= 90 and -180 <= lon <= 180:
        #             location_wkt = f"SRID=4326;POINT({lon} {lat})"
        #             valid_coords = True
        #     except:
        #         pass
        valid_coords = False
        if not pd.isna(lat) and not pd.isna(lon):
            try:
                lat = float(lat)
                lon = float(lon)
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    valid_coords = True
            except:
                pass

        def clean_str(val):
            if pd.isna(val): return None
            return str(val).strip()

        machine_data = {
            "serial_number": serial,
            "make": clean_str(row.get('Marque')),
            "model": clean_str(row.get('Modèle')),
            "family": clean_str(row.get('Famille de produits')),
            "service_meter": row.get("Compteur d'entretien (Heures)"),
            "last_reported_time": row.get("Heure du dernier signalement du dernier compteur d'entretien connu"), 
            "status": clean_str(row.get("Dernier statut matériel remonté")),
            "latitude": lat if valid_coords else None,
            "longitude": lon if valid_coords else None,
            #"location": location_wkt, 
            "client_id": client_db_id
        }
        
        # Handle potential NaN values for strings
        for k, v in machine_data.items():
            if isinstance(v, float) and math.isnan(v):
                machine_data[k] = None
        
        machine_inserts.append(machine_data)

    machines_processed = 0
    if machine_inserts:
             print(f"Inserting {len(machine_inserts)} machines...")
             chunk_size = 1000
             for i in range(0, len(machine_inserts), chunk_size):
                 chunk = machine_inserts[i:i+chunk_size]
                 stmt = insert(Machine).values(chunk)
                 stmt = stmt.on_conflict_do_update(
                    index_elements=['serial_number'],
                    set_=dict(
                        service_meter=stmt.excluded.service_meter,
                        status=stmt.excluded.status,
                        latitude=stmt.excluded.latitude,
                        longitude=stmt.excluded.longitude,
                        #location=stmt.excluded.location,
                        client_id=stmt.excluded.client_id
                    )
                 )
                 await session.execute(stmt)
                 print(f"Processed chunk {i} to {i+len(chunk)}")
             machines_processed = len(machine_inserts)

    # Process CVAF sheet if it exists
    cvaf_processed = 0
    try:
        cvaf_df = pd.read_excel(file_path, sheet_name='CVAF')
        print(f"Found CVAF sheet with {len(cvaf_df)} rows.")
        
        from models import CVAF

        cvaf_inserts = []
        for _, row in cvaf_df.iterrows():
            serial = row.get('Serial Number')
            if pd.isna(serial):
                continue
            serial = str(serial).strip()
            
            # Only insert if machine exists? Or should we create machine?
            # For now assuming machine should exist from main sheet, but we can't enforce it easily since we just inserted them.
            # We can rely on foreign key constraint to fail or we can do a quick check.
            # Upsert on serial_number in CVAF table.
            
            cvaf_data = {
                "serial_number": serial,
                "start_date": str(row.get('Start Date')) if not pd.isna(row.get('Start Date')) else None,
                "end_date": str(row.get('End Date')) if not pd.isna(row.get('End Date')) else None,
                "cva_type": row.get('Cva Type'),
                "country_code": row.get('Country Code'),
                "product_vertical": row.get('Product Vertical'),
                "dlr_cust_nm": row.get('Dlr Cust Nm'),
                "current_asset_age": row.get('Current Asset Age') if not pd.isna(row.get('Current Asset Age')) else None,
                "asset_age_group": row.get('Asset Age Group'),
                "inspection_score": str(row.get('Inspection Score')) if not pd.isna(row.get('Inspection Score')) else None,
                "connectivity_score": str(row.get('Connectivity Score')) if not pd.isna(row.get('Connectivity Score')) else None,
                "sos_score": str(row.get('Sos Score')) if not pd.isna(row.get('Sos Score')) else None
            }
            
            # Clean NaNs
            for k, v in cvaf_data.items():
                if isinstance(v, float) and math.isnan(v):
                    cvaf_data[k] = None
            
            cvaf_inserts.append(cvaf_data)
        
        if cvaf_inserts:
             # Fetch existing serial numbers to avoid FK violation
             result = await session.execute(select(Machine.serial_number))
             existing_serials = set(result.scalars().all())
             
             valid_cvaf_inserts = [
                 c for c in cvaf_inserts 
                 if c['serial_number'] in existing_serials
             ]
             
             print(f"Filtered CVAF records from {len(cvaf_inserts)} to {len(valid_cvaf_inserts)} based on existing machines.")
             
             if valid_cvaf_inserts:
                 print(f"Inserting {len(valid_cvaf_inserts)} CVAF records...")
                 chunk_size = 1000
                 for i in range(0, len(valid_cvaf_inserts), chunk_size):
                     chunk = valid_cvaf_inserts[i:i+chunk_size]
                     stmt = insert(CVAF).values(chunk)
                     stmt = stmt.on_conflict_do_update(
                        index_elements=['serial_number'],
                        set_=dict(
                            start_date=stmt.excluded.start_date,
                            end_date=stmt.excluded.end_date,
                            cva_type=stmt.excluded.cva_type,
                            country_code=stmt.excluded.country_code,
                            product_vertical=stmt.excluded.product_vertical,
                            dlr_cust_nm=stmt.excluded.dlr_cust_nm,
                            current_asset_age=stmt.excluded.current_asset_age,
                            asset_age_group=stmt.excluded.asset_age_group,
                            inspection_score=stmt.excluded.inspection_score,
                            connectivity_score=stmt.excluded.connectivity_score,
                            sos_score=stmt.excluded.sos_score
                        )
                     )
                     await session.execute(stmt)
                 cvaf_processed = len(valid_cvaf_inserts)

    except ValueError:
        print("CVAF sheet not found.")
    except Exception as e:
        print(f"Error processing CVAF: {e}")
    
    # Process PSSR_Client (Metadata for Client Only)
    pssr_processed = 0
    try:
        from sqlalchemy import update
        
        pssr_df = pd.read_excel(file_path, sheet_name='PSSR_Client')
        print(f"Found PSSR_Client sheet with {len(pssr_df)} rows.")
        
        # Map Client Name -> PSSR Name
        client_to_pssr = {}
        for _, row in pssr_df.iterrows():
            client_name = row.get('Nom du compte')
            pssr_name = row.get('PSSR/ ISR')
            
            if not pd.isna(client_name) and not pd.isna(pssr_name):
                client_to_pssr[str(client_name).strip()] = str(pssr_name).strip()
        
        if client_to_pssr:
            print(f"Updating {len(client_to_pssr)} Clients with PSSR assignment...")
            
            # Fetch existing clients to get IDs
            result = await session.execute(select(Client.name, Client.id))
            name_to_id = {row[0]: row[1] for row in result.all()}
            
            client_updates = []
            for name, pssr in client_to_pssr.items():
                if name in name_to_id:
                     client_updates.append({"id": name_to_id[name], "pssr": pssr})
            
            if client_updates:
                await session.execute(
                    update(Client),
                    client_updates
                )
                pssr_processed = len(client_updates)
                print(f"Updated {pssr_processed} clients.")
             
    except ValueError:
        print("PSSR_Client sheet not found.")
    except Exception as e:
        print(f"Error processing PSSR: {e}")

    # Process Suivi_PS
    suivi_ps_processed = 0
    try:
        from models import SuiviPS
        
        suivi_df = pd.read_excel(file_path, sheet_name='Suivi_PS')
        print(f"Found Suivi_PS sheet with {len(suivi_df)} rows.")
        
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
                "action_required": None, # Not in file
                "deadline": str(row.get('Term Date')) if not pd.isna(row.get('Term Date')) else None
            }
             # Clean NaNs
            for k, v in suivi_data.items():
                if isinstance(v, float) and math.isnan(v):
                    suivi_data[k] = None
            suivi_inserts.append(suivi_data)

        if suivi_inserts:
             print(f"Deleting existing SuiviPS for {len(serials_in_sheet)} machines...")
             await session.execute(delete(SuiviPS).where(SuiviPS.serial_number.in_(serials_in_sheet)))
             
             print(f"Inserting {len(suivi_inserts)} SuiviPS records...")
             chunk_size = 1000
             for i in range(0, len(suivi_inserts), chunk_size):
                 chunk = suivi_inserts[i:i+chunk_size]
                 await session.execute(insert(SuiviPS).values(chunk))
             suivi_ps_processed = len(suivi_inserts)
             
    except ValueError:
            print("Suivi_PS sheet not found.")
    except Exception as e:
            print(f"Error processing Suivi_PS: {e}")

    # Process Inspection Rate
    inspection_processed = 0
    try:
        from models import InspectionRate
        from sqlalchemy import update
        
        insp_df = pd.read_excel(file_path, sheet_name='Inspection Rate')
        print(f"Found Inspection Rate sheet with {len(insp_df)} rows.")
        
        # Refresh machine mapping to handle newly inserted machines
        result = await session.execute(select(Machine.serial_number, Machine.id))
        serial_to_id = {row[0]: row[1] for row in result.all()}
        existing_serials = set(serial_to_id.keys()) 

        insp_inserts = []
        machine_updates = []
        serials_in_sheet = set()

        for _, row in insp_df.iterrows():
            serial = row.get('S/N') # Column is S/N
            if pd.isna(serial):
                continue
            serial = str(serial).strip()
            
            if serial not in existing_serials:
                continue

            serials_in_sheet.add(serial)
            
            # Extract data
            date_facture = str(row.get('Date Facture (Lignes)')) if not pd.isna(row.get('Date Facture (Lignes)')) else None
            last_inspect = str(row.get('Last Inspect')) if not pd.isna(row.get('Last Inspect')) else None
            is_inspected = row.get('Is Inspected')
            
            # Prepare InspectionRate insertion payload
            insp_data = {
                "serial_number": serial,
                "or_segment": str(row.get('N° OR (Segment)')),
                "type_materiel": str(row.get('Type matériel')),
                "atelier": row.get('Atelier'),
                "date_facture": date_facture,
                "last_inspect": last_inspect,
                "nbr": int(row.get('Nbr')) if not pd.isna(row.get('Nbr')) else None,
                "nom_client_or": row.get('Nom Client OR (or)'),
                "is_inspected": is_inspected,
                "technicien_reel": row.get('Technicien Réel'),
                "equipe_reelle": row.get('Equipe Réelle'),
                "temps_reel": float(row.get('Temps Réel (h)')) if not pd.isna(row.get('Temps Réel (h)')) else None
            }
             # Clean NaNs
            for k, v in insp_data.items():
                if isinstance(v, float) and math.isnan(v):
                    insp_data[k] = None
            insp_inserts.append(insp_data)
            
            # Prepare Machine update payload
            machine_updates.append({
                "id": serial_to_id[serial],
                "last_visit": last_inspect,
                "psi_status": str(is_inspected) if not pd.isna(is_inspected) else None
            })

        if insp_inserts:
             print(f"Deleting existing InspectionRate for {len(serials_in_sheet)} machines...")
             await session.execute(delete(InspectionRate).where(InspectionRate.serial_number.in_(serials_in_sheet)))
             
             print(f"Inserting {len(insp_inserts)} InspectionRate records...")
             chunk_size = 1000
             for i in range(0, len(insp_inserts), chunk_size):
                 chunk = insp_inserts[i:i+chunk_size]
                 await session.execute(insert(InspectionRate).values(chunk))
             inspection_processed = len(insp_inserts)

        if machine_updates:
            print(f"Updating {len(machine_updates)} machines with Last Inspect info...")
            await session.execute(update(Machine), machine_updates)

    except ValueError:
            print("Inspection Rate sheet not found.")
    except Exception as e:
            print(f"Error processing Inspection Rate: {e}")

    # Process Remote Service
    remote_service_processed = 0
    # Normalize sheet names for case-insensitive lookup
    xl = pd.ExcelFile(file_path)
    sheet_names = xl.sheet_names
    
    remote_df = None
    # Try finding sheet by common names
    remote_sheet_target = next((s for s in sheet_names if s.lower() in ['remote service', 'remote_service', 'suivi remote service']), None)
    
    if remote_sheet_target:
        print(f"Detected Remote Service sheet: {remote_sheet_target}")
        remote_df = pd.read_excel(file_path, sheet_name=remote_sheet_target)
    else:
        # Plan B: Try to detect by headers in OTHER sheets if not found by name
        for sheet in sheet_names:
            try:
                temp_df = pd.read_excel(file_path, sheet_name=sheet, nrows=5)
                if any(col in temp_df.columns for col in ['Flash Update', 'Serial Number', 'Product Model', 'S/N']):
                    print(f"Detected Remote Service data in sheet: {sheet}")
                    remote_df = pd.read_excel(file_path, sheet_name=sheet)
                    break
            except:
                continue

    if remote_df is not None:
         # 1. Flush any previous changes to ensure DB is up to date for lookups
         await session.flush()
         
         # 2. Refresh existing serials
         result = await session.execute(select(Machine.serial_number))
         existing_serials = set(result.scalars().all())

         new_machine_stubs = []
         remote_inserts = []
         serials_processed_in_sheet = set()
         
         # Map potential S/N column names
         sn_col = next((c for c in remote_df.columns if str(c).lower() in ['s/n', 'serial number', 'n° série']), None)
         flash_col = next((c for c in remote_df.columns if str(c).lower() in ['flash update', 'flash_update']), None)

         if sn_col:
             for _, row in remote_df.iterrows():
                serial = row.get(sn_col)
                if pd.isna(serial): continue
                serial = str(serial).strip()
                
                if serial in serials_processed_in_sheet: continue
                serials_processed_in_sheet.add(serial)

                # If machine doesn't exist, prepare a stub
                if serial not in existing_serials:
                    val_model = row.get('Product Model')
                    new_machine_stubs.append({
                        "serial_number": serial,
                        "model": str(val_model) if not pd.isna(val_model) else None,
                    })
                    existing_serials.add(serial)

                # Prepare Remote Service record
                remote_inserts.append({
                    "serial_number": serial,
                    "flash_update": str(row.get(flash_col)) if flash_col and not pd.isna(row.get(flash_col)) else None
                })
            
             # 3. Bulk Insert Machine Stubs (on conflict do nothing)
             if new_machine_stubs:
                 print(f"Adding {len(new_machine_stubs)} machine stubs from Remote Service...")
                 stmt_machines = insert(Machine).values(new_machine_stubs)
                 stmt_machines = stmt_machines.on_conflict_do_nothing(index_elements=['serial_number'])
                 await session.execute(stmt_machines)
                 await session.flush() # Ensure machines exist before RemoteService refers to them

             # 4. Bulk Insert/Update Remote Service Records
             if remote_inserts:
                 print(f"Upserting RemoteService for {len(remote_inserts)} machines...")
                 stmt = insert(RemoteService).values(remote_inserts)
                 from models import RemoteService as RemoteServiceModel
                 stmt = stmt.on_conflict_do_update(
                     index_elements=['serial_number'],
                     set_=dict(
                         flash_update=stmt.excluded.flash_update
                     )
                 )
                 await session.execute(stmt)
                 remote_service_processed = len(remote_inserts)
    else:
        print("No Remote Service sheet or data detected.")


    return {
        "clients": clients_processed, 
        "machines": machines_processed, 
        "cvaf": cvaf_processed,
        "pssr": pssr_processed,
        "suivi_ps": suivi_ps_processed,
        "inspection_rate": inspection_processed,
        "remote_service": remote_service_processed
    }
