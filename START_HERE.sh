#!/bin/bash
# CRM-Leads Quick Launcher
# Double-click this file and select "Execute" or "Run in Terminal"

# Kill any existing server
pkill -f "manage.py runserver" 2>/dev/null
sleep 1

# Open a new terminal and run the server
xfce4-terminal --title="CRM-Leads Server" --hold --command="bash -c '
cd /home/jimm/CRM-Leads
clear
echo \"========================================\"
echo \"  🚀 CRM-LEADS SERVER\"
echo \"  Customer Relationship Management\"
echo \"========================================\"
echo \"\"
echo \"Starting server...\"
echo \"URL: http://127.0.0.1:8000\"
echo \"\"
echo \"Press Ctrl+C to stop the server\"
echo \"========================================\"
echo \"\"
sleep 2
xdg-open http://127.0.0.1:8000 2>/dev/null &
/home/jimm/CRM-Leads/venv_linux/bin/python /home/jimm/CRM-Leads/manage.py runserver
exec bash
'" 2>/dev/null || \

# Fallback for non-XFCE systems
gnome-terminal --title="CRM-Leads Server" -- bash -c '
cd /home/jimm/CRM-Leads
clear
echo "========================================"
echo "  🚀 CRM-LEADS SERVER"
echo "  Customer Relationship Management"
echo "========================================"
echo ""
echo "Starting server..."
echo "URL: http://127.0.0.1:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""
sleep 2
xdg-open http://127.0.0.1:8000 2>/dev/null &
/home/jimm/CRM-Leads/venv_linux/bin/python /home/jimm/CRM-Leads/manage.py runserver
exec bash
' 2>/dev/null || \

# Final fallback - x-terminal-emulator
x-terminal-emulator -e "bash -c '
cd /home/jimm/CRM-Leads
clear
echo \"========================================\"
echo \"  🚀 CRM-LEADS SERVER\"
echo \"========================================\"
echo \"\"
echo \"Starting server at http://127.0.0.1:8000\"
echo \"Press Ctrl+C to stop\"
echo \"\"
sleep 2
xdg-open http://127.0.0.1:8000 2>/dev/null &
/home/jimm/CRM-Leads/venv_linux/bin/python /home/jimm/CRM-Leads/manage.py runserver
exec bash
'"
