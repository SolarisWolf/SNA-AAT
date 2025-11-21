"""
Misinformation Detection Module
Identifies misinformation clusters using graph features and veracity scores
"""
import pandas as pd
import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict
import logging

from config import MISINFO_CONFIG
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MisinformationDetector:
    """Detect misinformation clusters in social networks"""
    
    def __init__(self):
        self.config = MISINFO_CONFIG
        self.logger = setup_logger(self.__class__.__name__)
        self.misinfo_clusters: List[Dict] = []
    
    def detect_misinformation_clusters(self, 
                                     network: 'MultiLayerNetwork',
                                     tweets_df: pd.DataFrame,
                                     claims_df: pd.DataFrame,
                                     communities: Dict,
                                     coordinated_groups: List[Dict]) -> Dict:
        """
        Detect misinformation clusters using multiple indicators
        
        Args:
            network: MultiLayerNetwork object
            tweets_df: DataFrame with tweet data and veracity scores
            claims_df: DataFrame with claim veracity information
            communities: Community detection results
            coordinated_groups: Coordinated behavior groups
            
        Returns:
            Dictionary with misinformation clusters and scores
        """
        self.logger.info("Detecting misinformation clusters...")
        
        clusters = []
        
        # Indicator 1: Low veracity scores
        veracity_clusters = self._detect_low_veracity_clusters(
            network, tweets_df, communities
        )
        clusters.extend(veracity_clusters)
        
        # Indicator 2: Rapid spread patterns
        spread_clusters = self._detect_rapid_spread_clusters(
            network, tweets_df
        )
        clusters.extend(spread_clusters)
        
        # Indicator 3: Coordinated misinformation
        coord_misinfo = self._detect_coordinated_misinformation(
            coordinated_groups, tweets_df
        )
        clusters.extend(coord_misinfo)
        
        # Indicator 4: Structural anomalies
        anomaly_clusters = self._detect_structural_anomalies(
            network, communities
        )
        clusters.extend(anomaly_clusters)
        
        # Indicator 5: Bot-like behavior patterns
        bot_clusters = self._detect_bot_clusters(network, tweets_df)
        clusters.extend(bot_clusters)
        
        # Combine and rank clusters
        ranked_clusters = self._rank_misinformation_clusters(clusters)
        
        result = {
            'misinfo_clusters': ranked_clusters,
            'n_clusters': len(ranked_clusters),
            'high_risk_clusters': [
                c for c in ranked_clusters 
                if c.get('risk_score', 0) >= 0.7
            ],
        }
        
        self.misinfo_clusters = ranked_clusters
        self.logger.info(f"Detected {result['n_clusters']} misinformation clusters")
        
        return result
    
    def _detect_low_veracity_clusters(self, 
                                     network: 'MultiLayerNetwork',
                                     tweets_df: pd.DataFrame,
                                     communities: Dict) -> List[Dict]:
        """
        Detect clusters with low veracity scores
        
        Returns:
            List of clusters with low veracity
        """
        self.logger.info("Analyzing veracity scores...")
        
        clusters = []
        
        if 'veracity_score' not in tweets_df.columns:
            return clusters
        
        # Get veracity threshold
        threshold = self.config['veracity_threshold']
        
        # Group tweets by community
        if isinstance(communities, dict) and 'communities' in communities:
            community_map = communities['communities']
        else:
            community_map = communities
        
        # Calculate average veracity per community
        community_veracity = defaultdict(list)
        
        for _, tweet in tweets_df.iterrows():
            user_id = tweet['user_id']
            if user_id in community_map:
                comm_id = community_map[user_id]
                veracity = tweet.get('veracity_score', 0.5)
                community_veracity[comm_id].append(veracity)
        
        # Identify low veracity communities
        for comm_id, veracity_scores in community_veracity.items():
            avg_veracity = np.mean(veracity_scores)
            
            if avg_veracity <= threshold:
                # Get all nodes in this community
                community_nodes = [
                    node for node, cid in community_map.items() 
                    if cid == comm_id
                ]
                
                if len(community_nodes) >= self.config['cluster_size_threshold']:
                    clusters.append({
                        'cluster_id': f"veracity_{comm_id}",
                        'nodes': community_nodes,
                        'avg_veracity': float(avg_veracity),
                        'n_nodes': len(community_nodes),
                        'indicator': 'low_veracity',
                        'risk_score': 1 - avg_veracity,  # Higher risk for lower veracity
                    })
        
        return clusters
    
    def _detect_rapid_spread_clusters(self, 
                                     network: 'MultiLayerNetwork',
                                     tweets_df: pd.DataFrame) -> List[Dict]:
        """
        Detect clusters with rapid information spread
        
        Returns:
            List of clusters with rapid spread patterns
        """
        self.logger.info("Analyzing spread velocity...")
        
        clusters = []
        
        if 'timestamp' not in tweets_df.columns:
            tweets_df['timestamp'] = pd.to_datetime(tweets_df['created_at']).astype('int64') // 10**9
        
        # Group by URL or hashtag to track spread
        spread_velocity = {}
        
        for _, tweet in tweets_df.iterrows():
            # Check URLs
            urls = tweet.get('urls', [])
            hashtags = tweet.get('hashtags', [])
            
            content_id = None
            if urls and isinstance(urls, list):
                content_id = urls[0]  # Use first URL
            elif hashtags and isinstance(hashtags, list):
                content_id = hashtags[0]  # Use first hashtag
            
            if content_id:
                if content_id not in spread_velocity:
                    spread_velocity[content_id] = {
                        'timestamps': [],
                        'users': [],
                        'tweet_ids': [],
                    }
                
                spread_velocity[content_id]['timestamps'].append(tweet['timestamp'])
                spread_velocity[content_id]['users'].append(tweet['user_id'])
                spread_velocity[content_id]['tweet_ids'].append(tweet['tweet_id'])
        
        # Calculate spread velocity
        threshold = self.config['spread_velocity_threshold']
        
        for content_id, data in spread_velocity.items():
            if len(data['timestamps']) < self.config['cluster_size_threshold']:
                continue
            
            timestamps = np.array(data['timestamps'])
            time_span = max(timestamps) - min(timestamps)
            n_shares = len(timestamps)
            
            if time_span > 0:
                velocity = n_shares / time_span  # Shares per second
            else:
                velocity = float('inf')
            
            if velocity >= threshold:
                clusters.append({
                    'cluster_id': f"spread_{content_id}",
                    'nodes': list(set(data['users'])),
                    'content_id': content_id,
                    'spread_velocity': float(velocity),
                    'n_shares': n_shares,
                    'time_span': int(time_span),
                    'indicator': 'rapid_spread',
                    'risk_score': min(1.0, velocity / 10.0),  # Normalize
                })
        
        return clusters
    
    def _detect_coordinated_misinformation(self, 
                                          coordinated_groups: List[Dict],
                                          tweets_df: pd.DataFrame) -> List[Dict]:
        """
        Detect coordinated groups spreading misinformation
        
        Returns:
            List of coordinated misinformation clusters
        """
        self.logger.info("Analyzing coordinated misinformation...")
        
        clusters = []
        
        if 'veracity_score' not in tweets_df.columns:
            return clusters
        
        threshold = self.config['veracity_threshold']
        
        for group in coordinated_groups:
            accounts = group.get('accounts', [])
            
            # Get tweets from these accounts
            group_tweets = tweets_df[tweets_df['user_id'].isin(accounts)]
            
            if len(group_tweets) > 0:
                avg_veracity = group_tweets['veracity_score'].mean()
                
                if avg_veracity <= threshold:
                    clusters.append({
                        'cluster_id': f"coord_misinfo_{len(clusters)}",
                        'nodes': accounts,
                        'avg_veracity': float(avg_veracity),
                        'n_nodes': len(accounts),
                        'coordination_signals': group.get('signals', []),
                        'confidence': group.get('confidence_score', 0),
                        'indicator': 'coordinated_misinformation',
                        'risk_score': (1 - avg_veracity) * group.get('confidence_score', 0.5),
                    })
        
        return clusters
    
    def _detect_structural_anomalies(self, 
                                    network: 'MultiLayerNetwork',
                                    communities: Dict) -> List[Dict]:
        """
        Detect structural anomalies indicating suspicious behavior
        
        Returns:
            List of clusters with structural anomalies
        """
        self.logger.info("Analyzing structural anomalies...")
        
        clusters = []
        
        if not network.combined_graph:
            return clusters
        
        G = network.combined_graph
        
        # Get community mapping
        if isinstance(communities, dict) and 'communities' in communities:
            community_map = communities['communities']
        else:
            community_map = communities
        
        # Calculate structural metrics per community
        community_metrics = defaultdict(lambda: {
            'nodes': [],
            'degrees': [],
            'clustering': [],
            'betweenness': [],
        })
        
        for node in G.nodes():
            if node in community_map:
                comm_id = community_map[node]
                community_metrics[comm_id]['nodes'].append(node)
                community_metrics[comm_id]['degrees'].append(G.degree(node))
        
        # Calculate clustering coefficients
        clustering = nx.clustering(G.to_undirected() if G.is_directed() else G)
        
        # Identify anomalous communities
        for comm_id, metrics in community_metrics.items():
            if len(metrics['nodes']) < self.config['cluster_size_threshold']:
                continue
            
            # High clustering but low reciprocity (suspicious)
            avg_degree = np.mean(metrics['degrees'])
            avg_clustering = np.mean([clustering.get(node, 0) for node in metrics['nodes']])
            
            # Calculate reciprocity for directed graphs
            if G.is_directed():
                reciprocity_scores = []
                for node in metrics['nodes']:
                    if node in G:
                        successors = list(G.successors(node))
                        predecessors = list(G.predecessors(node))
                        if successors:
                            reciprocal = len(set(successors) & set(predecessors))
                            reciprocity_scores.append(reciprocal / len(successors))
                
                avg_reciprocity = np.mean(reciprocity_scores) if reciprocity_scores else 0
                
                # Anomaly: high clustering, low reciprocity
                if avg_clustering > 0.5 and avg_reciprocity < 0.2:
                    anomaly_score = avg_clustering * (1 - avg_reciprocity)
                    
                    if anomaly_score >= self.config['structural_anomaly_threshold']:
                        clusters.append({
                            'cluster_id': f"anomaly_{comm_id}",
                            'nodes': metrics['nodes'],
                            'avg_clustering': float(avg_clustering),
                            'avg_reciprocity': float(avg_reciprocity),
                            'anomaly_score': float(anomaly_score),
                            'n_nodes': len(metrics['nodes']),
                            'indicator': 'structural_anomaly',
                            'risk_score': float(anomaly_score),
                        })
        
        return clusters
    
    def _detect_bot_clusters(self, 
                            network: 'MultiLayerNetwork',
                            tweets_df: pd.DataFrame) -> List[Dict]:
        """
        Detect bot-like behavior clusters
        
        Returns:
            List of bot-like clusters
        """
        self.logger.info("Analyzing bot-like patterns...")
        
        clusters = []
        
        if not network.combined_graph:
            return clusters
        
        G = network.combined_graph
        
        # Bot indicators: high activity, low diversity, star patterns
        bot_scores = {}
        
        for node in G.nodes():
            # Get user's tweets
            user_tweets = tweets_df[tweets_df['user_id'] == node]
            
            if len(user_tweets) == 0:
                continue
            
            # Calculate bot score
            activity = len(user_tweets)
            in_degree = G.in_degree(node)
            out_degree = G.out_degree(node)
            
            # Star pattern: many incoming, few outgoing
            star_score = in_degree / (out_degree + 1) if out_degree > 0 else in_degree
            
            # Content diversity (hashtag diversity)
            hashtags = []
            for _, tweet in user_tweets.iterrows():
                tweet_hashtags = tweet.get('hashtags', [])
                if isinstance(tweet_hashtags, list):
                    hashtags.extend(tweet_hashtags)
            
            hashtag_diversity = len(set(hashtags)) / (len(hashtags) + 1)
            
            # Combined bot score
            bot_score = (star_score / 10.0) * (1 - hashtag_diversity) * min(1.0, activity / 100)
            bot_scores[node] = bot_score
        
        # Find clusters of high bot scores
        threshold = self.config['bot_score_threshold']
        high_bot_nodes = [node for node, score in bot_scores.items() if score >= threshold]
        
        if len(high_bot_nodes) >= self.config['cluster_size_threshold']:
            # Find connected components of bot nodes
            bot_subgraph = G.subgraph(high_bot_nodes)
            components = list(nx.weakly_connected_components(bot_subgraph))
            
            for idx, component in enumerate(components):
                if len(component) >= self.config['cluster_size_threshold']:
                    avg_bot_score = np.mean([bot_scores[node] for node in component])
                    
                    clusters.append({
                        'cluster_id': f"bot_{idx}",
                        'nodes': list(component),
                        'avg_bot_score': float(avg_bot_score),
                        'n_nodes': len(component),
                        'indicator': 'bot_like',
                        'risk_score': float(avg_bot_score),
                    })
        
        return clusters
    
    def _rank_misinformation_clusters(self, clusters: List[Dict]) -> List[Dict]:
        """
        Rank clusters by risk score and remove duplicates
        
        Args:
            clusters: List of cluster dictionaries
            
        Returns:
            Ranked and deduplicated clusters
        """
        # Remove duplicates based on node overlap
        unique_clusters = []
        seen_nodes = set()
        
        # Sort by risk score (descending)
        clusters_sorted = sorted(clusters, key=lambda x: x.get('risk_score', 0), reverse=True)
        
        for cluster in clusters_sorted:
            nodes = set(cluster.get('nodes', []))
            
            # Check overlap with existing clusters
            overlap = False
            for existing in unique_clusters:
                existing_nodes = set(existing.get('nodes', []))
                jaccard = len(nodes & existing_nodes) / len(nodes | existing_nodes) if (nodes | existing_nodes) else 0
                
                if jaccard > 0.5:  # High overlap
                    overlap = True
                    # Merge if this cluster has higher risk
                    if cluster.get('risk_score', 0) > existing.get('risk_score', 0):
                        unique_clusters.remove(existing)
                        unique_clusters.append(cluster)
                    break
            
            if not overlap:
                unique_clusters.append(cluster)
        
        # Re-sort by risk score
        unique_clusters = sorted(unique_clusters, key=lambda x: x.get('risk_score', 0), reverse=True)
        
        return unique_clusters

