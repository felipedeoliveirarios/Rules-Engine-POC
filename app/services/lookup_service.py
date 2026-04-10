from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Tenant, Country, Platform, UserRole, AbTest

class BaseLookupService:
    model = None
    not_found_msg = "Not found"
    
    def list(self, db: Session):
        return db.query(self.model).all()
    
    def create(self, db: Session, data):
        entity = self.model(**data.model_dump())
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity
    
    def delete(self, db: Session, entity_id: int) -> None:
        entity = db.query(self.model).filter(self.model.id == entity_id).first()
        if not entity:
            raise HTTPException(status_code=404, detail=self.not_found_msg)
        db.delete(entity)
        db.commit()

class TenantService(BaseLookupService):
    model = Tenant
    not_found_msg = "Tenant not found"

class CountryService(BaseLookupService):
    model = Country
    not_found_msg = "Country not found"

class PlatformService(BaseLookupService):
    model = Platform
    not_found_msg = "Platform not found"

class UserRoleService(BaseLookupService):
    model = UserRole
    not_found_msg = "User role not found"

class AbTestService(BaseLookupService):
    model = AbTest
    not_found_msg = "A/B test not found"

tenant_service = TenantService()
country_service = CountryService()
platform_service = PlatformService()
user_role_service = UserRoleService()
ab_test_service = AbTestService()
