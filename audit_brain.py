import os
import subprocess
import json

def audit_bpfcobrain():
    base_path = r"C:\BPFCo\BPFCoBrain"
    report = {
        "base_path_exists": os.path.exists(base_path),
        "contents": [],
        "git_status": "unknown",
        "key_files": {},
        "gsn_paths_found": []
    }
    
    if report["base_path_exists"]:
        try:
            # 1. List top-level contents
            report["contents"] = os.listdir(base_path)
            
            # 2. Check Git status
            try:
                git_check = subprocess.run(
                    ["git", "-C", base_path, "status", "--porcelain"], 
                    capture_output=True, text=True, check=True
                )
                report["git_status"] = "clean" if not git_check.stdout.strip() else "has_uncommitted_changes"
            except FileNotFoundError:
                report["git_status"] = "git_not_found_in_path"
            except subprocess.CalledProcessError:
                report["git_status"] = "not_a_git_repo"
            
            # 3. Check for key architecture files
            key_files = ["omniroute.py", "vault-indexer.py", "brain-dashboard.py", "ObsidianVault", ".git"]
            report["key_files"] = {f: os.path.exists(os.path.join(base_path, f)) for f in key_files}
            
        except Exception as e:
            report["error"] = str(e)
    else:
        report["message"] = "Base path C:\\BPFCo\\BPFCoBrain not found. Please verify the path."
        
    # 4. Basic GSN installation check (checks common paths and env vars)
    potential_gsn_paths = [
        r"C:\Program Files\GSN",
        r"C:\GSN",
        os.environ.get("GSN_PATH", ""),
        os.environ.get("LOCALAPPDATA", "") + "\\GSN"
    ]
    report["gsn_paths_found"] = [p for p in potential_gsn_paths if p and os.path.exists(p)]
    
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    audit_bpfcobrain()