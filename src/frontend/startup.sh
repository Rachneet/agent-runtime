#!/bin/bash

# Agent Runtime Platform Startup Script
# This script starts both the Runtime API and Streamlit Frontend

echo "🚀 Starting Agent Runtime Platform..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python not found. Please install Python 3.10 or higher.${NC}"
    exit 1
fi


# # Create log directory
# mkdir -p logs

# # Start Runtime API in background
# echo -e "${BLUE}🔧 Starting Runtime API...${NC}"
# python src/backend/main.py > logs/api.log 2>&1 &
# API_PID=$!
# echo -e "${GREEN}✅ Runtime API started (PID: $API_PID)${NC}"
# echo "   Logs: logs/api.log"
# echo "   API: http://localhost:8001"
# echo "   Docs: http://localhost:8001/docs"
# echo ""

# # Wait for API to be ready
# echo -e "${BLUE}⏳ Waiting for API to be ready...${NC}"
# for i in {1..10}; do
#     if curl -s http://localhost:8001/ > /dev/null 2>&1; then
#         echo -e "${GREEN}✅ API is ready${NC}"
#         break
#     fi
#     if [ $i -eq 10 ]; then
#         echo -e "${YELLOW}⚠️  API taking longer than expected. Check logs/api.log${NC}"
#     fi
#     sleep 1
# done

echo ""

# Start Streamlit Frontend
echo -e "${BLUE}🎨 Starting Streamlit Frontend...${NC}"
echo -e "${GREEN}✅ Streamlit starting...${NC}"
echo "   URL: http://localhost:8501"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Agent Runtime Platform is running!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Access the platform at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down services...${NC}"
    kill $API_PID 2>/dev/null
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Start Streamlit (this will block)
streamlit run src/frontend/app.py --server.port 8501 --server.address localhost

# If streamlit exits, cleanup
cleanup