# -*- coding: utf-8 -*-
"""
Test Model Persistence
======================

Verify that model selection is persistent across server restarts.
"""

import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from WhereSpaceChat import (
    get_current_model,
    set_current_model,
    load_model_config,
    MODEL_CONFIG_FILE
)

def test_persistence():
    """Test model persistence functionality."""
    print("=" * 70)
    print("MODEL PERSISTENCE TEST")
    print("=" * 70)
    
    # Test 1: Initial state
    print("\n1. Checking initial state...")
    initial_model = get_current_model()
    print(f"   Current model: {initial_model}")
    
    # Test 2: Switch model
    print("\n2. Switching to 'mistral'...")
    set_current_model("mistral")
    print(f"   Current model: {get_current_model()}")
    
    # Test 3: Check config file
    print("\n3. Checking config file...")
    if MODEL_CONFIG_FILE.exists():
        with open(MODEL_CONFIG_FILE, 'r') as f:
            config = json.load(f)
        print(f"   Config file exists: ?")
        print(f"   Saved model: {config.get('current_model')}")
    else:
        print(f"   Config file missing: ?")
        return False
    
    # Test 4: Reload from disk
    print("\n4. Reloading from disk...")
    reloaded_model = load_model_config()
    print(f"   Reloaded model: {reloaded_model}")
    
    # Test 5: Verify persistence
    print("\n5. Verifying persistence...")
    if reloaded_model == "mistral":
        print(f"   ? Persistence works! Model correctly saved and reloaded.")
        success = True
    else:
        print(f"   ? Persistence failed. Expected 'mistral', got '{reloaded_model}'")
        success = False
    
    # Test 6: Switch to another model
    print("\n6. Switching to 'gemma2'...")
    set_current_model("gemma2")
    print(f"   Current model: {get_current_model()}")
    
    # Test 7: Final verification
    print("\n7. Final verification...")
    final_model = load_model_config()
    if final_model == "gemma2":
        print(f"   ? Model correctly updated to 'gemma2'")
    else:
        print(f"   ? Update failed")
        success = False
    
    # Cleanup: Restore original model
    print(f"\n8. Restoring original model...")
    set_current_model(initial_model)
    print(f"   Restored to: {get_current_model()}")
    
    print("\n" + "=" * 70)
    if success:
        print("? ALL TESTS PASSED")
    else:
        print("? SOME TESTS FAILED")
    print("=" * 70)
    
    return success


if __name__ == "__main__":
    try:
        success = test_persistence()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n? Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
