import os
import shutil
import subprocess
import tempfile
from typing import Optional

class GitLoader:
    """
    Downloads source code from a Git repository for analysis.
    Uses generic 'git' commands, so it requires git to be installed.
    """

    def __init__(self, base_dir: str = "data/raw_repos"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def load_repo(self, repo_url: str, branch: str = "main") -> str:
        """
        Clones a git repository to the local data workspace.
        
        Args:
            repo_url: HTTPs URL of the git repo.
            branch: Branch to clone (default: main).
            
        Returns:
            The absolute path to the cloned directory.
        """
        repo_name = repo_url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
            
        target_path = os.path.join(self.base_dir, repo_name)
        
        print(f"⬇️ Cloning {repo_url} to {target_path}...")
        
        if os.path.exists(target_path):
            print(f"   ⚠️ Directory exists. Pulling latest changes...")
            try:
                subprocess.run(["git", "pull"], cwd=target_path, check=True)
            except subprocess.CalledProcessError:
                print("   ❌ Git pull failed. Re-cloning...")
                shutil.rmtree(target_path)
                subprocess.run(["git", "clone", "--depth", "1", repo_url, target_path], check=True)
        else:
            try:
                subprocess.run(["git", "clone", "--depth", "1", repo_url, target_path], check=True)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Failed to clone repository: {e}")
                
        return os.path.abspath(target_path)
