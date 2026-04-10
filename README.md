# Rules Engine POC

API para gerenciamento de regras de negócio baseadas em contexto (tenant, país, plataforma, nível de usuário, teste A/B).

## Estrutura

```
├── app/
│   ├── main.py                  # Endpoints da API
│   ├── models.py                # Modelos SQLAlchemy
│   ├── schemas.py               # Schemas Pydantic
│   ├── database.py              # Conexão com banco
│   ├── seed.py                  # Dados iniciais
│   └── services/
│       ├── rule_service.py      # CRUD e busca de regras
│       ├── rule_consolidator.py # Consolidação hierárquica de valores
│       └── lookup_service.py    # CRUD das entidades de contexto
├── data/                        # Banco SQLite (criado automaticamente)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Como rodar

```bash
docker compose up --build
```

## Endpoints

### Rules

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/rules` | Lista regras (paginado, com filtros opcionais) |
| GET | `/rules/match` | Retorna regra consolidada por contexto |
| POST | `/rules` | Cria regra |
| PUT | `/rules/{id}` | Atualiza regra |
| DELETE | `/rules/{id}` | Remove regra |

#### GET /rules

Lista regras com paginação e filtros opcionais por campos de contexto.

Query params:
- `skip`, `limit` — paginação
- `tenant`, `country`, `platform`, `user_role`, `ab_test` — filtros exatos

#### GET /rules/match

Busca regras que casam com o contexto informado (incluindo wildcards `*`) e retorna uma única regra com valores consolidados hierarquicamente.

Query params:
- `tenant`, `country`, `platform`, `user_role`, `ab_test`

**Consolidação de valores:**

Os valores das regras podem ser definidos como:
- `=100` — valor absoluto (define a base)
- `+10` ou `-5` — modificador absoluto (soma/subtrai)
- `10%` — modificador percentual (aplica sobre o valor atual)
- `x1.5` — multiplicador

A consolidação percorre as regras por peso (maior primeiro) e, para cada campo:
1. Acumula modificadores até encontrar um valor absoluto (base)
2. Aplica os modificadores na ordem: absoluto → multiplicador → percentual

### Entidades de contexto

Tenants, Countries, Platforms, User Roles, A/B Tests:

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/{entidade}` | Lista todos |
| POST | `/{entidade}` | Cria |
| DELETE | `/{entidade}/{id}` | Remove |

## Docs

Swagger UI: `http://localhost:8000/docs`
