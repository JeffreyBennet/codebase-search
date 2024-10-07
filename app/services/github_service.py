import os
import git
import shutil

class GitHubService:
    def __init__(self, repo_dir="repos"):
        self.repo_dir = repo_dir
        if not os.path.exists(self.repo_dir):
            os.makedirs(self.repo_dir)

    def clone_repo(self, repo_url):
        """Clones a GitHub repository to a local directory."""
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        repo_path = os.path.join(self.repo_dir, repo_name)
        
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)  # Clear existing repo if already cloned
        
        git.Repo.clone_from(repo_url, repo_path)
        return repo_path

    def get_code_files(self, repo_path):
        """Returns a list of all code files in the repository."""
        code_files = []
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file.endswith(('.py', '.js', '.java', '.cpp', '.ts', '.cs')):  # Adjust for your language preferences
                    code_files.append(os.path.join(root, file))
        return code_files
