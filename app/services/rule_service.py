from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Rule
from app.schemas import RuleCreate
from app.services.rule_consolidator import rule_consolidator, ConsolidatedRule

SELECTOR_WILDCARD = "*"


class RuleService:
    def list(
        self, db: Session,
        skip: int = 0,
        limit: int = 20,
        tenant: str | None = None,
        country: str | None = None,
        platform: str | None = None,
        user_role: str | None = None,
        ab_test: str | None = None,
    ) -> tuple[list[Rule], int]:
        query = db.query(Rule)
        
        if tenant:
            query = query.filter(Rule.tenant == tenant)
        if country:
            query = query.filter(Rule.country == country)
        if platform:
            query = query.filter(Rule.platform == platform)
        if user_role:
            query = query.filter(Rule.user_role == user_role)
        if ab_test:
            query = query.filter(Rule.ab_test == ab_test)
        
        total = query.count()
        rules = query.offset(skip).limit(limit).all()
        return rules, total
    
    def match(
        self, db: Session,
        tenant: str | None = None,
        country: str | None = None,
        platform: str | None = None,
        user_role: str | None = None,
        ab_test: str | None = None,
    ) -> ConsolidatedRule:
        query = db.query(Rule)
        
        # Tenant Selector
        if tenant:
            query = query.filter((Rule.tenant == tenant) | (Rule.tenant == SELECTOR_WILDCARD))
        else:
            query = query.filter(Rule.tenant == SELECTOR_WILDCARD)
        
        # Country Selector
        if country:
            query = query.filter((Rule.country == country) | (Rule.country == SELECTOR_WILDCARD))
        else:
            query = query.filter(Rule.country == SELECTOR_WILDCARD)
        
        # Platform Selector
        if platform:
            query = query.filter((Rule.platform == platform) | (Rule.platform == SELECTOR_WILDCARD))
        else:
            query = query.filter(Rule.platform == SELECTOR_WILDCARD)
        
        # User Role Selector
        if user_role:
            query = query.filter((Rule.user_role == user_role) | (Rule.user_role == SELECTOR_WILDCARD))
        else:
            query = query.filter(Rule.user_role == SELECTOR_WILDCARD)
        
        # AB Test Selector
        if ab_test:
            query = query.filter((Rule.ab_test == ab_test) | (Rule.ab_test == SELECTOR_WILDCARD))
        else:
            query = query.filter(Rule.ab_test == SELECTOR_WILDCARD)
            
        
        rules_list = query.order_by(Rule.weight.desc()).all()
        
        return rule_consolidator.consolidate(rules_list)
    
    def get(self, db: Session, rule_id: int) -> Rule:
        rule = db.query(Rule).filter(Rule.id == rule_id).first()
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        return rule
    
    def create(self, db: Session, data: RuleCreate) -> Rule:
        rule = Rule(**data.model_dump())
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return rule
    
    def update(self, db: Session, rule_id: int, data: RuleCreate) -> Rule:
        rule = self.get(db, rule_id)
        for key, value in data.model_dump().items():
            setattr(rule, key, value)
        db.commit()
        db.refresh(rule)
        return rule
    
    def delete(self, db: Session, rule_id: int) -> None:
        rule = self.get(db, rule_id)
        db.delete(rule)
        db.commit()


rule_service = RuleService()
