# Multi-Layer Network Analysis Backend

A comprehensive backend system for detecting hidden communities and coordinated misinformation networks across multi-layer social media networks using Social Network Analysis (SNA) techniques.

## 🎯 Project Overview

This project implements a backend API for analyzing multi-layer social networks to:
- Build multi-layer network graphs from social media interactions
- Detect overlapping communities across different network layers
- Identify coordinated accounts using temporal and structural patterns
- Detect misinformation clusters using graph features and veracity scores
- Provide visualization data for network exploration

## 🏗️ Architecture

```
SNA AAT/
├── api/                    # FastAPI backend endpoints
│   ├── __init__.py
│   └── main.py            # Main API application
├── data/                   # Data loading and preprocessing
│   ├── __init__.py
│   └── data_loader.py     # MuMiN dataset loader
├── models/                 # Network analysis models
│   ├── __init__.py
│   ├── multilayer_network.py      # Multi-layer network construction
│   ├── community_detection.py     # Community detection algorithms
│   ├── coordination_detector.py   # Coordinated behavior detection
│   └── misinformation_detector.py # Misinformation cluster detection
├── utils/                  # Utility functions
│   ├── __init__.py
│   └── logger.py          # Logging utilities
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── main.py               # Application entry point
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd "SNA AAT"
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment (optional):**
   Create a `.env` file in the root directory:
   ```env
   API_HOST=0.0.0.0
   API_PORT=8000
   API_DEBUG=False
   MAX_TWEETS=100000
   ```

### Running the Server

**Option 1: Using the main entry point**
```bash
python main.py
```

**Option 2: Using uvicorn directly**
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, access:
- **Interactive API docs (Swagger):** `http://localhost:8000/docs`
- **Alternative docs (ReDoc):** `http://localhost:8000/redoc`

## 📡 API Endpoints

### Core Endpoints

#### 1. Start Analysis
```http
POST /api/analyze
Content-Type: application/json

{
  "sample_size": 10000,
  "layers": ["retweet", "mention", "hashtag"],
  "algorithms": ["louvain", "leiden", "infomap"]
}
```

#### 2. Get Analysis Status
```http
GET /api/status/{analysis_id}
```

#### 3. Get Network Statistics
```http
GET /api/network/stats
```

#### 4. Get Community Detection Results
```http
GET /api/communities?algorithm=louvain&layer=retweet
```

#### 5. Get Coordinated Behavior Results
```http
GET /api/coordination
```

#### 6. Get Misinformation Clusters
```http
GET /api/misinformation
```

#### 7. Get Visualization Data
```http
GET /api/visualization/data?max_nodes=1000&layer=retweet
```

## 🔧 Configuration

Edit `config.py` to customize:

- **Network Layers:** Enable/disable layers (follower, retweet, mention, hashtag, reply)
- **Community Detection:** Adjust resolution parameters for algorithms
- **Coordination Detection:** Set thresholds for temporal windows, similarity scores
- **Misinformation Detection:** Configure veracity thresholds, cluster sizes
- **Visualization:** Set node limits, layout preferences

## 📊 Features

### Multi-Layer Network Construction

- **Follower Layer:** User follow relationships
- **Retweet Layer:** Retweet interactions
- **Mention Layer:** @mention interactions
- **Reply Layer:** Reply interactions
- **Hashtag Layer:** Hashtag co-occurrence network

### Community Detection Algorithms

1. **Louvain Method:** Fast modularity-based community detection
2. **Leiden Algorithm:** Improved stability over Louvain
3. **Infomap:** Flow-based community detection
4. **Multi-Layer Detection:** Cross-layer community identification

### Coordinated Behavior Detection

Detects coordination using:
- **Temporal Synchronization:** Accounts posting within short time windows
- **Content Similarity:** High text similarity using TF-IDF and cosine similarity
- **Hashtag Coordination:** Simultaneous use of same hashtags
- **URL Sharing:** Rapid sharing of same URLs
- **Structural Patterns:** Star-shaped clusters, bot-like patterns

### Misinformation Detection

Identifies misinformation clusters using:
- **Low Veracity Scores:** Communities with low average veracity
- **Rapid Spread Patterns:** High velocity information spread
- **Coordinated Misinformation:** Coordinated groups spreading false information
- **Structural Anomalies:** Suspicious network structures
- **Bot Clusters:** Bot-like behavior patterns

