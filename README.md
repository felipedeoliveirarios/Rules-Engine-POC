# Rules Engine POC

API para gerenciamento de regras de negócio baseadas em contexto (tenant, país, plataforma, nível de usuário, teste A/B).

## Como rodar

Com Docker:
```bash
docker compose up --build
```

Localmente:
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Acesse a documentação em `http://localhost:8000/docs`

## Conceitos principais

### Seletores de contexto

Cada regra define seletores que determinam quando ela se aplica:
- `tenant` — identificador do cliente
- `country` — código do país (ex: BR, US)
- `platform` — plataforma de acesso (ex: web, ios, android)
- `user_role` — nível do usuário (ex: free, premium)
- `ab_test` — grupo de teste A/B

Use `*` (wildcard) para indicar que o seletor aceita qualquer valor.

### Cálculo automático de peso

O peso determina a prioridade da regra na consolidação. Ele é calculado automaticamente com base nos seletores definidos (não-wildcard):

| Seletor | Prioridade | Peso |
|---------|------------|------|
| tenant | 0 | +1 |
| country | 1 | +10 |
| platform | 2 | +100 |
| user_role | 3 | +1000 |
| ab_test | 4 | +10000 |

Exemplo: uma regra com `tenant=acme`, `country=*`, `platform=web` tem peso `1 + 100 = 101`.

Regras mais específicas (maior peso) têm prioridade sobre regras genéricas.

### Valores e modificadores

Os campos de valor (`monthly_fee`, `max_discount`, `cashback`, `trial_days`, `points_modifier`) suportam diferentes formatos:

| Formato | Tipo | Exemplo | Descrição |
|---------|------|---------|-----------|
| `=N` | Absoluto | `=100` | Define o valor base |
| `N` ou `+N` ou `-N` | Modificador absoluto | `+10`, `-5` | Soma/subtrai do valor |
| `N%` | Modificador percentual | `15%` | Adiciona N% do valor atual |
| `xN` | Multiplicador | `x1.5` | Multiplica o valor |

### Consolidação hierárquica

O endpoint `/rules/match` busca todas as regras que casam com o contexto e consolida os valores em uma única resposta.

O processo para cada campo:
1. Percorre as regras em ordem de peso (maior primeiro)
2. Acumula modificadores até encontrar um valor absoluto (base)
3. Aplica os modificadores na ordem: absoluto → multiplicador → percentual

Exemplo com `monthly_fee`:
```
Regra peso 10001: monthly_fee = "-5"      (modificador)
Regra peso 100:   monthly_fee = "x1.2"    (multiplicador)  
Regra peso 1:     monthly_fee = "=100"    (base)

Resultado: ((100 - 5) * 1.2) = 114
```

## Estrutura

```
├── app/
│   ├── main.py                  # Endpoints da API
│   ├── models.py                # Modelos SQLAlchemy
│   ├── schemas.py               # Schemas Pydantic (com validação)
│   ├── database.py              # Conexão com banco
│   ├── seed.py                  # Dados iniciais
│   └── services/
│       ├── rule_service.py      # CRUD e busca de regras
│       ├── rule_consolidator.py # Consolidação hierárquica
│       └── lookup_service.py    # CRUD das entidades de contexto
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Endpoints

### Rules

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/rules` | Lista regras (paginado, com filtros) |
| GET | `/rules/match` | Retorna regra consolidada por contexto |
| POST | `/rules` | Cria regra |
| PUT | `/rules/{id}` | Atualiza regra |
| DELETE | `/rules/{id}` | Remove regra |

### Entidades de contexto

Tenants, Countries, Platforms, User Roles, A/B Tests — endpoints para gerenciar os valores válidos de cada seletor.

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/{entidade}` | Lista todos |
| POST | `/{entidade}` | Cria |
| DELETE | `/{entidade}/{id}` | Remove |
