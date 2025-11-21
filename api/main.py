"""
FastAPI Backend for Multi-Layer Network Analysis
Provides endpoints for network analysis, community detection, and visualization
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
import json
from datetime import datetime

from config import API_HOST, API_PORT, API_DEBUG
from utils.logger import setup_logger
from data.data_loader import MuMiNDataLoader
from models.multilayer_network import MultiLayerNetwork
from models.community_detection import CommunityDetector
from models.coordination_detector import CoordinationDetector
from models.misinformation_detector import MisinformationDetector

logger = setup_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Layer Network Analysis API",
    description="Backend API for detecting hidden communities and coordinated misinformation networks",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state (in production, use proper state management)
analysis_state: Dict[str, Any] = {}


# Pydantic models for request/response
class AnalysisRequest(BaseModel):
    sample_size: Optional[int] = None
    layers: Optional[List[str]] = None
    algorithms: Optional[List[str]] = None


class AnalysisResponse(BaseModel):
    status: str
    message: str
    analysis_id: Optional[str] = None


# Initialize components
data_loader = MuMiNDataLoader()
network_builder = MultiLayerNetwork()
community_detector = CommunityDetector()
coordination_detector = CoordinationDetector()
misinfo_detector = MisinformationDetector()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Multi-Layer Network Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/analyze": "Start network analysis",
            "GET /api/status/{analysis_id}": "Get analysis status",
            "GET /api/network/stats": "Get network statistics",
            "GET /api/communities": "Get community detection results",
            "GET /api/coordination": "Get coordinated behavior results",
            "GET /api/misinformation": "Get misinformation clusters",
            "GET /api/visualization/data": "Get visualization data",
        }
    }


@app.post("/api/analyze", response_model=AnalysisResponse)
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Start network analysis pipeline
    
    This endpoint triggers the full analysis:
    1. Load data
    2. Build multi-layer network
    3. Detect communities
    4. Detect coordinated behavior
    5. Detect misinformation clusters
    """
    try:
        analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Starting analysis {analysis_id}")
        
        # Run analysis in background
        background_tasks.add_task(
            run_full_analysis,
            analysis_id,
            request.sample_size,
            request.layers,
            request.algorithms
        )
        
        analysis_state[analysis_id] = {
            "status": "running",
            "progress": 0,
            "message": "Analysis started"
        }
        
        return AnalysisResponse(
            status="started",
            message="Analysis started successfully",
            analysis_id=analysis_id
        )
        
    except Exception as e:
        logger.error(f"Error starting analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """Get status of a running analysis"""
    if analysis_id not in analysis_state:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis_state[analysis_id]


@app.get("/api/network/stats")
async def get_network_stats():
    """Get network statistics"""
    if "network" not in analysis_state:
        raise HTTPException(status_code=404, detail="Network not built. Run analysis first.")
    
    network = analysis_state["network"]
    stats = network.get_layer_statistics()
    
    return {
        "status": "success",
        "statistics": stats
    }


@app.get("/api/communities")
async def get_communities(algorithm: Optional[str] = None, layer: Optional[str] = None):
    """Get community detection results"""
    if "communities" not in analysis_state:
        raise HTTPException(status_code=404, detail="Communities not detected. Run analysis first.")
    
    communities = analysis_state["communities"]
    
    # Filter by algorithm and layer if specified
    if algorithm or layer:
        filtered = {}
        for key, result in communities.items():
            if algorithm and result.get('algorithm') != algorithm:
                continue
            if layer and result.get('layer') != layer:
                continue
            filtered[key] = result
        return {"status": "success", "communities": filtered}
    
    return {"status": "success", "communities": communities}


@app.get("/api/coordination")
async def get_coordination():
    """Get coordinated behavior detection results"""
    if "coordination" not in analysis_state:
        raise HTTPException(status_code=404, detail="Coordination analysis not run. Run analysis first.")
    
    return {
        "status": "success",
        "coordination": analysis_state["coordination"]
    }


@app.get("/api/misinformation")
async def get_misinformation():
    """Get misinformation cluster detection results"""
    if "misinformation" not in analysis_state:
        raise HTTPException(status_code=404, detail="Misinformation analysis not run. Run analysis first.")
    
    return {
        "status": "success",
        "misinformation": analysis_state["misinformation"]
    }


@app.get("/api/visualization/data")
async def get_visualization_data(
    max_nodes: Optional[int] = 1000,
    layer: Optional[str] = None
):
    """Get data formatted for visualization"""
    if "network" not in analysis_state:
        raise HTTPException(status_code=404, detail="Network not built. Run analysis first.")
    
    network = analysis_state["network"]
    
    # Get the graph to visualize
    if layer and layer in network.layers:
        G = network.layers[layer]
    elif network.combined_graph:
        G = network.combined_graph
    else:
        raise HTTPException(status_code=404, detail="No graph available for visualization")
    
    # Limit nodes for performance
    if G.number_of_nodes() > max_nodes:
        # Get top nodes by degree
        degrees = dict(G.degree())
        top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:max_nodes]
        top_node_ids = [node for node, _ in top_nodes]
        G = G.subgraph(top_node_ids)
    
    # Convert to format for visualization
    nodes = []
    for node in G.nodes():
        node_data = {"id": str(node), "label": str(node)}
        
        # Add degree
        node_data["degree"] = G.degree(node)
        
        # Add community if available
        if "communities" in analysis_state:
            for comm_result in analysis_state["communities"].values():
                comm_map = comm_result.get("communities", {})
                if node in comm_map:
                    node_data["community"] = comm_map[node]
                    break
        
        nodes.append(node_data)
    
    edges = []
    for u, v, data in G.edges(data=True):
        edges.append({
            "source": str(u),
            "target": str(v),
            "weight": data.get("weight", 1)
        })
    
    return {
        "status": "success",
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "n_nodes": len(nodes),
            "n_edges": len(edges),
            "layer": layer or "combined"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# Background task function
async def run_full_analysis(
    analysis_id: str,
    sample_size: Optional[int],
    layers: Optional[List[str]],
    algorithms: Optional[List[str]]
):
    """Run the full analysis pipeline"""
    import pandas as pd
    
    try:
        analysis_state[analysis_id]["progress"] = 10
        analysis_state[analysis_id]["message"] = "Loading data..."
        
        # Step 1: Load data
        data = data_loader.load_dataset(sample_size)
        tweets_df = data_loader.preprocess_tweets(data['tweets'])
        
        analysis_state[analysis_id]["progress"] = 30
        analysis_state[analysis_id]["message"] = "Building network layers..."
        
        # Step 2: Build network
        edges_df = data_loader.get_user_network_edges(data)
        network_builder.build_layers(edges_df)
        network_builder.build_hashtag_layer(tweets_df)
        network_builder.combine_layers()
        
        analysis_state["network"] = network_builder
        
        analysis_state[analysis_id]["progress"] = 50
        analysis_state[analysis_id]["message"] = "Detecting communities..."
        
        # Step 3: Community detection
        communities = {}
        algorithms_to_run = algorithms or ["louvain", "leiden", "infomap"]
        
        for layer_name, layer_graph in network_builder.layers.items():
            if layers and layer_name not in layers:
                continue
            
            if "louvain" in algorithms_to_run:
                communities[f"{layer_name}_louvain"] = community_detector.detect_louvain(
                    layer_graph, layer_name
                )
            if "leiden" in algorithms_to_run:
                communities[f"{layer_name}_leiden"] = community_detector.detect_leiden(
                    layer_graph, layer_name
                )
            if "infomap" in algorithms_to_run:
                communities[f"{layer_name}_infomap"] = community_detector.detect_infomap(
                    layer_graph, layer_name
                )
        
        # Multi-layer detection
        if "multilayer" in (algorithms or []):
            communities["multilayer"] = community_detector.detect_multilayer(
                network_builder.layers
            )
        
        analysis_state["communities"] = communities
        
        analysis_state[analysis_id]["progress"] = 70
        analysis_state[analysis_id]["message"] = "Detecting coordinated behavior..."
        
        # Step 4: Coordination detection
        coordination_result = coordination_detector.detect_coordinated_accounts(
            tweets_df, edges_df
        )
        analysis_state["coordination"] = coordination_result
        
        analysis_state[analysis_id]["progress"] = 85
        analysis_state[analysis_id]["message"] = "Detecting misinformation clusters..."
        
        # Step 5: Misinformation detection
        main_communities = communities.get("combined_louvain") or list(communities.values())[0]
        misinfo_result = misinfo_detector.detect_misinformation_clusters(
            network_builder,
            tweets_df,
            data.get('claims', pd.DataFrame()),
            main_communities,
            coordination_result.get('coordinated_groups', [])
        )
        analysis_state["misinformation"] = misinfo_result
        
        analysis_state[analysis_id]["progress"] = 100
        analysis_state[analysis_id]["status"] = "completed"
        analysis_state[analysis_id]["message"] = "Analysis completed successfully"
        
        logger.info(f"Analysis {analysis_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error in analysis {analysis_id}: {e}")
        analysis_state[analysis_id]["status"] = "error"
        analysis_state[analysis_id]["message"] = str(e)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT, log_level="info")

