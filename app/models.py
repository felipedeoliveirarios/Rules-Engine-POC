from sqlalchemy import Column, Integer, String, Index
from app.database import Base

class Rule(Base):
    __tablename__ = "rules"
    id = Column(Integer, primary_key=True, index=True)
    weight = Column(Integer, nullable=False)
    
    tenant = Column(String(64))
    country = Column(String(2))
    platform = Column(String(64))
    user_role = Column(String(64))
    ab_test = Column(String(64))
    
    monthly_fee = Column(String(32))
    max_discount = Column(String(32))
    cashback = Column(String(32))
    trial_days = Column(String(32))
    points_modifier = Column(String(32))
    
    __table_args__ = (
        Index('ix_rules_selectors', 'tenant', 'country', 'platform', 'user_role', 'ab_test'),
    )

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False)

class Country(Base):
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(2), unique=True, nullable=False)
    name = Column(String(100))

class Platform(Base):
    __tablename__ = "platforms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False)

class UserRole(Base):
    __tablename__ = "user_roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False)

class AbTest(Base):
    __tablename__ = "ab_tests"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False)
