#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting PPV System Health Monitor (Development)${NC}"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if PostgreSQL is running
check_postgres() {
    if command_exists psql; then
        if psql -h localhost -U postgres -d postgres -c '\l' >/dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Function to create database if it doesn't exist
create_database() {
    echo -e "${YELLOW}📊 Setting up database...${NC}"
    if psql -h localhost -U postgres -d postgres -c "CREATE DATABASE ppv_system_health;" 2>/dev/null; then
        echo -e "${GREEN}✅ Database 'ppv_system_health' created${NC}"
    else
        echo -e "${YELLOW}⚠️  Database might already exist (this is okay)${NC}"
    fi
}

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

if ! command_exists node; then
    echo -e "${RED}❌ Node.js not found. Install Node.js first.${NC}"
    exit 1
fi

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 not found. Install Python 3 first.${NC}"
    exit 1
fi

if ! command_exists psql; then
    echo -e "${RED}❌ PostgreSQL client not found. Install PostgreSQL first.${NC}"
    exit 1
fi

# Check if PostgreSQL is running
if ! check_postgres; then
    echo -e "${RED}❌ PostgreSQL is not running or not accessible.${NC}"
    echo -e "${YELLOW}💡 Start PostgreSQL first:${NC}"
    echo -e "   brew services start postgresql"
    echo -e "   # or #"
    echo -e "   sudo systemctl start postgresql"
    exit 1
fi

# Create database if needed
create_database

# Install dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    cd frontend && npm install && cd ..
fi

if [ ! -d "backend/.venv" ]; then
    echo -e "${YELLOW}🐍 Setting up Python virtual environment...${NC}"
    cd backend
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# Start services
echo -e "${GREEN}🎯 Starting services...${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    jobs -p | xargs -r kill
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start backend
echo -e "${YELLOW}🔧 Starting backend on http://localhost:8000${NC}"
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 2

# Start frontend
echo -e "${YELLOW}🎨 Starting frontend on http://localhost:3000${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo -e "${GREEN}✅ Services started successfully!${NC}"
echo -e "${GREEN}🌐 Frontend: http://localhost:3000${NC}"
echo -e "${GREEN}📡 Backend API: http://localhost:8000${NC}"
echo -e "${GREEN}📖 API Docs: http://localhost:8000/docs${NC}"
echo -e "${YELLOW}📝 Press Ctrl+C to stop all services${NC}"

# Wait for background processes
wait