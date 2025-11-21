# How to Install the Dataset

## ✅ Option 1: Use Sample Data (Recommended for Quick Start)

**No installation needed!** The backend automatically generates sample data.

### Steps:
1. **Just start the server:**
   ```bash
   python main.py
   ```

2. **That's it!** Sample data is automatically created with:
   - 1,000 users
   - 5,000 tweets
   - Network interactions
   - Veracity scores

**No API tokens, no downloads, no setup required!**

---

## 📊 Option 2: Use Real MuMiN Dataset

### Prerequisites:
- Twitter/X Developer Account
- Bearer Token from Twitter API

### Installation Steps:

#### Step 1: Get Twitter/X API Bearer Token

1. **Sign up for Twitter Developer Account:**
   - Go to: https://developer.twitter.com/
   - Apply for developer access (free tier available)

2. **Create an App:**
   - Go to: https://developer.twitter.com/en/portal/dashboard
   - Create a new project/app
   - Generate a Bearer Token
   - Copy the token (keep it secret!)

#### Step 2: Set the Token

**Windows PowerShell:**
```powershell
$env:MUMIN_BEARER_TOKEN="your_bearer_token_here"
```

**Windows Command Prompt:**
```cmd
set MUMIN_BEARER_TOKEN=your_bearer_token_here
```

**Linux/Mac:**
```bash
export MUMIN_BEARER_TOKEN='your_bearer_token_here'
```

**Or create `.env` file in project root:**
```env
MUMIN_BEARER_TOKEN=your_bearer_token_here
```

#### Step 3: Verify Setup

Run the setup checker:
```bash
python setup_dataset.py
```

This will:
- ✅ Check if token is set
- ✅ Test sample data (always works)
- ✅ Test MuMiN connection (if token is set)

#### Step 4: Start Using

```bash
python main.py
```

The backend will automatically:
- Use MuMiN dataset if token is set
- Fall back to sample data if token is missing

---

## 🔍 Verify Dataset Installation

### Quick Test:
```bash
python setup_dataset.py
```

### Expected Output:

**With Sample Data (No Token):**
```
✅ Sample Data: Ready
❌ MuMiN Token: Not Set
✅ You can use sample data immediately!
```

**With MuMiN Token Set:**
```
✅ Sample Data: Ready
✅ MuMiN Token: Set
✅ MuMiN Connection: Working
```

---

## 📁 Dataset Information

### Sample Data (Default)
- **Size:** 1,000 users, 5,000 tweets
- **Source:** Auto-generated
- **Use Case:** Testing, development, demos
- **Setup Time:** 0 seconds (automatic)

### MuMiN Dataset (Real Data)
- **Size Options:**
  - `small`: ~100K tweets
  - `medium`: ~1M tweets  
  - `large`: ~21M tweets
- **Source:** Twitter/X via API
- **Use Case:** Real analysis, research
- **Setup Time:** 5-10 minutes (one-time token setup)

---

## 🎯 Which Dataset Should I Use?

### Use Sample Data If:
- ✅ You want to test the system quickly
- ✅ You don't have Twitter API access
- ✅ You're learning/exploring
- ✅ You want to avoid API rate limits

### Use MuMiN Dataset If:
- ✅ You need real-world data
- ✅ You have Twitter API access
- ✅ You're doing research/analysis
- ✅ You need fact-checked misinformation data

---

## 🔄 Switching Between Datasets

The backend automatically chooses the best available:

1. **If `MUMIN_BEARER_TOKEN` is set:** Uses MuMiN dataset
2. **If token is missing:** Uses sample data

**No code changes needed!** Just set/unset the environment variable.

---

## 💾 Data Caching

All datasets are automatically cached in:
```
data/mumin_cache/
```

**Benefits:**
- Faster subsequent loads
- No re-downloading
- Works offline after first load

**Clear Cache:**
```bash
# Delete cache directory to force re-download
rm -rf data/mumin_cache/  # Linux/Mac
rmdir /s data\mumin_cache  # Windows
```

---

## 🛠️ Troubleshooting

### Issue: "MUMIN_BEARER_TOKEN not found"
**Solution:** Set the environment variable (see Step 2 above)

### Issue: "Rate limit exceeded"
**Solution:** 
- Wait a few minutes
- Use smaller dataset size
- Use sample data instead

### Issue: "MuMiN package not installed"
**Solution:** Already installed! It's in `requirements.txt`

### Issue: "Memory error"
**Solution:**
- Reduce `max_tweets` in config
- Use smaller dataset size
- Use sample data

---

## 📚 Additional Resources

- **Detailed Guide:** See `DATASET_SETUP.md`
- **Quick Reference:** See `QUICK_DATASET_GUIDE.md`
- **MuMiN Documentation:** https://mumin-dataset.github.io/

---

## ✅ Quick Start Summary

**Fastest way to get started:**
```bash
# 1. Activate environment
.\venv\Scripts\Activate.ps1

# 2. Start server (uses sample data automatically)
python main.py

# 3. Access API
# Open: http://localhost:8000/docs
```

**That's it!** Sample data is ready to use immediately.

---

## 🎉 Next Steps

1. **Test with sample data** (no setup needed)
2. **Get Twitter API token** (if you want real data)
3. **Run analysis** via API endpoints
4. **Explore results** in visualization

The dataset is ready to use! 🚀

