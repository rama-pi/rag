#helps as a self test for this folder
# framework/__main__.py
import sys
import os
from pathlib import Path

# Explicitly import your framework utilities
from framework.base_classes import Model
from framework.helpers import discover

def run_framework_self_test():
    print("\n==============================================")
    print("🛠️  RUNNING FRAMEWORK SUBSYSTEM SELF-TEST")
    print("==============================================\n")

    # Check 1: Verify Directory Enivronment Stability
    required_folders = ["plugins/chunkers", "plugins/loaders", "plugins/models", "plugins/retrievers"]
    all_folders_exist = True

    print("[Step 1/3] Verifying folder directory trees...")
    for folder in required_folders:
        if Path(folder).exists():
            print(f"  └── ✅ Found: /{folder}")
        else:
            print(f"  └── ❌ MISSING: /{folder} (Check file layout)")
            all_folders_exist = False

    if not all_folders_exist:
        print("\n💥 Self-Test Failed: Missing core plugin infrastructure directories.")
        sys.exit(1)

    # Check 2: Dynamic Link-Loading & Registry Verification
    print("\n[Step 2/3] Checking dynamic plugin discovery & compilation...")
    try:
        # Trigger the importlib dynamic load loop we fixed yesterday
        discover("plugins/models")
        print(f"  └── ✅ Discovery loop finished without compile errors.")
    except Exception as e:
        print(f"  └── ❌ CRITICAL: Plugin loading crashed!\nError Details: {e}")
        sys.exit(1)

    # Check 3: Functional Validation of Active Drivers
    print("\n[Step 3/3] Validating loaded plugin registries...")
    active_models = list(Model.registry.keys())
    print(f"  └── Registered Models found in global namespace: {active_models}")

    if not active_models:
        print("  └── ⚠️  Warning: Framework is active but zero models are registered.")
    else:
        print("  └── ✅ Registry linkage stable.")

    print("\n==============================================")
    print("🎉 ALL SUBSYSTEMS OPERATIONAL: SELF-TEST PASSED")
    print("==============================================\n")

if __name__ == "__main__":
    run_framework_self_test()


