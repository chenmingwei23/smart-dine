# SmartDine Development Guide

## Prerequisites
- Python 3.8+
- Node.js 14+
- Docker
- AWS CLI configured
- Git

## Package Setup

### Backend Services Setup

#### Windows
```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Core Dependencies
pip install fastapi uvicorn pydantic
```

#### Unix/macOS
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Core Dependencies
pip install fastapi uvicorn pydantic
```

### Common Dependencies
```bash
# Database Dependencies
pip install motor  # MongoDB async driver
pip install redis  # For rate limiting and caching

# Authentication & Security
pip install python-jose[cryptography]  # JWT handling
pip install passlib[bcrypt]  # Password hashing
pip install python-multipart  # Form data handling

# HTTP Client
pip install httpx  # Async HTTP client

# Configuration
pip install pydantic-settings  # Settings management
pip install python-dotenv  # Environment variables
```

### Frontend Setup

#### Windows
```powershell
cd frontend/web
npm install
```

#### Unix/macOS
```bash
cd frontend/web
npm install
```

### Common Frontend Dependencies
```bash
# TypeScript dependencies
npm install --save-dev typescript @types/node @types/react
npm install axios @types/axios

# Update package.json if needed:
{
  "dependencies": {
    "axios": "^1.6.2",
    "@types/axios": "^0.14.0"
  }
}
```

### Docker Services

#### Windows
```powershell
# Start all services
docker-compose up -d

# Individual services
docker-compose up -d redis
docker-compose up -d postgres
```

#### Unix/macOS
```bash
# Start all services
docker compose up -d

# Individual services
docker compose up -d redis
docker compose up -d postgres
```

## Initial Setup

#### Windows
```powershell
# Clone the repository
git clone https://github.com/yourusername/smartdine.git
cd smartdine
```

#### Unix/macOS
```bash
# Clone the repository
git clone https://github.com/yourusername/smartdine.git
cd smartdine
```

## Development Workflow

### Starting Local Development Environment

#### Windows
```powershell
# Start backend API
cd backend/api
.\.venv\Scripts\Activate.ps1
uvicorn src.main:app --reload

# Start frontend (in another window)
cd frontend/web
npm run dev
```

#### Unix/macOS
```bash
# Start backend API
cd backend/api
source .venv/bin/activate
uvicorn src.main:app --reload

# Start frontend (in another terminal)
cd frontend/web
npm run dev
```

### Running Tests

#### Windows
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

#### Unix/macOS
```bash
# Backend tests
cd backend/api
source .venv/bin/activate
pytest
deactivate

# Frontend tests
cd frontend/web
npm test
```

### Environment Variables

#### Windows
```powershell
# Create .env file
Copy-Item .env.example .env
```

#### Unix/macOS
```bash
# Create .env file
cp .env.example .env
```

### Common Issues and Solutions

#### Windows
1. **Execution Policy**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

2. **Path Separators**
- Use backslashes (`\`) for paths

#### Unix/macOS
1. **Permission Issues**
```bash
# Fix script permissions
chmod +x scripts/*.sh

# Fix virtual environment permissions
chmod -R 755 .venv/bin
```

2. **Path Separators**
- Use forward slashes (`/`) for paths

### API Gateway Implementation Considerations

#### Performance and Scaling
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

#### Frontend TypeScript Setup

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