# -*- coding: utf-8 -*-
"""
Test Model Persistence and Switching
=====================================

Comprehensive test to verify model switching works and persists.
Run this while WhereSpaceChat.py server is running.
"""

import requests
import json
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5000"
# Config file is in parent/config directory
CONFIG_FILE = Path(__file__).parent.parent / "config" / ".model_config.json"

def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)

def test_get_current_model():
    """Test getting current model."""
    print("\n1. Getting current model...")
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        data = response.json()
        
        current = data.get('current_model')
        persisted = data.get('persisted_model')
        verified = data.get('persistence_verified')
        
        print(f"   Current model (memory): {current}")
        print(f"   Persisted model (file): {persisted}")
        print(f"   Persistence verified: {'?' if verified else '?'}")
        
        return current
    except Exception as e:
        print(f"   ? Error: {e}")
        return None

def test_switch_model(new_model):
    """Test switching to a new model."""
    print(f"\n2. Switching to model: {new_model}")
    try:
        response = requests.post(
            f"{BASE_URL}/api/set_model",
            json={"model": new_model}
        )
        data = response.json()
        
        if data.get('success'):
            print(f"   ? Switch successful")
            print(f"   Model: {data.get('model')}")
            print(f"   Verified: {data.get('verified', False)}")
            
            if data.get('warning'):
                print(f"   Warning: {data.get('warning')}")
            
            return True
        else:
            print(f"   ? Switch failed: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"   ? Error: {e}")
        return False

def test_verify_persistence():
    """Test dedicated persistence verification endpoint."""
    print("\n3. Verifying persistence...")
    try:
        response = requests.get(f"{BASE_URL}/api/verify_model_persistence")
        data = response.json()
        
        if data.get('verified'):
            print(f"   ? Persistence verified")
            print(f"   Current: {data.get('current_model')}")
            print(f"   Saved: {data.get('saved_model')}")
            print(f"   Reloaded: {data.get('reloaded_model')}")
            return True
        else:
            print(f"   ? Verification failed: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"   ? Error: {e}")
        return False

def test_config_file():
    """Test config file exists and is readable."""
    print("\n4. Checking config file...")
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print(f"   ? Config file exists: {CONFIG_FILE}")
            print(f"   Model in file: {config.get('current_model')}")
            return config.get('current_model')
        else:
            print(f"   ? Config file not found: {CONFIG_FILE}")
            return None
    except Exception as e:
        print(f"   ? Error reading config: {e}")
        return None

def test_persistence_after_switch(test_model):
    """Test that model persists after switch."""
    print(f"\n5. Testing persistence after switch to {test_model}...")
    
    # Switch model
    if not test_switch_model(test_model):
        print("   ? Model switch failed")
        return False
    
    # Small delay
    time.sleep(0.5)
    
    # Verify immediately
    if not test_verify_persistence():
        print("   ? Immediate verification failed")
        return False
    
    # Check config file
    saved_model = test_config_file()
    if saved_model != test_model:
        print(f"   ? Config file has wrong model: {saved_model}")
        return False
    
    # Check status endpoint
    current = test_get_current_model()
    if current != test_model:
        print(f"   ? Status endpoint has wrong model: {current}")
        return False
    
    print(f"   ? All checks passed for {test_model}")
    return True

def main():
    """Run all tests."""
    print_header("MODEL PERSISTENCE TEST SUITE")
    
    print("\nTesting against:", BASE_URL)
    print("Config file:", CONFIG_FILE)
    
    # Test server is running
    try:
        requests.get(f"{BASE_URL}/api/status", timeout=2)
    except:
        print("\n? ERROR: Server not running at", BASE_URL)
        print("Start server with: python WhereSpaceChat.py")
        return False
    
    # Get initial model
    initial_model = test_get_current_model()
    if not initial_model:
        print("\n? Cannot get initial model")
        return False
    
    # Test persistence verification
    if not test_verify_persistence():
        print("\n? Initial verification failed")
        return False
    
    # Test config file
    file_model = test_config_file()
    if file_model != initial_model:
        print(f"\n? Config file mismatch: {file_model} != {initial_model}")
        return False
    
    # Test switching to different models
    test_models = ['mistral', 'gemma2', 'llama3.1']
    
    all_passed = True
    for test_model in test_models:
        if not test_persistence_after_switch(test_model):
            all_passed = False
            break
    
    # Restore initial model
    print(f"\n6. Restoring initial model: {initial_model}")
    test_switch_model(initial_model)
    
    # Final summary
    print_header("TEST SUMMARY")
    if all_passed:
        print("? ALL TESTS PASSED")
        print("\nModel persistence is working correctly!")
        print("- Model switches are saved to disk")
        print("- Persistence verified across all checks")
        print("- Config file is properly written and read")
    else:
        print("? SOME TESTS FAILED")
        print("\nModel persistence has issues!")
        print("Check the errors above for details")
    
    print("=" * 70)
    return all_passed

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        exit(130)
    except Exception as e:
        print(f"\n\n? Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
