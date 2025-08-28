#!/bin/bash
# Launch the frontend React/Electron UI

cd ../frontend

# Install dependencies if not installed
if [ ! -d "node_modules" ]; then
    npm install
fi

# Start development server
npm start
