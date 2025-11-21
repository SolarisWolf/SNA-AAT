# Fix Server Issues - Step by Step Guide

## ✅ Server is Actually Working!

All tests show the server is running correctly. If you're seeing issues, follow these steps:

## Step 1: Verify Server is Running

```powershell
# Check if server is running
netstat -ano | findstr :8000

# Should show something like:
# TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING       <PID>
```

## Step 2: Test Server from Command Line

```powershell
# Test health endpoint
curl http://localhost:8000/api/health

# Should return: {"status":"healthy","timestamp":"..."}
```

## Step 3: Test in Browser

### Option A: Use Test Page
1. Open `test_browser.html` in your browser
2. It will automatically test the connection
3. Click buttons to test each endpoint

### Option B: Direct Browser Access
1. Open browser
2. Go to: **http://localhost:8000/docs**
3. You should see the API documentation

## Step 4: If Browser Shows Errors

### Error: "This site can't be reached"
**Solution:**
- Make sure server is running: `python main.py`
- Try `http://127.0.0.1:8000` instead of `localhost`
- Check Windows Firewall settings

### Error: "Connection refused"
**Solution:**
- Server might not be running
- Start it: `python main.py`
- Check if port 8000 is blocked

### Error: CORS or Network Error
**Solution:**
- The server has CORS enabled for all origins
- Try a different browser
- Clear browser cache

### Error: 404 Not Found
**Solution:**
- Make sure you're using correct URLs:
  - ✅ `http://localhost:8000/docs`
  - ✅ `http://localhost:8000/api/health`
  - ❌ `http://0.0.0.0:8000` (won't work in browser)

## Step 5: Restart Server Cleanly

```powershell
# 1. Stop all Python processes
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force

# 2. Wait a moment
timeout /t 2

# 3. Start fresh
.\venv\Scripts\Activate.ps1
python main.py
```

## Step 6: Run Diagnostic Tests

```powershell
# Test all imports and routes
python test_server.py

# Test all endpoints
python test_endpoints.py
```

## Common Issues and Quick Fixes

### Issue: "Module not found"
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: Port already in use
```powershell
# Find and kill process
netstat -ano | findstr :8000
taskkill /F /PID <process_id>

# Or use different port
$env:API_PORT=8001
python main.py
```

### Issue: Server starts but browser can't connect
1. Check Windows Firewall
2. Try `127.0.0.1` instead of `localhost`
3. Try different browser
4. Check if antivirus is blocking

### Issue: Endpoints return 500 errors
- Check server console for error messages
- Run `python test_server.py` to see detailed errors
- Check `logs/app.log` if it exists

## Quick Verification Checklist

- [ ] Virtual environment activated: `.\venv\Scripts\Activate.ps1`
- [ ] Server is running: `python main.py`
- [ ] Port 8000 is listening: `netstat -ano | findstr :8000`
- [ ] Health endpoint works: `curl http://localhost:8000/api/health`
- [ ] Browser can access: `http://localhost:8000/docs`
- [ ] No firewall blocking port 8000

## Still Not Working?

1. **Run full diagnostic:**
   ```powershell
   python test_server.py
   python test_endpoints.py
   ```

2. **Check what specific error you're seeing:**
   - Browser console (F12)
   - Server terminal output
   - Network tab in browser dev tools

3. **Try alternative access:**
   - Use `127.0.0.1` instead of `localhost`
   - Try different browser
   - Use `test_browser.html` file

4. **Share the specific error message** you're seeing

## Expected Behavior

When everything works:
- ✅ Server starts without errors
- ✅ `http://localhost:8000/docs` shows API documentation
- ✅ `http://localhost:8000/api/health` returns `{"status":"healthy"}`
- ✅ All endpoints respond correctly

If you see this, the server IS working! 🎉

