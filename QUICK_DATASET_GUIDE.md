# Quick Dataset Guide

## 🚀 Fastest Way: Use Sample Data (No Setup!)

**Just start the server - sample data is automatically generated!**

```bash
python main.py
```

That's it! The backend will automatically create:
- 1,000 users
- 5,000 tweets  
- Realistic network structure
- Ready for analysis

---

## 📊 Use Real MuMiN Dataset

### Step 1: Get Twitter/X API Token
1. Go to https://developer.twitter.com/en/portal/dashboard
2. Create app → Get Bearer Token

### Step 2: Set Token

**PowerShell:**
```powershell
$env:MUMIN_BEARER_TOKEN="your_token_here"
```

**Command Prompt:**
```cmd
set MUMIN_BEARER_TOKEN=your_token_here
```

**Linux/Mac:**
```bash
export MUMIN_BEARER_TOKEN='your_token_here'
```

**Or create `.env` file:**
```
MUMIN_BEARER_TOKEN=your_token_here
```

### Step 3: Test Setup
```bash
python setup_dataset.py
```

### Step 4: Start Server
```bash
python main.py
```

The backend will automatically use MuMiN if token is set, otherwise falls back to sample data.

---

## ✅ Verify Dataset Setup

Run the setup checker:
```bash
python setup_dataset.py
```

This will:
- ✅ Check if token is set
- ✅ Test sample data generation
- ✅ Test MuMiN connection (if token available)
- ✅ Show cache status

---

## 📁 Data Locations

- **Cache:** `data/mumin_cache/` (auto-created)
- **Sample Data:** Generated on-the-fly (no files)
- **Custom Data:** Place CSV files in `data/` directory

---

## 🔄 Switching Between Datasets

The backend automatically chooses:
1. **MuMiN** (if token is set)
2. **Sample Data** (if no token)

No code changes needed!

---

## 💡 Tips

- **For Testing:** Use sample data (no setup)
- **For Real Analysis:** Get MuMiN token
- **For Custom Data:** Update `data/data_loader.py`

See `DATASET_SETUP.md` for detailed instructions.

