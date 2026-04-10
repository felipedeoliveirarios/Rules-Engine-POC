from pydantic import BaseModel, field_validator
from typing import Generic, TypeVar
from decimal import Decimal
import re

T = TypeVar("T")

# Padrão para valores de regra: =100, +10, -5, 15%, x1.5
RULE_VALUE_PATTERN = re.compile(r'^(=|x|[+\-])?(\d+(\.\d+)?)(%)?$')

def validate_rule_value(value: str | None) -> str | None:
    """Valida formato de valor de regra."""
    if value is None:
        return None
    
    if not RULE_VALUE_PATTERN.match(value):
        raise ValueError(
            f'Formato inválido: "{value}". Use: =100 (absoluto), +10/-5 (modificador), 15% (percentual), x1.5 (multiplicador)'
        )
    return value

def parse_numeric_value(value: str | None) -> Decimal | None:
    """Converte string de valor para Decimal, removendo prefixos/sufixos."""
    if not value:
        return None
    
    cleaned = re.sub(r'^[=x+\-]|%$', '', value)
    try:
        return Decimal(cleaned)
    except:
        return None


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int


# Rule
class RuleCreate(BaseModel):
    weight: int
    tenant: str
    country: str
    platform: str
    user_role: str
    ab_test: str
    monthly_fee: str | None = None
    max_discount: str | None = None
    cashback: str | None = None
    trial_days: str | None = None
    points_modifier: str | None = None
    
    @field_validator('tenant', 'country', 'platform', 'user_role', 'ab_test')
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Campo não pode ser vazio')
        return v.strip()
    
    @field_validator('monthly_fee', 'max_discount', 'cashback', 'trial_days', 'points_modifier')
    @classmethod
    def valid_rule_value(cls, v: str | None) -> str | None:
        return validate_rule_value(v)


class RuleResponse(BaseModel):
    id: int
    weight: int
    tenant: str
    country: str
    platform: str
    user_role: str
    ab_test: str
    monthly_fee: Decimal | None = None
    max_discount: Decimal | None = None
    cashback: Decimal | None = None
    trial_days: Decimal | None = None
    points_modifier: Decimal | None = None
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm_with_conversion(cls, rule) -> "RuleResponse":
        return cls(
            id=rule.id,
            weight=rule.weight,
            tenant=rule.tenant,
            country=rule.country,
            platform=rule.platform,
            user_role=rule.user_role,
            ab_test=rule.ab_test,
            monthly_fee=parse_numeric_value(rule.monthly_fee),
            max_discount=parse_numeric_value(rule.max_discount),
            cashback=parse_numeric_value(rule.cashback),
            trial_days=parse_numeric_value(rule.trial_days),
            points_modifier=parse_numeric_value(rule.points_modifier),
        )


class ConsolidatedRuleResponse(BaseModel):
    monthly_fee: Decimal | None = None
    max_discount: Decimal | None = None
    cashback: Decimal | None = None
    trial_days: Decimal | None = None
    points_modifier: Decimal | None = None


# Tenant
class TenantCreate(BaseModel):
    name: str

class TenantResponse(TenantCreate):
    id: int
    class Config:
        from_attributes = True


# Country
class CountryCreate(BaseModel):
    code: str
    name: str | None = None

class CountryResponse(CountryCreate):
    id: int
    class Config:
        from_attributes = True


# Platform
class PlatformCreate(BaseModel):
    name: str

class PlatformResponse(PlatformCreate):
    id: int
    class Config:
        from_attributes = True


# UserRole
class UserRoleCreate(BaseModel):
    name: str

class UserRoleResponse(UserRoleCreate):
    id: int
    class Config:
        from_attributes = True


# AbTest
class AbTestCreate(BaseModel):
    name: str

class AbTestResponse(AbTestCreate):
    id: int
    class Config:
        from_attributes = True
