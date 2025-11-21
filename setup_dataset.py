"""
Helper script to set up and test dataset loading
"""
import os
import sys
from pathlib import Path

def check_mumin_token():
    """Check if MuMiN bearer token is set"""
    token = os.getenv('MUMIN_BEARER_TOKEN')
    if token:
        print("✅ MUMIN_BEARER_TOKEN is set")
        print(f"   Token: {token[:10]}...{token[-5:]}")
        return True
    else:
        print("❌ MUMIN_BEARER_TOKEN not found")
        print("\nTo set it:")
        print("  Windows PowerShell: $env:MUMIN_BEARER_TOKEN='your_token'")
        print("  Windows CMD: set MUMIN_BEARER_TOKEN=your_token")
        print("  Linux/Mac: export MUMIN_BEARER_TOKEN='your_token'")
        print("\nOr create a .env file with:")
        print("  MUMIN_BEARER_TOKEN=your_token")
        return False

def test_sample_data():
    """Test sample data generation"""
    print("\n" + "="*60)
    print("Testing Sample Data Generation")
    print("="*60)
    
    try:
        from data.data_loader import MuMiNDataLoader
        
        loader = MuMiNDataLoader()
        data = loader.load_dataset(sample_size=100)
        
        print(f"✅ Sample data generated successfully!")
        print(f"   Users: {len(data['users'])}")
        print(f"   Tweets: {len(data['tweets'])}")
        print(f"   Claims: {len(data['claims'])}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_mumin_connection():
    """Test MuMiN dataset connection"""
    print("\n" + "="*60)
    print("Testing MuMiN Dataset Connection")
    print("="*60)
    
    token = os.getenv('MUMIN_BEARER_TOKEN')
    if not token:
        print("⚠️  Skipping: MUMIN_BEARER_TOKEN not set")
        return False
    
    try:
        from mumin import compile_dataset
        
        print("Attempting to compile small MuMiN dataset...")
        print("(This may take a few minutes and use API quota)")
        
        # Ask for confirmation
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            print("Skipped.")
            return False
        
        dataset = compile_dataset(size='small', bearer_token=token)
        
        print("✅ MuMiN dataset compiled successfully!")
        if hasattr(dataset, 'tweets'):
            print(f"   Tweets available: {len(dataset.tweets) if dataset.tweets is not None else 0}")
        if hasattr(dataset, 'users'):
            print(f"   Users available: {len(dataset.users) if dataset.users is not None else 0}")
        
        return True
    except ImportError:
        print("❌ MuMiN package not installed")
        print("   Install with: pip install mumin")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_cache():
    """Check for cached data"""
    print("\n" + "="*60)
    print("Checking Data Cache")
    print("="*60)
    
    cache_dir = Path("data/mumin_cache")
    if cache_dir.exists():
        files = list(cache_dir.glob("*.parquet"))
        if files:
            print(f"✅ Found {len(files)} cached data files:")
            for f in files:
                size = f.stat().st_size / (1024 * 1024)  # MB
                print(f"   - {f.name} ({size:.2f} MB)")
        else:
            print("ℹ️  Cache directory exists but is empty")
    else:
        print("ℹ️  No cache directory found (will be created on first run)")

def main():
    """Main setup function"""
    print("="*60)
    print("Dataset Setup Checker")
    print("="*60)
    
    # Check token
    has_token = check_mumin_token()
    
    # Test sample data
    sample_ok = test_sample_data()
    
    # Check cache
    check_cache()
    
    # Test MuMiN if token available
    if has_token:
        mumin_ok = test_mumin_connection()
    else:
        mumin_ok = False
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print(f"Sample Data: {'✅ Ready' if sample_ok else '❌ Error'}")
    print(f"MuMiN Token: {'✅ Set' if has_token else '❌ Not Set'}")
    print(f"MuMiN Connection: {'✅ Working' if mumin_ok else '⚠️  Not Tested/Error'}")
    
    if sample_ok:
        print("\n✅ You can use sample data immediately!")
        print("   Just run: python main.py")
    
    if has_token and mumin_ok:
        print("\n✅ MuMiN dataset is ready to use!")
    elif has_token:
        print("\n⚠️  MuMiN token is set but connection test failed")
        print("   You can still try using it - it may work with the API")

if __name__ == "__main__":
    main()

