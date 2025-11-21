"""
Coordinated Behavior Detection Module
Detects coordinated accounts using temporal and structural patterns
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Set, Optional
from collections import defaultdict
from datetime import datetime, timedelta
import logging
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import networkx as nx

from config import COORDINATION_CONFIG
from utils.logger import setup_logger

logger = setup_logger(__name__)


class CoordinationDetector:
    """Detect coordinated behavior patterns in social media networks"""
    
    def __init__(self):
        self.config = COORDINATION_CONFIG
        self.logger = setup_logger(self.__class__.__name__)
        self.coordinated_groups: List[Dict] = []
    
    def detect_coordinated_accounts(self, tweets_df: pd.DataFrame, 
                                   edges_df: pd.DataFrame) -> Dict:
        """
        Detect coordinated accounts using multiple signals
        
        Args:
            tweets_df: DataFrame with tweet data
            edges_df: DataFrame with network edges
            
        Returns:
            Dictionary with coordinated groups and scores
        """
        self.logger.info("Detecting coordinated accounts...")
        
        coordinated_accounts = set()
        coordination_signals = []
        
        # Signal 1: Temporal synchronization
        temporal_groups = self._detect_temporal_synchronization(tweets_df)
        coordination_signals.append(('temporal', temporal_groups))
        
        # Signal 2: Content similarity
        content_groups = self._detect_content_similarity(tweets_df)
        coordination_signals.append(('content', content_groups))
        
        # Signal 3: Hashtag coordination
        hashtag_groups = self._detect_hashtag_coordination(tweets_df)
        coordination_signals.append(('hashtag', hashtag_groups))
        
        # Signal 4: URL sharing patterns
        url_groups = self._detect_url_sharing(tweets_df)
        coordination_signals.append(('url', url_groups))
        
        # Signal 5: Structural patterns
        structural_groups = self._detect_structural_patterns(edges_df)
        coordination_signals.append(('structural', structural_groups))
        
        # Combine signals
        coordinated_groups = self._combine_coordination_signals(
            coordination_signals, tweets_df
        )
        
        result = {
            'coordinated_groups': coordinated_groups,
            'n_groups': len(coordinated_groups),
            'n_accounts': len(coordinated_accounts),
            'signals': {
                signal_name: len(groups) 
                for signal_name, groups in coordination_signals
            },
        }
        
        self.coordinated_groups = coordinated_groups
        self.logger.info(f"Detected {result['n_groups']} coordinated groups")
        
        return result
    
    def _detect_temporal_synchronization(self, tweets_df: pd.DataFrame) -> List[Dict]:
        """
        Detect accounts posting at synchronized times
        
        Returns:
            List of coordinated groups with temporal patterns
        """
        self.logger.info("Analyzing temporal synchronization...")
        
        # Ensure timestamp column exists
        if 'timestamp' not in tweets_df.columns:
            if 'created_at' in tweets_df.columns:
                tweets_df = tweets_df.copy()
                tweets_df['timestamp'] = pd.to_datetime(tweets_df['created_at']).astype('int64') // 10**9
            else:
                self.logger.warning("No timestamp information available")
                return []
        
        window_seconds = self.config['temporal_window']
        groups = []
        
        # Group tweets by time windows
        tweets_df = tweets_df.copy()
        tweets_df['time_window'] = tweets_df['timestamp'] // window_seconds
        
        # Find accounts posting in same time windows
        for time_window, window_tweets in tweets_df.groupby('time_window'):
            if len(window_tweets) < self.config['min_coordinated_accounts']:
                continue
            
            accounts = window_tweets['user_id'].unique()
            if len(accounts) >= self.config['min_coordinated_accounts']:
                # Check synchronization score
                timestamps = window_tweets.groupby('user_id')['timestamp'].apply(list)
                sync_score = self._calculate_sync_score(timestamps)
                
                if sync_score >= self.config['synchronization_threshold']:
                    groups.append({
                        'accounts': list(accounts),
                        'time_window': int(time_window),
                        'sync_score': sync_score,
                        'n_tweets': len(window_tweets),
                        'signal': 'temporal',
                    })
        
        return groups
    
    def _calculate_sync_score(self, timestamps_dict: Dict) -> float:
        """Calculate synchronization score for a group of accounts"""
        if len(timestamps_dict) < 2:
            return 0.0
        
        # Calculate variance in posting times
        all_timestamps = []
        for account, times in timestamps_dict.items():
            all_timestamps.extend(times)
        
        if len(all_timestamps) < 2:
            return 0.0
        
        # Lower variance = higher synchronization
        variance = np.var(all_timestamps)
        # Normalize to 0-1 scale (inverse relationship)
        max_variance = 3600  # 1 hour
        sync_score = max(0, 1 - (variance / max_variance))
        
        return sync_score
    
    def _detect_content_similarity(self, tweets_df: pd.DataFrame) -> List[Dict]:
        """
        Detect accounts posting similar content
        
        Returns:
            List of coordinated groups with similar content
        """
        self.logger.info("Analyzing content similarity...")
        
        # Filter tweets with text
        text_tweets = tweets_df[tweets_df['text'].notna()].copy()
        if len(text_tweets) < 2:
            return []
        
        # Vectorize tweets
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        try:
            tfidf_matrix = vectorizer.fit_transform(text_tweets['text'].astype(str))
        except:
            return []
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        threshold = self.config['text_similarity_threshold']
        groups = []
        processed_pairs = set()
        
        # Find similar tweet pairs
        for i in range(len(text_tweets)):
            for j in range(i+1, len(text_tweets)):
                if similarity_matrix[i, j] >= threshold:
                    tweet_i = text_tweets.iloc[i]
                    tweet_j = text_tweets.iloc[j]
                    
                    account_i = tweet_i['user_id']
                    account_j = tweet_j['user_id']
                    
                    if account_i != account_j:
                        pair = tuple(sorted([account_i, account_j]))
                        if pair not in processed_pairs:
                            processed_pairs.add(pair)
                            
                            # Find or create group
                            group_found = False
                            for group in groups:
                                if account_i in group['accounts'] or account_j in group['accounts']:
                                    if account_i not in group['accounts']:
                                        group['accounts'].append(account_i)
                                    if account_j not in group['accounts']:
                                        group['accounts'].append(account_j)
                                    group['similarity_scores'].append(similarity_matrix[i, j])
                                    group_found = True
                                    break
                            
                            if not group_found:
                                groups.append({
                                    'accounts': [account_i, account_j],
                                    'similarity_scores': [similarity_matrix[i, j]],
                                    'signal': 'content',
                                })
        
        # Calculate average similarity for each group
        for group in groups:
            group['avg_similarity'] = np.mean(group['similarity_scores'])
            del group['similarity_scores']
        
        # Filter groups by minimum size
        groups = [g for g in groups if len(g['accounts']) >= self.config['min_coordinated_accounts']]
        
        return groups
    
    def _detect_hashtag_coordination(self, tweets_df: pd.DataFrame) -> List[Dict]:
        """
        Detect accounts using same hashtags simultaneously
        
        Returns:
            List of coordinated groups with hashtag patterns
        """
        self.logger.info("Analyzing hashtag coordination...")
        
        # Filter tweets with hashtags
        hashtag_tweets = tweets_df[tweets_df['hashtags'].notna()].copy()
        hashtag_tweets = hashtag_tweets[hashtag_tweets['hashtags'].apply(
            lambda x: isinstance(x, list) and len(x) > 0
        )]
        
        if len(hashtag_tweets) < 2:
            return []
        
        groups = []
        
        # Group by time windows
        if 'timestamp' not in hashtag_tweets.columns:
            hashtag_tweets['timestamp'] = pd.to_datetime(hashtag_tweets['created_at']).astype('int64') // 10**9
        
        hashtag_tweets['time_window'] = hashtag_tweets['timestamp'] // self.config['temporal_window']
        
        # Find accounts using same hashtags in same time windows
        for time_window, window_tweets in hashtag_tweets.groupby('time_window'):
            if len(window_tweets) < self.config['min_coordinated_accounts']:
                continue
            
            # Calculate Jaccard similarity for hashtag sets
            account_hashtags = {}
            for _, tweet in window_tweets.iterrows():
                account = tweet['user_id']
                hashtags = set(tweet['hashtags'])
                if account not in account_hashtags:
                    account_hashtags[account] = set()
                account_hashtags[account].update(hashtags)
            
            # Find accounts with high hashtag overlap
            accounts = list(account_hashtags.keys())
            for i, acc_i in enumerate(accounts):
                for acc_j in accounts[i+1:]:
                    jaccard = self._jaccard_similarity(
                        account_hashtags[acc_i], 
                        account_hashtags[acc_j]
                    )
                    
                    if jaccard >= self.config['hashtag_jaccard_threshold']:
                        # Add to group
                        group_found = False
                        for group in groups:
                            if acc_i in group['accounts'] or acc_j in group['accounts']:
                                if acc_i not in group['accounts']:
                                    group['accounts'].append(acc_i)
                                if acc_j not in group['accounts']:
                                    group['accounts'].append(acc_j)
                                group['jaccard_scores'].append(jaccard)
                                group_found = True
                                break
                        
                        if not group_found:
                            groups.append({
                                'accounts': [acc_i, acc_j],
                                'jaccard_scores': [jaccard],
                                'time_window': int(time_window),
                                'signal': 'hashtag',
                            })
        
        # Calculate average Jaccard for each group
        for group in groups:
            group['avg_jaccard'] = np.mean(group['jaccard_scores'])
            del group['jaccard_scores']
        
        # Filter by minimum size
        groups = [g for g in groups if len(g['accounts']) >= self.config['min_coordinated_accounts']]
        
        return groups
    
    def _jaccard_similarity(self, set1: Set, set2: Set) -> float:
        """Calculate Jaccard similarity between two sets"""
        if not set1 and not set2:
            return 1.0
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0
    
    def _detect_url_sharing(self, tweets_df: pd.DataFrame) -> List[Dict]:
        """
        Detect accounts sharing same URLs rapidly
        
        Returns:
            List of coordinated groups sharing URLs
        """
        self.logger.info("Analyzing URL sharing patterns...")
        
        # Filter tweets with URLs
        url_tweets = tweets_df[tweets_df['urls'].notna()].copy()
        url_tweets = url_tweets[url_tweets['urls'].apply(
            lambda x: isinstance(x, list) and len(x) > 0
        )]
        
        if len(url_tweets) < 2:
            return []
        
        groups = []
        
        # Group by URL
        for url_list in url_tweets['urls']:
            for url in url_list:
                url_tweets_subset = url_tweets[
                    url_tweets['urls'].apply(lambda x: url in x if isinstance(x, list) else False)
                ]
                
                if len(url_tweets_subset) >= self.config['min_coordinated_accounts']:
                    accounts = url_tweets_subset['user_id'].unique()
                    
                    if len(accounts) >= self.config['min_coordinated_accounts']:
                        # Check temporal clustering
                        timestamps = url_tweets_subset['timestamp'].values
                        if len(timestamps) > 1:
                            time_span = max(timestamps) - min(timestamps)
                            # Rapid sharing = within short time span
                            if time_span < 3600:  # Within 1 hour
                                groups.append({
                                    'accounts': list(accounts),
                                    'url': url,
                                    'n_shares': len(url_tweets_subset),
                                    'time_span': int(time_span),
                                    'signal': 'url',
                                })
        
        # Remove duplicates
        unique_groups = []
        seen_accounts = set()
        for group in groups:
            account_tuple = tuple(sorted(group['accounts']))
            if account_tuple not in seen_accounts:
                unique_groups.append(group)
                seen_accounts.add(account_tuple)
        
        return unique_groups
    
    def _detect_structural_patterns(self, edges_df: pd.DataFrame) -> List[Dict]:
        """
        Detect structural patterns indicating coordination
        
        Returns:
            List of coordinated groups with structural patterns
        """
        self.logger.info("Analyzing structural patterns...")
        
        if edges_df.empty:
            return []
        
        # Build graph
        G = nx.DiGraph()
        for _, edge in edges_df.iterrows():
            G.add_edge(edge['source'], edge['target'], weight=edge.get('weight', 1))
        
        groups = []
        
        # Detect star-shaped clusters (bot-like behavior)
        # High in-degree, low out-degree nodes
        in_degrees = dict(G.in_degree())
        out_degrees = dict(G.out_degree())
        
        for node in G.nodes():
            in_deg = in_degrees.get(node, 0)
            out_deg = out_degrees.get(node, 0)
            
            # Star pattern: many incoming edges, few outgoing
            if in_deg > 10 and out_deg < 3:
                # Get neighbors
                predecessors = list(G.predecessors(node))
                if len(predecessors) >= self.config['min_coordinated_accounts']:
                    groups.append({
                        'accounts': predecessors + [node],
                        'center_node': node,
                        'in_degree': in_deg,
                        'out_degree': out_deg,
                        'signal': 'structural_star',
                    })
        
        return groups
    
    def _combine_coordination_signals(self, signals: List[Tuple[str, List[Dict]]], 
                                     tweets_df: pd.DataFrame) -> List[Dict]:
        """
        Combine multiple coordination signals to identify high-confidence groups
        
        Args:
            signals: List of (signal_name, groups) tuples
            tweets_df: Tweet dataframe for additional context
            
        Returns:
            Combined coordinated groups with confidence scores
        """
        # Build account -> signals mapping
        account_signals = defaultdict(list)
        
        for signal_name, groups in signals:
            for group in groups:
                accounts = group.get('accounts', [])
                for account in accounts:
                    account_signals[account].append({
                        'signal': signal_name,
                        'group': group,
                    })
        
        # Find accounts appearing in multiple signals
        high_confidence_accounts = {
            acc: sigs for acc, sigs in account_signals.items() 
            if len(sigs) >= 2  # Appears in at least 2 signals
        }
        
        # Build combined groups
        combined_groups = []
        processed_accounts = set()
        
        for account, signals_list in high_confidence_accounts.items():
            if account in processed_accounts:
                continue
            
            # Find all accounts connected through multiple signals
            group_accounts = {account}
            group_signals = set()
            
            for sig_info in signals_list:
                group_signals.add(sig_info['signal'])
                group_accounts.update(sig_info['group'].get('accounts', []))
            
            # Calculate confidence score
            confidence = len(group_signals) / len(signals)  # Fraction of signals
            
            if len(group_accounts) >= self.config['min_coordinated_accounts']:
                combined_groups.append({
                    'accounts': list(group_accounts),
                    'signals': list(group_signals),
                    'confidence_score': confidence,
                    'n_signals': len(group_signals),
                })
                
                processed_accounts.update(group_accounts)
        
        return combined_groups

