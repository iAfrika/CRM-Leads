#!/bin/bash
# CRM-Leads Launcher with Terminal Window

pkill -f "manage.py runserver" 2>/dev/null
sleep 1

gnome-terminal --title="CRM-Leads Server" -- bash -c '
cd "/home/jimm/CRM-Leads"
echo "========================================"
echo "  🚀 CRM-LEADS"
echo "  Customer Relationship Management"
echo "========================================"
echo ""
echo "Starting server..."
sleep 2
xdg-open http://127.0.0.1:8000 2>/dev/null &
"/home/jimm/CRM-Leads/venv_linux/bin/python" manage.py runserver
'
