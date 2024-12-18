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

## API Gateway Implementation Considerations

### Performance and Scaling
1. **Current Implementation (FastAPI)**
   - Pros:
     - Fast enough for initial scale (~30k req/s)
     - Easy to maintain and modify
     - Team familiarity with Python
     - Strong type checking with Pydantic
   - Cons:
     - Lower raw performance compared to Go
     - Higher memory usage

2. **Scaling Strategy**
   - Short term: Use FastAPI + AWS API Gateway
   - Medium term: AWS API Gateway for core functions
   - Long term options:
     - Move to Go for better performance
     - Use managed solutions (Kong/Traefik)
     - Full AWS API Gateway + Lambda

3. **AWS Integration**
   - AWS API Gateway can handle:
     - Authentication
     - Rate limiting
     - Basic routing
   - Our FastAPI implementation handles:
     - Custom business logic
     - Service discovery
     - Circuit breaking

### Frontend TypeScript Setup

#### Common Issues and Solutions

1. **Axios Type Declarations**
   ```bash
   # Error: Cannot find module 'axios' or its corresponding type declarations
   
   # Solution: Install axios types
   npm install axios @types/axios
   ```

2. **API Client Export**
   ```typescript
   // Error: Module './client' declares 'APIClient' locally, but it is not exported
   
   // Solution: Update client.ts to export the class
   export class APIClient {
     // ... existing implementation
   }
   ```

3. **TypeScript Configuration**
   ```json
   // tsconfig.json
   {
     "compilerOptions": {
       "esModuleInterop": true,
       "allowSyntheticDefaultImports": true,
       "skipLibCheck": true
     }
   }
   ```

4. **Package Dependencies**
   ```json
   // package.json
   {
     "dependencies": {
       "axios": "^1.6.2",
       "@types/axios": "^0.14.0"
     }
   }
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