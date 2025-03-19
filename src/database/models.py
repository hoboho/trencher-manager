from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Machine(Base):
    __tablename__ = 'machines'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    model = Column(String(100))
    ownership_percentage = Column(Float, nullable=False)  # Company's ownership percentage
    status = Column(String(20), default='available')  # available, in_use, maintenance
    created_at = Column(DateTime, default=datetime.utcnow)
    
    projects = relationship("MachineProject", back_populates="machine")
    costs = relationship("MachineCost", back_populates="machine")

class Operator(Base):
    __tablename__ = 'operators'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    contract_type = Column(String(20), nullable=False)  # daily, monthly, per_meter
    rate = Column(Float, nullable=False)
    status = Column(String(20), default='available')  # available, assigned, inactive
    created_at = Column(DateTime, default=datetime.utcnow)
    
    projects = relationship("OperatorProject", back_populates="operator")

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    contract_amount = Column(Float, nullable=False)
    received_amount = Column(Float, default=0.0)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    status = Column(String(20), default='active')  # active, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    
    machines = relationship("MachineProject", back_populates="project")
    operators = relationship("OperatorProject", back_populates="project")

class MachineProject(Base):
    __tablename__ = 'machine_projects'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    machine_id = Column(Integer, ForeignKey('machines.id'), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    
    project = relationship("Project", back_populates="machines")
    machine = relationship("Machine", back_populates="projects")
    
    __table_args__ = (
        UniqueConstraint('project_id', 'machine_id', name='unique_machine_project'),
    )

class OperatorProject(Base):
    __tablename__ = 'operator_projects'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    operator_id = Column(Integer, ForeignKey('operators.id'), nullable=False)
    machine_id = Column(Integer, ForeignKey('machines.id'), nullable=False)
    work_amount = Column(Float, nullable=False)  # days, months, or meters
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    
    project = relationship("Project", back_populates="operators")
    operator = relationship("Operator", back_populates="projects")
    
    __table_args__ = (
        UniqueConstraint('project_id', 'operator_id', 'machine_id', name='unique_operator_project'),
    )

class MachineCost(Base):
    __tablename__ = 'machine_costs'
    
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey('machines.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    cost_type = Column(String(50), nullable=False)  # fuel, repair, parts, etc.
    amount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    description = Column(String(200))
    
    machine = relationship("Machine", back_populates="costs")

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    recipient_type = Column(String(20), nullable=False)  # operator, shareholder
    recipient_id = Column(Integer, nullable=False)  # operator_id or machine_id
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, nullable=False)
    status = Column(String(20), default='pending')  # pending, paid, cancelled
    description = Column(String(200)) 