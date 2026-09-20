import os
import sys
from tqdm import tqdm

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from eval.eval_metrics import code_pass_rate
from src.rag_pipeline.agent import execute_code_safely

def main():
    vault_dir = os.path.join(BASE_DIR, "codevault", "python")
    
    if not os.path.exists(vault_dir):
        print(f"Code vault directory not found: {vault_dir}")
        print("Run the agent a few times to generate some Python code first!")
        return

    py_files = [os.path.join(vault_dir, f) for f in os.listdir(vault_dir) if f.endswith(".py")]
    
    if not py_files:
        print(f"No .py files found in {vault_dir}")
        return

    print(f"Found {len(py_files)} Python files in Code Vault. Executing...")
    
    passed = 0
    total = len(py_files)
    
    for py_file in tqdm(py_files):
        success, output = execute_code_safely(py_file)
        if success:
            passed += 1
        else:
            print(f"\n[FAILED] {os.path.basename(py_file)}")
            print(output[:200] + ("..." if len(output) > 200 else ""))
            
    pass_rate = code_pass_rate(total, passed)
    
    print("\n--- CODE EXECUTION EVALUATION ---")
    print(f"Total Files Tested : {total}")
    print(f"Passed             : {passed}")
    print(f"Failed             : {total - passed}")
    print(f"Pass Rate          : {pass_rate:.2%}")

if __name__ == "__main__":
    main()
