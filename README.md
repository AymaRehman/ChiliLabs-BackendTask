## Chili Labs – FastAPI Avatar Upload Service

A small backend service built for a pre-internship test at Chili Labs, designed to handle user authentication and real-time avatar uploads via WebSockets. 
  
### ✨ What this project does
  
- Provides JWT-based authentication
- Lets users upload profile avatars (PNG/JPG)
- Streams real-time WebSocket messages
- Uses SQLite + SQLAlchemy for storage
- Runs fully inside Docker with one command
  
### 🛠️ Tech Stack
  
- FastAPI (Python)
- SQLAlchemy
- JWT authentication
- WebSockets
- Docker / Docker Compose
- Pytest (unit + integration tests)

### How to Run

```
docker compose up --build
```

The server runs at:

```
http://127.0.0.1:8000
```

Find the interactive API docs:
```
http://127.0.0.1:8000/docs
```

Real-Time Websocket Tests:
```
websocat ws://127.0.0.1:8000/ws?token=<JWT_TOKEN>
```

### Project Structure

```
BackendDeveloper/
├── .gitignore
├── BackendDeveloper.db
├── Dockerfile
├── docker-compose.yml
├── README.md
├── requirements.txt
│
├── venv/
│
├── .vscode/
│
├── static/
│
├── tests/
│   ├── __pycache__/
│   ├── test_auth.py
│   └── test_integration.py
│
├── __pycache__/
├── .pytest_cache/
│
├── __init__.py
├── apidoc.apib
├── auth.py
├── database.py
├── jsend.py
├── main.py
├── models.py
├── schemas.py
├── utils.py
├── ws_manager.py
└── ws_test.html
```