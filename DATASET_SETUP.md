# Dataset Setup Guide

## Overview

The backend supports three ways to use data:
1. **Sample Data (Default)** - Automatically generated, no setup needed
2. **MuMiN Dataset** - Real misinformation dataset (requires Twitter/X API token)
3. **Custom Dataset** - Your own data files

---

## Option 1: Sample Data (Recommended for Testing)

**No installation needed!** The backend automatically generates sample data for development and testing.

### Features:
- ✅ 1,000 users
- ✅ 5,000 tweets
- ✅ Realistic network structure
- ✅ Veracity scores
- ✅ Ready to use immediately

### Usage:
Just start the server - sample data is generated automatically:
```bash
python main.py
```

The sample data includes:
- User interactions (retweets, mentions, replies)
- Hashtag co-occurrences
- Veracity scores for misinformation detection
- Temporal patterns for coordination detection

---

## Option 2: MuMiN Dataset (Real Data)

MuMiN is a large-scale multilingual misinformation dataset with over 21 million tweets.

### Prerequisites:
1. **Twitter/X API Bearer Token**
   - Sign up at: https://developer.twitter.com/
   - Create an app and get your Bearer Token
   - Free tier available (limited requests)

### Installation Steps:

#### Step 1: Get Twitter/X API Token
1. Go to https://developer.twitter.com/en/portal/dashboard
2. Create a new project/app
3. Generate a Bearer Token
4. Copy the token

#### Step 2: Configure the Token

**Option A: Environment Variable (Recommended)**
```bash
# Create .env file in project root
MUMIN_BEARER_TOKEN=your_bearer_token_here
```

**Option B: Direct in Code**
Edit `data/data_loader.py` and add your token in the `_load_mumin_data` method.

#### Step 3: Update Data Loader

The MuMiN loading is already set up. Just uncomment and configure:

```python
# In data/data_loader.py, update _load_mumin_data method
from mumin import compile_dataset
import os

def _load_mumin_data(self, max_tweets: int):
    bearer_token = os.getenv('MUMIN_BEARER_TOKEN')
    if not bearer_token:
        raise ValueError("MUMIN_BEARER_TOKEN not found in environment")
    
    dataset = compile_dataset(
        size='small',  # 'small', 'medium', or 'large'
        bearer_token=bearer_token
    )
    
    # Convert to our format
    return self._convert_mumin_to_format(dataset)
```

#### Step 4: Load Dataset

The dataset will be automatically loaded when you start an analysis:
```bash
python main.py
```

Then call:
```bash
POST /api/analyze
{
  "sample_size": 10000  # Adjust based on your needs
}
```

### MuMiN Dataset Sizes:
- **small**: ~100K tweets (good for testing)
- **medium**: ~1M tweets (moderate analysis)
- **large**: Full dataset ~21M tweets (requires significant resources)

### Caching:
The dataset is automatically cached in `data/mumin_cache/` to avoid re-downloading.

---

## Option 3: Custom Dataset

If you have your own social media data, you can load it directly.

### Data Format Required:

Your data should be in CSV or Parquet format with these structures:

#### 1. Users CSV (`users.csv`)
```csv
user_id,username,followers_count,verified,created_at
user1,alice,1000,False,2020-01-01
user2,bob,5000,True,2019-06-15
```

#### 2. Tweets CSV (`tweets.csv`)
```csv
tweet_id,user_id,text,created_at,retweet_count,like_count,reply_count,is_retweet,retweeted_tweet_id,in_reply_to_user_id,hashtags,urls,veracity_score
tweet1,user1,"Check this out!",2023-01-01 10:00:00,10,50,5,False,,,"news,politics","https://example.com",0.8
tweet2,user2,"RT: Check this out!",2023-01-01 10:01:00,0,0,0,True,tweet1,,"news,politics",,0.8
```

**Note:** 
- `hashtags` should be comma-separated string or JSON list
- `urls` should be comma-separated string or JSON list
- `veracity_score` should be 0.0 (false) to 1.0 (true)

#### 3. Claims CSV (`claims.csv`) - Optional
```csv
claim_id,text,veracity,veracity_score
claim1,"This is a claim",false,0.2
claim2,"Another claim",true,0.9
```

### Loading Custom Data:

#### Method 1: Update Data Loader

Edit `data/data_loader.py`:

```python
def load_custom_dataset(self, data_dir: str):
    """Load custom dataset from CSV files"""
    data_dir = Path(data_dir)
    
    users = pd.read_csv(data_dir / "users.csv")
    tweets = pd.read_csv(data_dir / "tweets.csv")
    
    # Parse hashtags and URLs if they're strings
    if 'hashtags' in tweets.columns:
        tweets['hashtags'] = tweets['hashtags'].apply(
            lambda x: x.split(',') if isinstance(x, str) else x
        )
    
    claims = pd.read_csv(data_dir / "claims.csv") if (data_dir / "claims.csv").exists() else pd.DataFrame()
    
    return {
        'users': users,
        'tweets': tweets,
        'claims': claims,
        'tweet_claims': pd.DataFrame()  # Optional linking
    }
```

#### Method 2: Use API Endpoint (Future)

You could add an endpoint to upload custom data:
```python
@app.post("/api/upload-dataset")
async def upload_dataset(files: List[UploadFile]):
    # Process uploaded CSV files
    pass
```

---

## Quick Start Examples

### Example 1: Use Sample Data (No Setup)
```bash
# Just start the server
python main.py

# Sample data is automatically generated
```

### Example 2: Use MuMiN with API Token
```bash
# 1. Set environment variable
export MUMIN_BEARER_TOKEN="your_token_here"  # Linux/Mac
# OR
set MUMIN_BEARER_TOKEN=your_token_here  # Windows CMD
# OR
$env:MUMIN_BEARER_TOKEN="your_token_here"  # PowerShell

# 2. Start server
python main.py

# 3. The dataset will be loaded automatically
```

### Example 3: Load Custom Data
```python
from data.data_loader import MuMiNDataLoader

loader = MuMiNDataLoader()
data = loader.load_custom_dataset("path/to/your/data")
```

---

## Dataset Configuration

Edit `config.py` to customize dataset settings:

```python
MUMIN_CONFIG = {
    "max_tweets": 100000,  # Limit for development
    "languages": ["en"],    # Focus on English
    "min_claim_veracity": 0.5,
    "cache_dir": "data/mumin_cache",
}
```

---

## Troubleshooting

### Issue: "MUMIN_BEARER_TOKEN not found"
**Solution:** Set the environment variable or add token to `.env` file

### Issue: "Rate limit exceeded"
**Solution:** 
- Use smaller dataset size
- Wait between requests
- Use cached data

### Issue: "Memory error with large dataset"
**Solution:**
- Reduce `max_tweets` in config
- Use `sample_size` parameter in API calls
- Process data in batches

### Issue: "Dataset not loading"
**Solution:**
- Check internet connection (MuMiN downloads from Twitter)
- Verify API token is valid
- Check cache directory permissions
- Fall back to sample data for testing

---

## Data Caching

All datasets are automatically cached in:
```
data/mumin_cache/
```

To clear cache and reload:
```bash
# Delete cache directory
rm -rf data/mumin_cache/  # Linux/Mac
rmdir /s data\mumin_cache  # Windows
```

---

## Next Steps

1. **For Testing:** Use sample data (no setup needed)
2. **For Real Analysis:** Get MuMiN API token and configure
3. **For Custom Data:** Format your data and update loader

The backend will automatically use the best available data source!

