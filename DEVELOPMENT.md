# SmartDine Development Guide

## Prerequisites
- Python 3.8+
- Node.js 14+
- Docker
- AWS CLI configured
- Git for Windows (with Git Bash)
- PowerShell 5.1 or higher

## Initial Setup
```powershell
# Clone the repository
git clone https://github.com/yourusername/smartdine.git
cd smartdine

# Run setup script (using Git Bash or WSL)
bash scripts/setup.sh
```

## Development Workflow

### Starting Local Development Environment
```powershell
# Start local services
docker-compose up -d

# Start backend API
cd backend/api
.\.venv\Scripts\Activate.ps1
uvicorn src.main:app --reload

# Start frontend (in another PowerShell window)
cd frontend/web
npm run dev
```

### Running Tests
```powershell
# Backend tests
cd backend/api
.\.venv\Scripts\Activate.ps1
pytest
deactivate

# Frontend tests
cd frontend/web
npm test
```

### Virtual Environment Management
All Python dependencies are installed in local `.venv` directories:
- Backend API: `backend/api/.venv/`
- Workers: `backend/workers/.venv/`

To activate virtual environments in PowerShell:
```powershell
# For API
cd backend/api
.\.venv\Scripts\Activate.ps1

# For Workers
cd backend/workers
.\.venv\Scripts\Activate.ps1

# To deactivate
deactivate
```

### Deployment
```powershell
# Deploy infrastructure
cd infrastructure
cdk deploy --all
```

## Common PowerShell Issues and Solutions

1. **Execution Policy**
If you get execution policy errors, you might need to run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

2. **Virtual Environment Activation**
If activation fails, ensure you're using the correct path:
```powershell
# Use this exact path
.\.venv\Scripts\Activate.ps1
```

3. **Path Separators**
Always use backslashes (`\`) for paths in PowerShell instead of forward slashes (`/`)

## Project Structure
[Include the project structure from README.md]

## Common Issues and Solutions
[To be populated as issues arise] 