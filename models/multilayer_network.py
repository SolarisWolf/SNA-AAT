"""
Multi-Layer Network Construction Module
Builds and manages multi-layer social network graphs
"""
import networkx as nx
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict
import logging

from config import LAYER_CONFIG
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MultiLayerNetwork:
    """Manages multi-layer network construction and operations"""
    
    def __init__(self):
        self.layers: Dict[str, nx.Graph] = {}
        self.combined_graph: Optional[nx.Graph] = None
        self.layer_config = LAYER_CONFIG
        self.logger = setup_logger(self.__class__.__name__)
    
    def build_layers(self, edges_df: pd.DataFrame) -> Dict[str, nx.Graph]:
        """
        Build network layers from edge dataframe
        
        Args:
            edges_df: DataFrame with columns: source, target, layer, weight, timestamp
            
        Returns:
            Dictionary of layer_name -> NetworkX graph
        """
        self.logger.info("Building multi-layer network...")
        
        # Group edges by layer
        for layer_name, layer_config in self.layer_config.items():
            if not layer_config.get("enabled", True):
                continue
            
            layer_edges = edges_df[edges_df['layer'] == layer_name].copy()
            
            if layer_edges.empty:
                self.logger.warning(f"No edges found for layer: {layer_name}")
                continue
            
            # Create graph
            is_directed = layer_config.get("directed", True)
            G = nx.DiGraph() if is_directed else nx.Graph()
            
            # Add edges with weights
            for _, edge in layer_edges.iterrows():
                source = str(edge['source'])
                target = str(edge['target'])
                weight = edge.get('weight', 1)
                
                if weight >= layer_config.get("weight_threshold", 1):
                    if G.has_edge(source, target):
                        G[source][target]['weight'] += weight
                    else:
                        G.add_edge(source, target, weight=weight)
            
            # Add node attributes if available
            self._add_node_attributes(G, layer_edges)
            
            self.layers[layer_name] = G
            self.logger.info(f"Layer '{layer_name}': {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        
        return self.layers
    
    def _add_node_attributes(self, G: nx.Graph, edges_df: pd.DataFrame):
        """Add node attributes from edge data"""
        # Extract unique nodes and their first appearance
        all_nodes = set(edges_df['source'].unique()) | set(edges_df['target'].unique())
        
        for node in all_nodes:
            if node not in G:
                G.add_node(node)
    
    def build_hashtag_layer(self, tweets_df: pd.DataFrame) -> nx.Graph:
        """
        Build hashtag co-occurrence layer
        
        Args:
            tweets_df: DataFrame with 'hashtags' column (list of hashtags)
            
        Returns:
            NetworkX graph of hashtag co-occurrences
        """
        self.logger.info("Building hashtag co-occurrence layer...")
        
        hashtag_config = self.layer_config.get("hashtag", {})
        G = nx.Graph()  # Undirected for co-occurrence
        
        # Count co-occurrences
        cooccurrence = defaultdict(int)
        
        for _, tweet in tweets_df.iterrows():
            hashtags = tweet.get('hashtags', [])
            if isinstance(hashtags, list) and len(hashtags) > 1:
                # Normalize hashtags
                hashtags = [h.lower().strip('#') for h in hashtags if h]
                # Count all pairs
                for i, h1 in enumerate(hashtags):
                    for h2 in hashtags[i+1:]:
                        pair = tuple(sorted([h1, h2]))
                        cooccurrence[pair] += 1
        
        # Add edges above threshold
        threshold = hashtag_config.get("weight_threshold", 2)
        for (h1, h2), weight in cooccurrence.items():
            if weight >= threshold:
                G.add_edge(h1, h2, weight=weight)
        
        self.layers['hashtag'] = G
        self.logger.info(f"Hashtag layer: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        
        return G
    
    def combine_layers(self, method: str = "union") -> nx.Graph:
        """
        Combine multiple layers into a single graph
        
        Args:
            method: 'union' (all edges) or 'intersection' (edges in all layers)
            
        Returns:
            Combined NetworkX graph
        """
        self.logger.info(f"Combining layers using {method} method...")
        
        if not self.layers:
            raise ValueError("No layers available. Build layers first.")
        
        if method == "union":
            G = nx.DiGraph()
            
            # Add all nodes and edges from all layers
            for layer_name, layer_graph in self.layers.items():
                G.add_nodes_from(layer_graph.nodes(data=True))
                G.add_edges_from(layer_graph.edges(data=True))
            
            # Aggregate edge weights if multiple layers have same edge
            edge_weights = defaultdict(float)
            for layer_name, layer_graph in self.layers.items():
                for u, v, data in layer_graph.edges(data=True):
                    weight = data.get('weight', 1)
                    edge_weights[(u, v)] += weight
            
            # Update edge weights
            for (u, v), weight in edge_weights.items():
                if G.has_edge(u, v):
                    G[u][v]['weight'] = weight
        
        elif method == "intersection":
            # Only edges that exist in all layers
            common_edges = None
            for layer_graph in self.layers.values():
                layer_edges = set(layer_graph.edges())
                if common_edges is None:
                    common_edges = layer_edges
                else:
                    common_edges &= layer_edges
            
            G = nx.DiGraph()
            for u, v in common_edges:
                # Sum weights across layers
                weight = sum(self.layers[layer].get_edge_data(u, v, {}).get('weight', 1) 
                           for layer in self.layers if self.layers[layer].has_edge(u, v))
                G.add_edge(u, v, weight=weight)
        
        else:
            raise ValueError(f"Unknown combination method: {method}")
        
        self.combined_graph = G
        self.logger.info(f"Combined graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        
        return G
    
    def get_layer_statistics(self) -> Dict[str, Dict]:
        """Get statistics for each layer"""
        stats = {}
        
        for layer_name, G in self.layers.items():
            stats[layer_name] = {
                'nodes': G.number_of_nodes(),
                'edges': G.number_of_edges(),
                'density': nx.density(G),
                'is_directed': G.is_directed(),
                'is_connected': nx.is_weakly_connected(G) if G.is_directed() else nx.is_connected(G),
            }
            
            if G.number_of_nodes() > 0:
                degrees = dict(G.degree())
                stats[layer_name]['avg_degree'] = np.mean(list(degrees.values()))
                stats[layer_name]['max_degree'] = max(degrees.values())
        
        if self.combined_graph:
            G = self.combined_graph
            stats['combined'] = {
                'nodes': G.number_of_nodes(),
                'edges': G.number_of_edges(),
                'density': nx.density(G),
            }
        
        return stats
    
    def get_node_attributes(self, node_id: str) -> Dict:
        """Get attributes of a node across all layers"""
        attributes = {
            'node_id': node_id,
            'layers': [],
            'degrees': {},
            'neighbors': {},
        }
        
        for layer_name, G in self.layers.items():
            if node_id in G:
                attributes['layers'].append(layer_name)
                attributes['degrees'][layer_name] = G.degree(node_id)
                if G.is_directed():
                    attributes['neighbors'][layer_name] = {
                        'in': list(G.predecessors(node_id)),
                        'out': list(G.successors(node_id)),
                    }
                else:
                    attributes['neighbors'][layer_name] = list(G.neighbors(node_id))
        
        return attributes

