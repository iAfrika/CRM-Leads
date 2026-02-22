#!/bin/bash
# Simple CRM-Leads Server Launcher

cd /home/jimm/CRM-Leads

# Kill existing servers
pkill -f "manage.py runserver" 2>/dev/null
sleep 1

clear
echo "========================================"
echo "  CRM-LEADS SERVER"
echo "========================================"
echo ""
echo "Starting server..."
echo "URL: http://127.0.0.1:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

# Wait 3 seconds then open browser
(sleep 3 && xdg-open http://127.0.0.1:8000 2>/dev/null) &

# Start the server
/home/jimm/CRM-Leads/venv_linux/bin/python manage.py runserver

echo ""
echo "Server stopped."
read -p "Press Enter to close..."
