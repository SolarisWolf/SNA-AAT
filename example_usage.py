"""
Example usage script for the Multi-Layer Network Analysis API
Demonstrates how to interact with the backend API
"""
import requests
import time
import json

API_BASE_URL = "http://localhost:8000"


def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(json.dumps(response, indent=2))


def main():
    """Example workflow"""
    
    print("Multi-Layer Network Analysis API - Example Usage")
    print("=" * 60)
    
    # 1. Health check
    print("\n1. Checking API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        print_response("Health Check", response.json())
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API. Make sure the server is running.")
        print("Start the server with: python main.py")
        return
    
    # 2. Get API info
    print("\n2. Getting API information...")
    response = requests.get(f"{API_BASE_URL}/")
    print_response("API Info", response.json())
    
    # 3. Start analysis
    print("\n3. Starting network analysis...")
    analysis_request = {
        "sample_size": 5000,  # Smaller sample for faster processing
        "layers": ["retweet", "mention", "hashtag"],
        "algorithms": ["louvain", "leiden"]
    }
    
    response = requests.post(
        f"{API_BASE_URL}/api/analyze",
        json=analysis_request
    )
    
    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}")
        return
    
    result = response.json()
    analysis_id = result.get("analysis_id")
    print_response("Analysis Started", result)
    
    # 4. Monitor analysis progress
    print("\n4. Monitoring analysis progress...")
    max_wait = 300  # 5 minutes max
    wait_time = 0
    
    while wait_time < max_wait:
        response = requests.get(f"{API_BASE_URL}/api/status/{analysis_id}")
        status = response.json()
        
        progress = status.get("progress", 0)
        message = status.get("message", "")
        state = status.get("status", "unknown")
        
        print(f"Progress: {progress}% - {message}")
        
        if state == "completed":
            print("\n✓ Analysis completed!")
            break
        elif state == "error":
            print(f"\n✗ Analysis failed: {message}")
            return
        
        time.sleep(5)
        wait_time += 5
    
    if wait_time >= max_wait:
        print("\n⚠ Analysis taking longer than expected. Results may be partial.")
    
    # 5. Get network statistics
    print("\n5. Getting network statistics...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/network/stats")
        print_response("Network Statistics", response.json())
    except Exception as e:
        print(f"Error: {e}")
    
    # 6. Get community detection results
    print("\n6. Getting community detection results...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/communities")
        communities = response.json()
        
        # Print summary
        if "communities" in communities:
            print(f"\nFound {len(communities['communities'])} community detection results:")
            for key, result in communities["communities"].items():
                print(f"  - {key}: {result.get('n_communities', 0)} communities "
                      f"(modularity: {result.get('modularity', 0):.3f})")
    except Exception as e:
        print(f"Error: {e}")
    
    # 7. Get coordination results
    print("\n7. Getting coordinated behavior results...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/coordination")
        coordination = response.json()
        
        if "coordination" in coordination:
            coord_data = coordination["coordination"]
            print(f"\nFound {coord_data.get('n_groups', 0)} coordinated groups")
            print(f"Signals detected: {coord_data.get('signals', {})}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 8. Get misinformation clusters
    print("\n8. Getting misinformation clusters...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/misinformation")
        misinfo = response.json()
        
        if "misinformation" in misinfo:
            misinfo_data = misinfo["misinformation"]
            print(f"\nFound {misinfo_data.get('n_clusters', 0)} misinformation clusters")
            high_risk = misinfo_data.get('high_risk_clusters', [])
            print(f"High-risk clusters: {len(high_risk)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 9. Get visualization data
    print("\n9. Getting visualization data...")
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/visualization/data",
            params={"max_nodes": 500, "layer": "retweet"}
        )
        viz_data = response.json()
        
        if "nodes" in viz_data and "edges" in viz_data:
            print(f"\nVisualization data:")
            print(f"  - Nodes: {len(viz_data['nodes'])}")
            print(f"  - Edges: {len(viz_data['edges'])}")
            print(f"  - Layer: {viz_data.get('metadata', {}).get('layer', 'unknown')}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("Example usage completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

