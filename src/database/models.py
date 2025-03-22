from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, UniqueConstraint, Date, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

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
    purchase_date = Column(Date)
    purchase_price = Column(Float)  # Rial
    fuel_consumption_rate = Column(Float)  # Liters per hour
    fuel_cost_per_liter = Column(Float)  # Rial per liter
    maintenance_cost_per_hour = Column(Float)  # Rial per hour
    trenching_depth = Column(Float)  # Meters
    trenching_width = Column(Float)  # Meters
    maximum_speed = Column(Float)  # Meters per hour
    weight = Column(Float)  # Kilograms
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    projects = relationship("MachineProject", back_populates="machine")
    costs = relationship("MachineCost", back_populates="machine")
    transactions = relationship("Transaction", back_populates="machine")

    def __repr__(self):
        return f"<Machine(name='{self.name}', model='{self.model}')>"

class Operator(Base):
    __tablename__ = 'operators'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    hourly_rate = Column(Float, nullable=False)  # Rial per hour
    overtime_rate = Column(Float, nullable=False)  # Rial per hour (usually 1.5x hourly rate)
    overtime_threshold = Column(Float, default=8.0)  # Hours per day before overtime
    contact = Column(String)  # Added contact info
    skills = Column(String)   # Added skills
    notes = Column(String)    # Added notes
    specialization = Column(String)  # Added specialization
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    projects = relationship("OperatorProject", back_populates="operator")
    transactions = relationship("Transaction", back_populates="operator")

    def __repr__(self):
        return f"<Operator(name='{self.name}')>"

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    client_name = Column(String)
    client_contact = Column(String)
    location = Column(String)
    contract_amount = Column(Float, nullable=False)  # Rial
    received_amount = Column(Float, default=0.0)  # Rial
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    total_length = Column(Float)  # Meters
    average_depth = Column(Float)  # Meters
    average_width = Column(Float)  # Meters
    status = Column(String(20), nullable=False, default='active')
    description = Column(String)
    notes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    machines = relationship("MachineProject", back_populates="project")
    operators = relationship("OperatorProject", back_populates="project")
    expenses = relationship("ProjectExpense", back_populates="project")
    transactions = relationship("Transaction", back_populates="project")
    
    # Add relationships for payments and machine costs
    payments_received = relationship("Transaction", 
                                   primaryjoin="and_(Project.id==Transaction.project_id, "
                                             "Transaction._type=='income')",
                                   viewonly=True)
    
    machine_costs = relationship("MachineCost", back_populates="project")
    payments = relationship("Payment", back_populates="project")
    
    def calculate_total_costs(self):
        """Calculate total costs for the project in Rial."""
        total = 0.0
        
        # Add machine costs
        for machine in self.machines:
            total += machine.calculate_total_cost()
        
        # Add operator costs
        for operator in self.operators:
            total += operator.calculate_total_cost()
        
        # Add other expenses
        for expense in self.expenses:
            total += expense.amount
        
        return total
    
    def calculate_profit(self):
        """Calculate profit/loss for the project in Rial."""
        return self.received_amount - self.calculate_total_costs()
    
    def calculate_remaining_balance(self):
        """Calculate remaining balance to be received in Rial."""
        return self.contract_amount - self.received_amount
    
    def calculate_progress(self):
        """Calculate project progress in meters."""
        if not self.total_length:
            return 0.0
        completed_length = sum(mp.completed_length for mp in self.machines)
        return (completed_length / self.total_length * 100) if self.total_length > 0 else 0
    
    def get_financial_summary(self):
        """Get a financial summary of the project."""
        return {
            'total_contract': self.contract_amount,
            'total_received': self.received_amount,
            'total_costs': self.calculate_total_costs(),
            'total_profit': self.calculate_profit(),
            'remaining_balance': self.calculate_remaining_balance(),
            'progress_percentage': self.calculate_progress()
        }
    
    def get_machine_summary(self):
        """Get a summary of machine usage in the project."""
        return [{
            'machine_name': mp.machine.name,
            'hours_used': mp.hours_used,
            'completed_length': mp.completed_length,
            'efficiency': mp.completed_length / mp.hours_used if mp.hours_used > 0 else 0,
            'total_cost': mp.calculate_total_cost()
        } for mp in self.machines]
    
    def get_operator_summary(self):
        """Get a summary of operator performance in the project."""
        return [{
            'operator_name': op.operator.name,
            'hours_worked': op.hours_worked,
            'completed_length': op.completed_length,
            'efficiency': op.completed_length / op.hours_worked if op.hours_worked > 0 else 0,
            'total_cost': op.calculate_total_cost()
        } for op in self.operators]
    
    def __repr__(self):
        return f"<Project(name='{self.name}', status='{self.status}')>"

