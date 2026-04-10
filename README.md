# POC CRUD API

API simples em FastAPI com SQLite para demonstração de CRUD.

## Estrutura

```
├── app/
│   └── main.py          # API e modelos
├── data/                # Banco SQLite (criado automaticamente)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Como rodar

```bash
docker compose up --build
```

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/items` | Lista todos |
| GET | `/items/{id}` | Busca por ID |
| POST | `/items` | Cria item |
| PUT | `/items/{id}` | Atualiza item |
| DELETE | `/items/{id}` | Remove item |

Body para POST/PUT:
```json
{
  "name": "Nome do item",
  "description": "Descrição opcional"
}
```

## Docs

Swagger UI disponível em `http://localhost:8000/docs`
