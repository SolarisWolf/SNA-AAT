"""
Community Detection Module
Implements various community detection algorithms for single and multi-layer networks
"""
import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Optional, Set
import logging
from collections import defaultdict

try:
    import igraph as ig
    IGRAPH_AVAILABLE = True
except ImportError:
    IGRAPH_AVAILABLE = False
    print("Warning: python-igraph not available. Some algorithms will use NetworkX alternatives.")

try:
    import cdlib
    from cdlib import algorithms, evaluation
    CDLIB_AVAILABLE = True
except ImportError:
    CDLIB_AVAILABLE = False
    print("Warning: cdlib not available. Some algorithms will be unavailable.")

from config import COMMUNITY_DETECTION_CONFIG
from utils.logger import setup_logger

logger = setup_logger(__name__)


class CommunityDetector:
    """Detect communities in single and multi-layer networks"""
    
    def __init__(self):
        self.config = COMMUNITY_DETECTION_CONFIG
        self.logger = setup_logger(self.__class__.__name__)
        self.communities: Dict[str, Dict] = {}
    
    def detect_louvain(self, G: nx.Graph, layer_name: str = "combined") -> Dict:
        """
        Detect communities using Louvain algorithm
        
        Args:
            G: NetworkX graph
            layer_name: Name of the layer
            
        Returns:
            Dictionary with community assignments
        """
        self.logger.info(f"Running Louvain algorithm on {layer_name}...")
        
        try:
            if CDLIB_AVAILABLE:
                # Convert to igraph if needed, or use cdlib directly
                communities = algorithms.louvain(G, weight='weight', 
                                                resolution=self.config['louvain']['resolution'],
                                                random_state=self.config['louvain']['random_state'])
                
                # Convert to node->community mapping
                community_map = {}
                for idx, community in enumerate(communities.communities):
                    for node in community:
                        community_map[node] = idx
                
                modularity = communities.modularity()
                
            else:
                # Fallback to networkx greedy_modularity_communities
                communities_generator = nx.community.greedy_modularity_communities(
                    G, weight='weight'
                )
                communities_list = list(communities_generator)
                
                community_map = {}
                for idx, community in enumerate(communities_list):
                    for node in community:
                        community_map[node] = idx
                
                # Calculate modularity
                modularity = nx.community.modularity(G, communities_list, weight='weight')
            
            result = {
                'algorithm': 'louvain',
                'layer': layer_name,
                'communities': community_map,
                'n_communities': len(set(community_map.values())),
                'modularity': float(modularity),
                'community_list': self._convert_to_community_list(community_map),
            }
            
            self.communities[f"{layer_name}_louvain"] = result
            self.logger.info(f"Found {result['n_communities']} communities with modularity {modularity:.4f}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in Louvain detection: {e}")
            return self._empty_result('louvain', layer_name)
    
    def detect_leiden(self, G: nx.Graph, layer_name: str = "combined") -> Dict:
        """
        Detect communities using Leiden algorithm
        
        Args:
            G: NetworkX graph
            layer_name: Name of the layer
            
        Returns:
            Dictionary with community assignments
        """
        self.logger.info(f"Running Leiden algorithm on {layer_name}...")
        
        try:
            if CDLIB_AVAILABLE:
                communities = algorithms.leiden(G, 
                                               resolution=self.config['leiden']['resolution'],
                                               random_state=self.config['leiden']['random_state'],
                                               n_iterations=self.config['leiden']['n_iterations'])
                
                community_map = {}
                for idx, community in enumerate(communities.communities):
                    for node in community:
                        community_map[node] = idx
                
                modularity = communities.modularity()
                
            else:
                # Fallback to Louvain if Leiden not available
                self.logger.warning("Leiden not available, using Louvain instead")
                return self.detect_louvain(G, layer_name)
            
            result = {
                'algorithm': 'leiden',
                'layer': layer_name,
                'communities': community_map,
                'n_communities': len(set(community_map.values())),
                'modularity': float(modularity),
                'community_list': self._convert_to_community_list(community_map),
            }
            
            self.communities[f"{layer_name}_leiden"] = result
            self.logger.info(f"Found {result['n_communities']} communities with modularity {modularity:.4f}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in Leiden detection: {e}")
            return self._empty_result('leiden', layer_name)
    
    def detect_infomap(self, G: nx.Graph, layer_name: str = "combined") -> Dict:
        """
        Detect communities using Infomap algorithm
        
        Args:
            G: NetworkX graph
            layer_name: Name of the layer
            
        Returns:
            Dictionary with community assignments
        """
        self.logger.info(f"Running Infomap algorithm on {layer_name}...")
        
        try:
            if CDLIB_AVAILABLE:
                communities = algorithms.infomap(G, trials=self.config['infomap']['trials'])
                
                community_map = {}
                for idx, community in enumerate(communities.communities):
                    for node in community:
                        community_map[node] = idx
                
                # Infomap doesn't use modularity, use code length instead
                code_length = communities.codelength if hasattr(communities, 'codelength') else None
                
            elif IGRAPH_AVAILABLE:
                # Use igraph's infomap
                ig_G = self._nx_to_igraph(G)
                communities_ig = ig_G.community_infomap(trials=self.config['infomap']['trials'])
                
                community_map = {}
                for idx, community in enumerate(communities_ig):
                    for node in community:
                        node_name = ig_G.vs[node]['name']
                        community_map[node_name] = idx
                
                code_length = communities_ig.codelength
                
            else:
                self.logger.warning("Infomap not available, using Louvain instead")
                return self.detect_louvain(G, layer_name)
            
            result = {
                'algorithm': 'infomap',
                'layer': layer_name,
                'communities': community_map,
                'n_communities': len(set(community_map.values())),
                'code_length': float(code_length) if code_length else None,
                'community_list': self._convert_to_community_list(community_map),
            }
            
            self.communities[f"{layer_name}_infomap"] = result
            self.logger.info(f"Found {result['n_communities']} communities")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in Infomap detection: {e}")
            return self._empty_result('infomap', layer_name)
    
    def detect_multilayer(self, layers: Dict[str, nx.Graph]) -> Dict:
        """
        Detect communities across multiple layers
        
        Args:
            layers: Dictionary of layer_name -> NetworkX graph
            
        Returns:
            Dictionary with multi-layer community assignments
        """
        self.logger.info("Running multi-layer community detection...")
        
        try:
            # Simple approach: detect communities in each layer and find overlaps
            layer_communities = {}
            
            for layer_name, G in layers.items():
                # Use Louvain on each layer
                result = self.detect_louvain(G, layer_name)
                layer_communities[layer_name] = result['communities']
            
            # Find overlapping communities
            overlap_communities = self._find_overlapping_communities(layer_communities)
            
            result = {
                'algorithm': 'multilayer',
                'layer': 'multilayer',
                'communities': overlap_communities,
                'n_communities': len(set(overlap_communities.values())),
                'layer_communities': layer_communities,
                'community_list': self._convert_to_community_list(overlap_communities),
            }
            
            self.communities['multilayer'] = result
            self.logger.info(f"Found {result['n_communities']} multi-layer communities")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in multi-layer detection: {e}")
            return self._empty_result('multilayer', 'multilayer')
    
    def _find_overlapping_communities(self, layer_communities: Dict[str, Dict]) -> Dict:
        """
        Find communities that overlap across layers
        
        Args:
            layer_communities: Dict of layer_name -> node->community mapping
            
        Returns:
            Combined community mapping
        """
        # Get all nodes
        all_nodes = set()
        for communities in layer_communities.values():
            all_nodes.update(communities.keys())
        
        # For each node, assign to community based on most common assignment
        node_community_votes = defaultdict(list)
        
        for layer_name, communities in layer_communities.items():
            for node, comm_id in communities.items():
                node_community_votes[node].append((comm_id, layer_name))
        
        # Assign nodes to communities
        final_communities = {}
        community_counter = 0
        node_to_community = {}
        
        for node, votes in node_community_votes.items():
            # Use most frequent community assignment
            comm_ids = [v[0] for v in votes]
            most_common = max(set(comm_ids), key=comm_ids.count)
            
            # Create unique community ID
            comm_key = (node, most_common)
            if comm_key not in node_to_community:
                node_to_community[comm_key] = community_counter
                community_counter += 1
            
            final_communities[node] = node_to_community[comm_key]
        
        return final_communities
    
    def _convert_to_community_list(self, community_map: Dict) -> List[List]:
        """Convert node->community mapping to list of communities"""
        communities_dict = defaultdict(list)
        for node, comm_id in community_map.items():
            communities_dict[comm_id].append(node)
        return list(communities_dict.values())
    
    def _nx_to_igraph(self, G: nx.Graph) -> 'ig.Graph':
        """Convert NetworkX graph to igraph"""
        if not IGRAPH_AVAILABLE:
            raise ImportError("igraph not available")
        
        # Create igraph graph
        ig_G = ig.Graph(directed=G.is_directed())
        ig_G.add_vertices(list(G.nodes()))
        
        # Add edges with weights
        edges = []
        weights = []
        for u, v, data in G.edges(data=True):
            edges.append((u, v))
            weights.append(data.get('weight', 1))
        
        ig_G.add_edges(edges)
        ig_G.es['weight'] = weights
        ig_G.vs['name'] = list(G.nodes())
        
        return ig_G
    
    def _empty_result(self, algorithm: str, layer_name: str) -> Dict:
        """Return empty result structure"""
        return {
            'algorithm': algorithm,
            'layer': layer_name,
            'communities': {},
            'n_communities': 0,
            'modularity': 0.0,
            'community_list': [],
        }
    
    def get_community_statistics(self, communities: Dict, G: nx.Graph) -> Dict:
        """Get statistics about detected communities"""
        community_list = self._convert_to_community_list(communities)
        
        stats = {
            'n_communities': len(community_list),
            'community_sizes': [len(comm) for comm in community_list],
            'avg_community_size': np.mean([len(comm) for comm in community_list]) if community_list else 0,
            'max_community_size': max([len(comm) for comm in community_list]) if community_list else 0,
            'min_community_size': min([len(comm) for comm in community_list]) if community_list else 0,
        }
        
        return stats

