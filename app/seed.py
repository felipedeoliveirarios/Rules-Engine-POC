from sqlalchemy.orm import Session
from app.models import Tenant, Country, Platform, UserRole, AbTest, Rule

def seed_data(db: Session):
    """Popula o banco com dados iniciais se estiver vazio."""
    
    # Só executa se não houver dados
    if db.query(Rule).first():
        return
    
    # Tenants
    tenants = [
        Tenant(name="default"),
        Tenant(name="acme"),
        Tenant(name="globex"),
    ]
    db.add_all(tenants)
    
    # Countries
    countries = [
        Country(code="BR", name="Brasil"),
        Country(code="US", name="Estados Unidos"),
        Country(code="PT", name="Portugal"),
    ]
    db.add_all(countries)
    
    # Platforms
    platforms = [
        Platform(name="web"),
        Platform(name="ios"),
        Platform(name="android"),
    ]
    db.add_all(platforms)
    
    # User Roles
    user_roles = [
        UserRole(name="free"),
        UserRole(name="basic"),
        UserRole(name="premium"),
    ]
    db.add_all(user_roles)
    
    # A/B Tests
    ab_tests = [
        AbTest(name="control"),
        AbTest(name="variant_a"),
        AbTest(name="variant_b"),
    ]
    db.add_all(ab_tests)
    
    # Regra base (prioridade mais baixa - todos wildcards)
    base_rule = Rule(
        weight=0,
        tenant="*",
        country="*",
        platform="*",
        user_role="*",
        ab_test="*",
        monthly_fee="=0",
        max_discount="=0",
        cashback="=0",
        trial_days="=0",
        points_modifier="=0",
    )
    db.add(base_rule)
    
    db.commit()
