# Project Structure

## Directory Layout

```
SNA AAT/
│
├── api/                          # FastAPI Backend
│   ├── __init__.py
│   └── main.py                   # Main API application with endpoints
│
├── data/                         # Data Loading & Preprocessing
│   ├── __init__.py
│   └── data_loader.py           # MuMiN dataset loader and preprocessor
│
├── models/                        # Network Analysis Models
│   ├── __init__.py
│   ├── multilayer_network.py    # Multi-layer network construction
│   ├── community_detection.py   # Community detection algorithms
│   ├── coordination_detector.py # Coordinated behavior detection
│   └── misinformation_detector.py # Misinformation cluster detection
│
├── utils/                         # Utilities
│   ├── __init__.py
│   └── logger.py                # Logging configuration
│
├── config.py                     # Configuration settings
├── main.py                       # Application entry point
├── requirements.txt              # Python dependencies
├── README.md                     # Main documentation
├── example_usage.py              # Example API usage script
└── .gitignore                    # Git ignore rules
```

## Module Descriptions

### API Layer (`api/`)
- **main.py**: FastAPI application with REST endpoints
  - `/api/analyze` - Start network analysis
  - `/api/status/{id}` - Get analysis status
  - `/api/network/stats` - Network statistics
  - `/api/communities` - Community detection results
  - `/api/coordination` - Coordinated behavior results
  - `/api/misinformation` - Misinformation clusters
  - `/api/visualization/data` - Visualization data

### Data Layer (`data/`)
- **data_loader.py**: 
  - Loads MuMiN dataset (or generates sample data)
  - Preprocesses tweets (extracts mentions, hashtags)
  - Builds edge lists for network construction
  - Caches processed data

### Models Layer (`models/`)

#### multilayer_network.py
- `MultiLayerNetwork`: Constructs and manages multi-layer graphs
  - Builds individual layers (follower, retweet, mention, hashtag, reply)
  - Combines layers (union/intersection)
  - Provides layer statistics

#### community_detection.py
- `CommunityDetector`: Detects communities using multiple algorithms
  - Louvain method
  - Leiden algorithm
  - Infomap
  - Multi-layer community detection

#### coordination_detector.py
- `CoordinationDetector`: Identifies coordinated behavior
  - Temporal synchronization
  - Content similarity (TF-IDF + cosine similarity)
  - Hashtag coordination (Jaccard similarity)
  - URL sharing patterns
  - Structural patterns (star-shaped clusters)

#### misinformation_detector.py
- `MisinformationDetector`: Detects misinformation clusters
  - Low veracity score clusters
  - Rapid spread patterns
  - Coordinated misinformation
  - Structural anomalies
  - Bot-like behavior clusters

### Utilities (`utils/`)
- **logger.py**: Centralized logging configuration

### Configuration (`config.py`)
- Centralized configuration for:
  - API settings
  - Dataset parameters
  - Network layer settings
  - Community detection parameters
  - Coordination detection thresholds
  - Misinformation detection settings
  - Visualization preferences

## Data Flow

```
1. Data Loading (data_loader.py)
   ↓
2. Network Construction (multilayer_network.py)
   ↓
3. Community Detection (community_detection.py)
   ↓
4. Coordination Detection (coordination_detector.py)
   ↓
5. Misinformation Detection (misinformation_detector.py)
   ↓
6. API Response (api/main.py)
```

## Key Dependencies

- **FastAPI**: Web framework
- **NetworkX**: Graph operations
- **python-igraph**: Advanced graph algorithms
- **cdlib**: Community detection
- **scikit-learn**: ML utilities (TF-IDF, similarity)
- **pandas/numpy**: Data processing

## Extension Points

To extend the system:

1. **Add new detection algorithm**: Extend `CommunityDetector` or create new detector class
2. **Add new network layer**: Modify `MultiLayerNetwork.build_layers()`
3. **Add new API endpoint**: Add route in `api/main.py`
4. **Add new data source**: Extend `MuMiNDataLoader` or create new loader
5. **Add new coordination signal**: Extend `CoordinationDetector`
6. **Add new misinformation indicator**: Extend `MisinformationDetector`

