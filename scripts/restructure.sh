#!/bin/bash

# Create new directory structure
mkdir -p data-crawler/src/{crawlers,ai,tasks,models}
mkdir -p backend/fastapi-api/src/{api,models,services,utils}

# Move crawler files
mv backend/crawlers/src/crawlers/* data-crawler/src/crawlers/
mv backend/crawlers/src/ai/* data-crawler/src/ai/
mv backend/crawlers/src/tasks/* data-crawler/src/tasks/
mv backend/crawlers/src/models/* data-crawler/src/models/
mv backend/crawlers/src/config.py data-crawler/src/

# Move crawler configuration files
mv backend/crawlers/Dockerfile data-crawler/
mv backend/crawlers/requirements.txt data-crawler/

# Move and rename API
mv backend/api/* backend/fastapi-api/
rm -rf backend/api
rm -rf backend/crawlers

echo "Project restructured successfully!" 