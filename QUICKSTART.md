# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Start the Server

```bash
python main.py
```

The API will be running at `http://localhost:8000`

### Step 3: Test the API

Open your browser and go to:
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health

### Step 4: Run Example

In a new terminal:

```bash
python example_usage.py
```

This will:
1. Start a network analysis
2. Monitor progress
3. Display results

## 📝 Basic API Usage

### Start Analysis

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"sample_size": 5000}'
```

### Get Results

```bash
# Communities
curl "http://localhost:8000/api/communities"

# Coordination
curl "http://localhost:8000/api/coordination"

# Misinformation
curl "http://localhost:8000/api/misinformation"
```

## 🎯 What the Backend Does

1. **Loads Data**: MuMiN dataset (or generates sample data)
2. **Builds Networks**: Creates multi-layer graphs (retweet, mention, hashtag, etc.)
3. **Detects Communities**: Finds hidden communities using Louvain, Leiden, Infomap
4. **Finds Coordination**: Identifies coordinated accounts using temporal/content patterns
5. **Detects Misinformation**: Flags misinformation clusters using veracity scores and graph features

## 🔧 Configuration

Edit `config.py` to customize:
- Network layers to include
- Community detection parameters
- Coordination thresholds
- Misinformation detection settings

## 📊 Next Steps

1. **Connect Frontend**: Use the `/api/visualization/data` endpoint
2. **Extend Detection**: Add new algorithms in `models/`
3. **Add Data Sources**: Modify `data/data_loader.py`
4. **Customize Analysis**: Adjust parameters in `config.py`

## 🆘 Troubleshooting

**Port already in use?**
```bash
# Change port in config.py or use:
uvicorn api.main:app --port 8001
```

**Import errors?**
```bash
pip install -r requirements.txt --upgrade
```

**Memory issues?**
- Reduce `sample_size` in analysis request
- Lower `max_nodes` in visualization requests

## 📚 Learn More

- See `README.md` for detailed documentation
- See `PROJECT_STRUCTURE.md` for architecture details
- Check `example_usage.py` for code examples

