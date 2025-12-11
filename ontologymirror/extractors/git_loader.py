import os
from typing import List, Optional
import git
from git import Repo
from ..config.settings import settings

class GitLoader:
    """
    Handles cloning or pulling git repositories.
    負責將遠端 GitHub 專案 Clone 到本地 data/raw_repos 目錄。
    """
    
    def load_repo(self, repo_url: str) -> str:
        """
        Clones a repo and returns the local directory path.
        If repo exists, it pulls the latest changes.
        """
        repo_name = repo_url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
            
        local_path = settings.REPOS_DIR / repo_name
        
        if local_path.exists():
            print(f"🔄 Repository exists at {local_path}, pulling latest...")
            try:
                repo = Repo(local_path)
                repo.remotes.origin.pull()
            except Exception as e:
                print(f"⚠️ Git pull failed: {e}")
        else:
            print(f"⬇️ Cloning {repo_url} to {local_path}...")
            Repo.clone_from(repo_url, local_path)
            
        return str(local_path)