class MachineProject(Base):
    __tablename__ = 'machine_projects'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    machine_id = Column(Integer, ForeignKey('machines.id'))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    hours_used = Column(Float, default=0.0)  # Hours
    completed_length = Column(Float, default=0.0)  # Meters
    average_depth = Column(Float)  # Meters
    average_width = Column(Float)  # Meters
    average_speed = Column(Float)  # Meters per hour
    
    project = relationship("Project", back_populates="machines")
    machine = relationship("Machine", back_populates="projects")
    
    __table_args__ = (
        UniqueConstraint('project_id', 'machine_id', name='unique_machine_project'),
    )

    def calculate_total_cost(self):
        """Calculate total cost for this machine in this project in Rial."""
        if not self.machine:
            return 0.0
            
        # Calculate fuel cost
        fuel_cost = (self.hours_used * self.machine.fuel_consumption_rate * 
                    self.machine.fuel_cost_per_liter)
        
        # Calculate maintenance cost
        maintenance_cost = self.hours_used * self.machine.maintenance_cost_per_hour
        
        return fuel_cost + maintenance_cost

class OperatorProject(Base):
    __tablename__ = 'operator_projects'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    operator_id = Column(Integer, ForeignKey('operators.id'))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    hours_worked = Column(Float, default=0.0)  # Hours
    completed_length = Column(Float, default=0.0)  # Meters
    
    project = relationship("Project", back_populates="operators")
    operator = relationship("Operator", back_populates="projects")
    
    __table_args__ = (
        UniqueConstraint('project_id', 'operator_id', name='unique_operator_project'),
    )

    def calculate_total_cost(self):
        """Calculate total cost for this operator in this project in Rial."""
        if not self.operator:
            return 0.0
            
        # Calculate regular hours and overtime hours
        regular_hours = min(self.hours_worked, self.operator.overtime_threshold)
        overtime_hours = max(0, self.hours_worked - self.operator.overtime_threshold)
        
        # Calculate costs
        regular_cost = regular_hours * self.operator.hourly_rate
        overtime_cost = overtime_hours * self.operator.overtime_rate
        
        return regular_cost + overtime_cost

class MachineCost(Base):
    __tablename__ = 'machine_costs'
    
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey('machines.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    cost_type = Column(String(50), nullable=False)  # fuel, repair, parts, etc.
    amount = Column(Float, nullable=False)  # Rial
    date = Column(DateTime, nullable=False)
    description = Column(String(200))
    
    machine = relationship("Machine", back_populates="costs")
    project = relationship("Project", back_populates="machine_costs")
    
    def to_dict(self):
        """Convert the machine cost to a dictionary for reporting."""
        return {
            'cost_type': self.cost_type,
            'amount': self.amount,
            'date': self.date.isoformat(),
            'description': self.description,
            'machine_name': self.machine.name if self.machine else None,
            'project_name': self.project.name if self.project else None
        }

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    recipient_type = Column(String(20), nullable=False)  # operator, shareholder
    recipient_id = Column(Integer, nullable=False)  # operator_id or machine_id
    amount = Column(Float, nullable=False)  # Rial
    payment_date = Column(DateTime, nullable=False)
    status = Column(String(20), default='pending')  # pending, paid, cancelled
    description = Column(String(200))
    
    project = relationship("Project", back_populates="payments")
    
    def to_dict(self):
        """Convert the payment to a dictionary for reporting."""
        return {
            'amount': self.amount,
            'payment_date': self.payment_date.isoformat(),
            'status': self.status,
            'recipient_type': self.recipient_type,
            'description': self.description,
            'project_name': self.project.name if self.project else None
        }

class ProjectExpense(Base):
    __tablename__ = 'project_expenses'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    date = Column(Date, nullable=False)
    description = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)  # Rial
    category = Column(String(50))
    
    project = relationship("Project", back_populates="expenses")
    
    def __repr__(self):
        return f"<ProjectExpense(description='{self.description}', amount={self.amount})>"

class TransactionType(enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"

class TransactionCategory(enum.Enum):
    PROJECT_PAYMENT = "project_payment"
    SALARY = "salary"
    MAINTENANCE = "maintenance"
    FUEL = "fuel"
    OTHER = "other"

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    _type = Column('type', String(20), nullable=False)  # Store as string
    amount = Column(Float, nullable=False)
    _category = Column('category', String(50), nullable=False)  # Store as string
    description = Column(String(200))
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    project_id = Column(Integer, ForeignKey('projects.id'))
    operator_id = Column(Integer, ForeignKey('operators.id'))
    machine_id = Column(Integer, ForeignKey('machines.id'))
    
    project = relationship("Project", back_populates="transactions")
    operator = relationship("Operator", back_populates="transactions")
    machine = relationship("Machine", back_populates="transactions")
    
    @property
    def type(self):
        return TransactionType(self._type)
    
    @type.setter
    def type(self, value):
        if isinstance(value, TransactionType):
            self._type = value.value
        else:
            self._type = value
    
    @property
    def category(self):
        return TransactionCategory(self._category)
    
    @category.setter
    def category(self, value):
        if isinstance(value, TransactionCategory):
            self._category = value.value
        else:
            self._category = value
    
    def __repr__(self):
        return f"<Transaction(type='{self._type}', amount={self.amount}, category='{self._category}')>"

class ReportCache(Base):
    __tablename__ = 'report_cache'
    
    id = Column(Integer, primary_key=True)
    report_type = Column(String(50), nullable=False)
    parameters = Column(String, nullable=False)  # JSON string of parameters
    data = Column(String, nullable=False)  # JSON string of report data
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<ReportCache(type='{self.report_type}', created_at='{self.created_at}')>" 