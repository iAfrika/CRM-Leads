# CRM-Leads Server Launcher

## Quick Start Scripts

Three ways to run the CRM-Leads server:

### 1. **start_server.sh** (Simple Terminal)
```bash
./start_server.sh
```
- Runs in the current terminal
- Opens browser automatically after 3 seconds
- Press Ctrl+C to stop

### 2. **launch_server.sh** (New Terminal Window)
```bash
./launch_server.sh
```
- Opens a new terminal window
- Better for running in background
- Shows startup banner
- Auto-opens browser

### 3. **CRM-Leads.desktop** (Desktop Icon)
- Double-click the file to launch
- Works like an application shortcut
- To add to desktop:
  ```bash
  cp CRM-Leads.desktop ~/Desktop/
  chmod +x ~/Desktop/CRM-Leads.desktop
  ```
- Or add to applications menu:
  ```bash
  cp CRM-Leads.desktop ~/.local/share/applications/
  ```

## Server Information

- **URL**: http://127.0.0.1:8000
- **Project Location**: /tmp/CRM-Leads
- **Python Environment**: venv_linux

## Stopping the Server

The scripts automatically kill any existing server before starting.
To manually stop:
```bash
pkill -f "manage.py runserver"
```

Or press **Ctrl+C** in the terminal running the server.

## Troubleshooting

If the server doesn't start:
1. Check if port 8000 is already in use
2. Ensure virtual environment exists: `/tmp/CRM-Leads/venv_linux`
3. Check terminal output for error messages

## VS Code Integration

You can also run from VS Code:
- Press **F5** or click "Run and Debug" 
- Or use **Terminal > Run Task > Run Django Server**
