# Server Troubleshooting Guide

## Common Issues and Solutions

### Issue: Server Not Loading / "Not Found" Errors

#### Solution 1: Check if Server is Running
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# If you see processes, kill them:
taskkill /F /PID <process_id>
```

#### Solution 2: Start Server Correctly
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start server
python main.py

# OR use the improved startup script
python start_server.py
```

#### Solution 3: Check for Import Errors
```powershell
python test_server.py
```

This will test all imports and routes.

#### Solution 4: Access Correct URLs
- **Root:** http://localhost:8000/
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health

**Note:** Use `localhost` or `127.0.0.1`, not `0.0.0.0` in browser

### Issue: Port Already in Use

```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process
taskkill /F /PID <process_id>

# Or use a different port
# Edit config.py or set environment variable:
$env:API_PORT=8001
python main.py
```

### Issue: Import Errors

```powershell
# Reinstall dependencies
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: Module Not Found

Make sure you're in the project root directory:
```powershell
cd "C:\Users\agarw\Downloads\SNA AAT"
python main.py
```

### Issue: Server Starts But Routes Don't Work

1. **Check route registration:**
   ```powershell
   python -c "from api.main import app; print([r.path for r in app.routes])"
   ```

2. **Test specific endpoint:**
   ```powershell
   curl http://localhost:8000/api/health
   ```

3. **Check browser console** for CORS or other errors

### Issue: Background Tasks Not Working

The analysis runs in background. Check status:
```powershell
# Start analysis
curl -X POST http://localhost:8000/api/analyze -H "Content-Type: application/json" -d "{}"

# Check status (use the analysis_id from response)
curl http://localhost:8000/api/status/analysis_20231121_120000
```

## Quick Diagnostic Steps

1. **Test imports:**
   ```powershell
   python test_server.py
   ```

2. **Check server startup:**
   ```powershell
   python start_server.py
   ```

3. **Verify routes:**
   ```powershell
   python -c "from api.main import app; print('Routes:', len(app.routes))"
   ```

4. **Test health endpoint:**
   ```powershell
   curl http://localhost:8000/api/health
   ```

## Expected Server Output

When server starts correctly, you should see:
```
INFO:     Started server process [xxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## Browser Access

- **Windows:** Use `http://localhost:8000` or `http://127.0.0.1:8000`
- **Don't use:** `http://0.0.0.0:8000` (this won't work in browser)

## Still Having Issues?

1. Check `logs/app.log` for error messages
2. Run `python test_server.py` to diagnose
3. Make sure virtual environment is activated
4. Verify all dependencies are installed: `pip list`

