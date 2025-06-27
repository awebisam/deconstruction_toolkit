#!/bin/bash

# Narrative Deconstruction Toolkit - Startup Script

echo "🚀 Starting Narrative Deconstruction Toolkit..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please configure your Azure OpenAI credentials."
    exit 1
fi

# Activate virtual environment and start the server
echo "📡 Starting FastAPI server..."
source .venv/bin/activate
python main.py

echo "🎯 Server should be running at http://localhost:8000"
