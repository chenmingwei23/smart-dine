#!/bin/bash

# Create project structure
mkdir -p frontend/{web,mobile,wechat}/src
mkdir -p backend/api/src/{routes,services,models,utils}
mkdir -p backend/api/tests
mkdir -p backend/workers/{crawlers,processors}/{google_maps,yelp,tripadvisor}
mkdir -p infrastructure/{lib,bin}
mkdir -p shared/{types,constants}

# Set PYTHONPATH to ensure packages are installed in the project directory
export PYTHONPATH="$PWD/backend/api:$PYTHONPATH"

# Initialize backend with local virtual environments
cd backend/api
python -m venv .venv  # Changed from venv to .venv for clarity
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
pip install --target=./.venv/Lib/site-packages fastapi uvicorn pytest requests python-dotenv
pip freeze > requirements.txt
deactivate

cd ../workers
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
pip install --target=./.venv/Lib/site-packages scrapy selenium openai pytest python-dotenv
pip freeze > requirements.txt
deactivate

# Initialize frontend
cd ../../frontend/web
npm init -y
npm install react react-dom react-native-web @react-navigation/native expo

cd ../mobile
npm init -y
npm install react react-native expo @react-navigation/native

# Initialize infrastructure
cd ../../infrastructure
npm init -y
npm install -D aws-cdk aws-cdk-lib constructs typescript @types/node
npx tsc --init

# Create initial configuration files
cd ..
cat > .gitignore << EOL
node_modules/
.venv/
__pycache__/
*.pyc
.env
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
EOL

# Create docker-compose.yml
cat > docker-compose.yml << EOL
version: '3.8'
services:
  dynamodb-local:
    image: amazon/dynamodb-local
    ports:
      - "8000:8000"
  
  redis-cache:
    image: redis:alpine
    ports:
      - "6379:6379"
EOL

# Create environment files
cat > backend/api/.env << EOL
AWS_REGION=us-east-1
STAGE=development
OPENAI_API_KEY=your_key_here
EOL

cat > frontend/web/.env << EOL
REACT_APP_API_URL=http://localhost:8000
REACT_APP_STAGE=development
EOL

# Initialize basic FastAPI application
cat > backend/api/src/main.py << EOL
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SmartDine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to SmartDine API"}
EOL

# Create basic AWS CDK stack
cat > infrastructure/lib/api-stack.ts << EOL
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';

export class ApiStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Add your CDK resources here
  }
}
EOL

echo "Setup completed successfully!" 