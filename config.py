"""
Configuration file for the Multi-Layer Network Analysis Backend
"""
import os
from pathlib import Path
from typing import Dict, Any

# Project paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
for dir_path in [DATA_DIR, MODELS_DIR, RESULTS_DIR, LOGS_DIR]:
    dir_path.mkdir(exist_ok=True)

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
API_DEBUG = os.getenv("API_DEBUG", "False").lower() == "true"

# MuMiN Dataset Configuration
MUMIN_CONFIG: Dict[str, Any] = {
    "dataset_name": "mumin",
    "cache_dir": str(DATA_DIR / "mumin_cache"),
    "max_tweets": int(os.getenv("MAX_TWEETS", "100000")),  # Limit for development
    "languages": ["en"],  # Focus on English for now
    "min_claim_veracity": 0.5,  # Minimum veracity score to include
}

# Network Layer Configuration
LAYER_CONFIG: Dict[str, Dict[str, Any]] = {
    "follower": {
        "enabled": True,
        "weight_threshold": 1,
        "directed": True,
    },
    "retweet": {
        "enabled": True,
        "weight_threshold": 1,
        "directed": True,
    },
    "mention": {
        "enabled": True,
        "weight_threshold": 1,
        "directed": True,
    },
    "hashtag": {
        "enabled": True,
        "weight_threshold": 2,  # Co-occurrence threshold
        "directed": False,
    },
    "reply": {
        "enabled": True,
        "weight_threshold": 1,
        "directed": True,
    },
}

# Community Detection Configuration
COMMUNITY_DETECTION_CONFIG: Dict[str, Any] = {
    "louvain": {
        "resolution": 1.0,
        "random_state": 42,
    },
    "leiden": {
        "resolution": 1.0,
        "random_state": 42,
        "n_iterations": 2,
    },
    "infomap": {
        "trials": 10,
    },
    "multilayer": {
        "omega": 1.0,  # Inter-layer coupling
        "gamma": 1.0,  # Resolution parameter
    },
}

# Coordinated Behavior Detection Configuration
COORDINATION_CONFIG: Dict[str, Any] = {
    "temporal_window": 5,  # seconds
    "text_similarity_threshold": 0.9,
    "hashtag_jaccard_threshold": 0.7,
    "min_coordinated_accounts": 3,
    "synchronization_threshold": 0.8,
    "min_interactions": 2,
}

# Misinformation Detection Configuration
MISINFO_CONFIG: Dict[str, Any] = {
    "cluster_size_threshold": 5,
    "veracity_threshold": 0.3,  # Below this is likely misinformation
    "spread_velocity_threshold": 0.5,
    "bot_score_threshold": 0.7,
    "structural_anomaly_threshold": 0.8,
}

# Visualization Configuration
VIZ_CONFIG: Dict[str, Any] = {
    "max_nodes": 1000,  # For performance
    "layout": "spring",  # spring, kamada_kawai, forceatlas2
    "node_size_range": (10, 50),
    "edge_width_range": (1, 5),
    "color_palette": "Set3",
}

# Logging Configuration
LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": str(LOGS_DIR / "app.log"),
            "formatter": "default",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "handlers": ["file", "console"],
        "level": "INFO",
    },
}

