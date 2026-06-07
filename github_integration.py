"""
GitHub Integration - Crea issues automáticamente en defects
"""

import requests
from typing import Dict, Optional
from pathlib import Path
from rich.console import Console
from datetime import datetime

console = Console()


class GitHubIssueCreator:
    """
    Crea issues en GitHub automáticamente
    """
    
    def __init__(self, 
                 repo: Optional[str] = None,
                 token: Optional[str] = None):
        """
        Args:
            repo: formato "owner/repo" ej: "PedroGM80/smart-web-test-ai"
            token: GitHub Personal Access Token
        """
        self.repo = repo or self._load_from_env("GITHUB_REPO")
        self.token = token or self._load_from_env("GITHUB_TOKEN")
        self.api_url = "https://api.github.com"
    
    def _load_from_env(self, key: str) -> Optional[str]:
        """Carga desde .env"""
        env_file = Path(".env")
        if env_file.exists():
            for line in env_file.read_text().split("\n"):
                if line.startswith(f"{key}="):
                    return line.split("=", 1)[1].strip()
        return None
    
    def _get_headers(self) -> Dict:
        """Headers para API GitHub"""
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Smart-Test"
        }
    
    def create_issue_from_failure(self, result: Dict) -> Optional[str]:
        """
        Crea issue cuando un test falla
        
        Args:
            result: Dict con {url, objective, error, pass_rate, ...}
        
        Returns:
            Issue URL o None si falla
        """
        if not self.repo or not self.token:
            console.print("[yellow]⚠️  GITHUB_REPO o GITHUB_TOKEN no configurado[/yellow]")
            return None
        
        if result.get("pass_rate", 100) >= 75:
            return None  # No crea issue si pass rate >= 75%
        
        title = f"Test Failure: {result.get('url', 'Unknown')}"
        
        body = f"""
## Test Failure Report

**URL Tested:** {result.get('url', 'N/A')}
**Objective:** {result.get('objective', 'N/A')}

### Metrics
- Pass Rate: **{result.get('pass_rate', 0):.1f}%**
- Duration: **{result.get('duration', 0):.1f}s**
- Mode: **{result.get('mode', 'balanced')}**
- Model: **{result.get('model', 'unknown')}**

### Error Details
```
{result.get('error', 'No error details')}
```

### Timestamp
{datetime.now().isoformat()}

---
*Created by Smart Test - AI Testing Platform*
"""
        
        labels = self._determine_labels(result)
        
        payload = {
            "title": title,
            "body": body,
            "labels": labels
        }
        
        return self._create_issue(payload)
    
    def _determine_labels(self, result: Dict) -> list:
        """Determina labels según pass rate"""
        labels = ["smart-test", "automated"]
        
        pass_rate = result.get("pass_rate", 100)
        if pass_rate < 50:
            labels.append("critical")
        elif pass_rate < 75:
            labels.append("bug")
        
        return labels
    
    def _create_issue(self, payload: Dict) -> Optional[str]:
        """Crea issue en GitHub"""
        url = f"{self.api_url}/repos/{self.repo}/issues"
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers()
            )
            
            if response.status_code == 201:
                issue_data = response.json()
                issue_url = issue_data.get("html_url")
                console.print(f"[green]✅ Issue creado: {issue_url}[/green]")
                return issue_url
            else:
                console.print(f"[red]❌ Error GitHub: {response.status_code}[/red]")
                console.print(response.text)
                return None
        except Exception as e:
            console.print(f"[red]❌ Error: {str(e)}[/red]")
            return None
    
    def add_comment_to_issue(self, issue_number: int, comment: str) -> bool:
        """
        Añade comentario a un issue
        
        Args:
            issue_number: Número del issue
            comment: Texto del comentario
        """
        if not self.repo or not self.token:
            return False
        
        url = f"{self.api_url}/repos/{self.repo}/issues/{issue_number}/comments"
        payload = {"body": comment}
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers()
            )
            return response.status_code == 201
        except:
            return False
    
    def find_existing_issue(self, url: str) -> Optional[int]:
        """
        Busca si ya existe issue para esta URL
        
        Returns:
            Issue number o None
        """
        if not self.repo or not self.token:
            return None
        
        search_url = f"{self.api_url}/search/issues"
        query = f"repo:{self.repo} in:title \"{url}\" is:open"
        
        params = {"q": query}
        
        try:
            response = requests.get(
                search_url,
                params=params,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                items = response.json().get("items", [])
                if items:
                    return items[0].get("number")
        except:
            pass
        
        return None
    
    def create_or_update_issue(self, result: Dict) -> Optional[str]:
        """
        Crea nuevo issue o actualiza existente
        
        Args:
            result: Dict con resultado del test
        
        Returns:
            Issue URL
        """
        url = result.get("url")
        existing_issue = self.find_existing_issue(url)
        
        if existing_issue:
            # Añade comentario al existing
            comment = f"""
### Update - {datetime.now().isoformat()}

Pass Rate: **{result.get('pass_rate', 0):.1f}%**
Status: Still failing
"""
            self.add_comment_to_issue(existing_issue, comment)
            console.print(f"[cyan]💬 Comentario añadido a issue #{existing_issue}[/cyan]")
            return f"https://github.com/{self.repo}/issues/{existing_issue}"
        else:
            # Crea nuevo
            return self.create_issue_from_failure(result)
    
    def close_issue(self, issue_number: int, comment: str = "Fixed by Smart Test") -> bool:
        """
        Cierra un issue
        """
        if not self.repo or not self.token:
            return False
        
        url = f"{self.api_url}/repos/{self.repo}/issues/{issue_number}"
        payload = {
            "state": "closed"
        }
        
        try:
            response = requests.patch(
                url,
                json=payload,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                self.add_comment_to_issue(issue_number, comment)
                console.print(f"[green]✅ Issue #{issue_number} cerrado[/green]")
                return True
        except:
            pass
        
        return False


def setup_github() -> bool:
    """
    Guía interactiva para configurar GitHub
    """
    console.print("[cyan]🔗 GitHub Integration Setup[/cyan]")
    console.print()
    console.print("1. Ve a: https://github.com/settings/tokens/new")
    console.print("2. Scopes necesarios: repo (todas las opciones)")
    console.print("3. Copia el token (no se puede ver después)")
    console.print()
    
    repo = input("Repository (owner/repo): ").strip()
    token = input("Personal Access Token: ").strip()
    
    if not repo or "/" not in repo:
        console.print("[red]❌ Repo inválido[/red]")
        return False
    
    if not token:
        console.print("[red]❌ Token vacío[/red]")
        return False
    
    # Guarda en .env
    env_file = Path(".env")
    content = env_file.read_text() if env_file.exists() else ""
    
    if "GITHUB_REPO=" not in content:
        content += f"\nGITHUB_REPO={repo}"
    if "GITHUB_TOKEN=" not in content:
        content += f"\nGITHUB_TOKEN={token}"
    
    env_file.write_text(content)
    
    console.print("[green]✅ GitHub configurado[/green]")
    return True


if __name__ == "__main__":
    # Test
    creator = GitHubIssueCreator()
    
    if not creator.repo or not creator.token:
        if setup_github():
            creator = GitHubIssueCreator()
        else:
            exit(1)
    
    # Test issue creation
    test_result = {
        "url": "https://github.com",
        "objective": "Test repository",
        "pass_rate": 45.0,
        "duration": 42.3,
        "error": "Timeout exceeded after 30 seconds",
        "mode": "balanced",
        "model": "mistral"
    }
    
    creator.create_or_update_issue(test_result)
