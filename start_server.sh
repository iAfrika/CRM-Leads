#!/bin/bash
# CRM-Leads Startup Script

# Kill any existing server
pkill -f "manage.py runserver" 2>/dev/null
sleep 1

# Change to project directory
cd "/home/jimm/CRM-Leads"

# Start the server
echo "========================================"
echo "  Starting CRM-Leads Server..."
echo "  Access at: http://127.0.0.1:8000"
echo "  Press Ctrl+C to stop"
echo "========================================"
echo ""

# Open browser in background after 3 seconds
(sleep 3 && xdg-open http://127.0.0.1:8000 2>/dev/null) &

# Start Django server (keeps terminal open)
"/home/jimm/CRM-Leads/venv_linux/bin/python" manage.py runserver