## 📈 Usage Example

### Python Client Example

```python
import requests

# Start analysis
response = requests.post("http://localhost:8000/api/analyze", json={
    "sample_size": 10000,
    "algorithms": ["louvain", "leiden"]
})

analysis_id = response.json()["analysis_id"]

# Check status
status = requests.get(f"http://localhost:8000/api/status/{analysis_id}")
print(status.json())

# Get results
communities = requests.get("http://localhost:8000/api/communities")
coordination = requests.get("http://localhost:8000/api/coordination")
misinformation = requests.get("http://localhost:8000/api/misinformation")

# Get visualization data
viz_data = requests.get("http://localhost:8000/api/visualization/data?max_nodes=500")
```

### cURL Example

```bash
# Start analysis
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"sample_size": 10000}'

# Get communities
curl "http://localhost:8000/api/communities"

# Get visualization data
curl "http://localhost:8000/api/visualization/data?max_nodes=1000"
```

## 🗂️ Dataset

The backend is designed to work with the **MuMiN dataset**, a large-scale multilingual misinformation dataset. 

### MuMiN Dataset Features:
- Over 21 million tweets
- 2 million users
- 12,914 fact-checked claims
- 41 languages
- Heterogeneous graph structure

### Using Your Own Data

To use custom data, modify `data/data_loader.py`:
1. Implement your data loading logic
2. Ensure data format matches expected structure:
   - `users`: DataFrame with user information
   - `tweets`: DataFrame with tweet data (text, timestamps, user_id, etc.)
   - `claims`: DataFrame with claim veracity information

## 🧪 Testing

Test the API endpoints:

```bash
# Health check
curl http://localhost:8000/api/health

# Get API info
curl http://localhost:8000/
```

## 📝 Output Format

### Community Detection Output
```json
{
  "status": "success",
  "communities": {
    "retweet_louvain": {
      "algorithm": "louvain",
      "layer": "retweet",
      "communities": {"user1": 0, "user2": 0, "user3": 1},
      "n_communities": 2,
      "modularity": 0.75
    }
  }
}
```

### Coordination Detection Output
```json
{
  "status": "success",
  "coordination": {
    "coordinated_groups": [
      {
        "accounts": ["user1", "user2", "user3"],
        "signals": ["temporal", "content"],
        "confidence_score": 0.85
      }
    ],
    "n_groups": 1
  }
}
```

### Misinformation Detection Output
```json
{
  "status": "success",
  "misinformation": {
    "misinfo_clusters": [
      {
        "cluster_id": "veracity_0",
        "nodes": ["user1", "user2"],
        "avg_veracity": 0.2,
        "risk_score": 0.8,
        "indicator": "low_veracity"
      }
    ],
    "n_clusters": 1
  }
}
```

## 🔍 Performance Considerations

- For large datasets, use `sample_size` parameter to limit data
- Adjust `max_nodes` in visualization endpoint for better performance
- Consider using distributed computing for very large networks
- Cache results for repeated queries

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors:**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.8+)

2. **Memory Issues:**
   - Reduce `sample_size` in analysis request
   - Reduce `max_nodes` in visualization requests
   - Process data in batches

3. **Dataset Loading:**
   - MuMiN dataset requires API token (configure in data loader)
   - For development, sample data is generated automatically

## 📚 Dependencies

Key libraries:
- **FastAPI:** Modern web framework
- **NetworkX:** Network analysis
- **python-igraph:** Advanced graph algorithms
- **cdlib:** Community detection library
- **scikit-learn:** Machine learning utilities
- **pandas/numpy:** Data processing

See `requirements.txt` for complete list.

## 🤝 Contributing

This is a project backend. To extend:
1. Add new detection algorithms in `models/`
2. Add new API endpoints in `api/main.py`
3. Extend data loading in `data/data_loader.py`

## 📄 License

This project is for academic/research purposes.

## 🙏 Acknowledgments

- MuMiN dataset creators
- NetworkX and igraph communities
- FastAPI framework

---

**Note:** This backend provides the core analysis engine. For visualization, connect a frontend (e.g., React, D3.js, Gephi) to consume the API endpoints.

