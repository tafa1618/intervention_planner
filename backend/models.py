
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, BigInteger
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from database import Base
import datetime

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True) # Internal ID
    external_id = Column(String, unique=True, index=True) # From Customer ID
    name = Column(String)
    account_number = Column(String, nullable=True) # From Compte if needed, or matched
    pssr = Column(String, nullable=True) # Technico-commercial assigned

    machines = relationship("Machine", back_populates="client")

class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String, unique=True, index=True) # 'N° série du matériel'
    make = Column(String, nullable=True) # 'Marque'
    model = Column(String, nullable=True) # 'Modèle'
    family = Column(String, nullable=True) # 'Famille de produits'
    
    # IoT Data
    service_meter = Column(Float, nullable=True) # 'Compteur d'entretien (Heures)'
    last_reported_time = Column(Float, nullable=True) # 'Dernière heure signalée ...' (Excel float date)
    status = Column(String, nullable=True) # 'Dernier statut matériel remonté'
    
    # Location
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location = Column(Geometry('POINT', srid=4326), nullable=True) # PostGIS column
    
    # Fields from PSSR_Client sheet
    last_visit = Column(String, nullable=True)
    next_visit = Column(String, nullable=True)
    psi_status = Column(String, nullable=True) # 'Dernier Rapport' / Inspection status

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    client = relationship("Client", back_populates="machines")

    cvaf = relationship("CVAF", back_populates="machine", uselist=False)
    # pssr relationship removed
    suivi_ps = relationship("SuiviPS", back_populates="machine", uselist=True)
    inspection_rate = relationship("InspectionRate", back_populates="machine", uselist=True)

    def __repr__(self):
        return f"<Machine(serial={self.serial_number}, model={self.model})>"

class CVAF(Base):
    __tablename__ = "cvaf"

    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String, ForeignKey("machines.serial_number"), unique=True, index=True)
    
    start_date = Column(String, nullable=True) # Parsing dates from excel can be tricky, keeping as string for now or DateTime if clean
    end_date = Column(String, nullable=True)
    cva_type = Column(String, nullable=True)
    country_code = Column(String, nullable=True)
    product_vertical = Column(String, nullable=True)
    dlr_cust_nm = Column(String, nullable=True)
    current_asset_age = Column(Integer, nullable=True)
    asset_age_group = Column(String, nullable=True)
    inspection_score = Column(String, nullable=True)
    connectivity_score = Column(String, nullable=True)
    sos_score = Column(String, nullable=True)

    machine = relationship("Machine", back_populates="cvaf")

# PSSR table removed

# PSSR table removed

class SuiviPS(Base):
    __tablename__ = "suivi_ps"

    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String, ForeignKey("machines.serial_number"), index=True)

    date = Column(String, nullable=True)
    client = Column(String, nullable=True)
    reference_number = Column(String, nullable=True) # Program Number
    ps_type = Column(String, nullable=True)
    status = Column(String, nullable=True)
    description = Column(String, nullable=True)
    action_required = Column(String, nullable=True)
    deadline = Column(String, nullable=True)

    machine = relationship("Machine", back_populates="suivi_ps")

class InspectionRate(Base):
    __tablename__ = "inspection_rate"

    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String, ForeignKey("machines.serial_number"), index=True)

    or_segment = Column(String, nullable=True) # N° OR (Segment)
    type_materiel = Column(String, nullable=True)
    atelier = Column(String, nullable=True)
    date_facture = Column(String, nullable=True)
    last_inspect = Column(String, nullable=True)
    nbr = Column(Integer, nullable=True)
    nom_client_or = Column(String, nullable=True)
    is_inspected = Column(String, nullable=True)
    technicien_reel = Column(String, nullable=True)
    equipe_reelle = Column(String, nullable=True)
    temps_reel = Column(Float, nullable=True)

    machine = relationship("Machine", back_populates="inspection_rate")

class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), index=True)
    
    # Types: 'CVAF', 'INSPECTION', 'SUIVI_PS', 'OPPORTUNITY'
    type = Column(String, index=True)
    
    # Priority: 'HIGH', 'MEDIUM', 'LOW'
    priority = Column(String, index=True)
    
    # Status: 'PENDING', 'PLANNED', 'COMPLETED', 'CANCELLED'
    status = Column(String, default='PENDING', index=True)
    
    description = Column(String, nullable=True)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    
    machine = relationship("Machine", back_populates="interventions")

# Update Machine relationship
Machine.interventions = relationship("Intervention", back_populates="machine", cascade="all, delete-orphan")
Machine.remote_service = relationship("RemoteService", back_populates="machine", uselist=False, cascade="all, delete-orphan")

class RemoteService(Base):
    __tablename__ = "remote_service"

    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String, ForeignKey("machines.serial_number"), unique=True, index=True)
    flash_update = Column(String, nullable=True) # '0/1' status

    machine = relationship("Machine", back_populates="remote_service")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)
    password_hash = Column(String)
    role = Column(String, default="user") # 'admin' or 'user' (read-only)
    is_active = Column(Integer, default=1) # 1=Active, 0=Inactive
