from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import engine, get_db, Base
from app.schemas import (
    RuleCreate, RuleResponse, PaginatedResponse, ConsolidatedRuleResponse,
    TenantCreate, TenantResponse,
    CountryCreate, CountryResponse,
    PlatformCreate, PlatformResponse,
    UserRoleCreate, UserRoleResponse,
    AbTestCreate, AbTestResponse,
)
from app.services import (
    rule_service, tenant_service, country_service,
    platform_service, user_role_service, ab_test_service,
)

app = FastAPI(title="Rules Engine POC")

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    from app.seed import seed_data
    db = next(get_db())
    seed_data(db)

# === Rules ===
@app.get("/rules", response_model=PaginatedResponse[RuleResponse])
def list_rules(
    skip: int = 0,
    limit: int = 20,
    tenant: str | None = None,
    country: str | None = None,
    platform: str | None = None,
    user_role: str | None = None,
    ab_test: str | None = None,
    db: Session = Depends(get_db),
):
    """Lista todas as regras cadastradas com paginação e filtros opcionais."""
    rules, total = rule_service.list(
        db, skip, limit,
        tenant=tenant,
        country=country,
        platform=platform,
        user_role=user_role,
        ab_test=ab_test,
    )
    items = [RuleResponse.from_orm_with_conversion(r) for r in rules]
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)

@app.get("/rules/match", response_model=ConsolidatedRuleResponse)
def search_rules(
    tenant: str | None = None,
    country: str | None = None,
    platform: str | None = None,
    user_role: str | None = None,
    ab_test: str | None = None,
    db: Session = Depends(get_db),
):
    """Busca regras por contexto e retorna uma regra consolidada com os valores hierárquicos."""
    return rule_service.match(db, tenant, country, platform, user_role, ab_test)

@app.post("/rules", response_model=RuleResponse, status_code=201)
def create_rule(rule: RuleCreate, db: Session = Depends(get_db)):
    """Cria uma nova regra com seletores de contexto e valores numéricos."""
    created = rule_service.create(db, rule)
    return RuleResponse.from_orm_with_conversion(created)

@app.put("/rules/{rule_id}", response_model=RuleResponse)
def update_rule(rule_id: int, rule: RuleCreate, db: Session = Depends(get_db)):
    """Atualiza uma regra existente."""
    updated = rule_service.update(db, rule_id, rule)
    return RuleResponse.from_orm_with_conversion(updated)

@app.delete("/rules/{rule_id}", status_code=204)
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    """Remove uma regra pelo ID."""
    rule_service.delete(db, rule_id)


# === Tenants ===
@app.get("/tenants", response_model=list[TenantResponse])
def list_tenants(db: Session = Depends(get_db)):
    """Lista todos os tenants disponíveis."""
    return tenant_service.list(db)

@app.post("/tenants", response_model=TenantResponse, status_code=201)
def create_tenant(tenant: TenantCreate, db: Session = Depends(get_db)):
    """Cadastra um novo tenant."""
    return tenant_service.create(db, tenant)

@app.delete("/tenants/{tenant_id}", status_code=204)
def delete_tenant(tenant_id: int, db: Session = Depends(get_db)):
    """Remove um tenant pelo ID."""
    tenant_service.delete(db, tenant_id)


# === Countries ===
@app.get("/countries", response_model=list[CountryResponse])
def list_countries(db: Session = Depends(get_db)):
    """Lista todos os países disponíveis."""
    return country_service.list(db)

@app.post("/countries", response_model=CountryResponse, status_code=201)
def create_country(country: CountryCreate, db: Session = Depends(get_db)):
    """Cadastra um novo país (código ISO 2 letras)."""
    return country_service.create(db, country)

@app.delete("/countries/{country_id}", status_code=204)
def delete_country(country_id: int, db: Session = Depends(get_db)):
    """Remove um país pelo ID."""
    country_service.delete(db, country_id)


# === Platforms ===
@app.get("/platforms", response_model=list[PlatformResponse])
def list_platforms(db: Session = Depends(get_db)):
    """Lista todas as plataformas disponíveis."""
    return platform_service.list(db)

@app.post("/platforms", response_model=PlatformResponse, status_code=201)
def create_platform(platform: PlatformCreate, db: Session = Depends(get_db)):
    """Cadastra uma nova plataforma."""
    return platform_service.create(db, platform)

@app.delete("/platforms/{platform_id}", status_code=204)
def delete_platform(platform_id: int, db: Session = Depends(get_db)):
    """Remove uma plataforma pelo ID."""
    platform_service.delete(db, platform_id)


# === User Roles ===
@app.get("/user-roles", response_model=list[UserRoleResponse])
def list_user_roles(db: Session = Depends(get_db)):
    """Lista todos os níveis de usuário disponíveis."""
    return user_role_service.list(db)

@app.post("/user-roles", response_model=UserRoleResponse, status_code=201)
def create_user_role(user_role: UserRoleCreate, db: Session = Depends(get_db)):
    """Cadastra um novo nível de usuário."""
    return user_role_service.create(db, user_role)

@app.delete("/user-roles/{user_role_id}", status_code=204)
def delete_user_role(user_role_id: int, db: Session = Depends(get_db)):
    """Remove um nível de usuário pelo ID."""
    user_role_service.delete(db, user_role_id)


# === A/B Tests ===
@app.get("/ab-tests", response_model=list[AbTestResponse])
def list_ab_tests(db: Session = Depends(get_db)):
    """Lista todos os testes A/B disponíveis."""
    return ab_test_service.list(db)

@app.post("/ab-tests", response_model=AbTestResponse, status_code=201)
def create_ab_test(ab_test: AbTestCreate, db: Session = Depends(get_db)):
    """Cadastra um novo teste A/B."""
    return ab_test_service.create(db, ab_test)

@app.delete("/ab-tests/{ab_test_id}", status_code=204)
def delete_ab_test(ab_test_id: int, db: Session = Depends(get_db)):
    """Remove um teste A/B pelo ID."""
    ab_test_service.delete(db, ab_test_id)
