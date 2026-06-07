"""
Slack Integration - Envía resultados de tests a Slack
"""

import json
import requests
from typing import Dict, Optional
from pathlib import Path
from rich.console import Console

console = Console()


class SlackNotifier:
    """
    Envía notificaciones a Slack
    """
    
    def __init__(self, webhook_url: Optional[str] = None):
        """
        Args:
            webhook_url: URL del webhook de Slack
                        Obtener en: https://api.slack.com/messaging/webhooks
        """
        self.webhook_url = webhook_url or self._load_webhook_from_env()
    
    def _load_webhook_from_env(self) -> Optional[str]:
        """Carga webhook desde archivo .env"""
        env_file = Path(".env")
        if env_file.exists():
            for line in env_file.read_text().split("\n"):
                if line.startswith("SLACK_WEBHOOK_URL="):
                    return line.split("=", 1)[1].strip()
        return None
    
    def send_test_result(self, result: Dict) -> bool:
        """
        Envía resultado de test a Slack
        
        Args:
            result: Dict con resultado {url, pass_rate, duration, ...}
        
        Returns:
            bool: True si se envió exitosamente
        """
        if not self.webhook_url:
            console.print("[yellow]⚠️  SLACK_WEBHOOK_URL no configurado[/yellow]")
            return False
        
        # Determina color según pass_rate
        pass_rate = result.get("pass_rate", 0)
        if pass_rate >= 90:
            color = "#2ecc71"  # Verde
            emoji = "✅"
        elif pass_rate >= 75:
            color = "#f39c12"  # Naranja
            emoji = "⚠️"
        else:
            color = "#e74c3c"  # Rojo
            emoji = "❌"
        
        # Construye mensaje
        message = {
            "attachments": [
                {
                    "color": color,
                    "title": f"{emoji} Test Result",
                    "fields": [
                        {
                            "title": "URL",
                            "value": result.get("url", "N/A"),
                            "short": False
                        },
                        {
                            "title": "Objective",
                            "value": result.get("objective", "N/A"),
                            "short": False
                        },
                        {
                            "title": "Pass Rate",
                            "value": f"{result.get('pass_rate', 0):.1f}%",
                            "short": True
                        },
                        {
                            "title": "Duration",
                            "value": f"{result.get('duration', 0):.1f}s",
                            "short": True
                        },
                        {
                            "title": "Status",
                            "value": result.get("status", "unknown").upper(),
                            "short": True
                        },
                        {
                            "title": "Mode",
                            "value": result.get("mode", "balanced"),
                            "short": True
                        }
                    ],
                    "footer": "Smart Test",
                    "ts": int(__import__("time").time())
                }
            ]
        }
        
        try:
            response = requests.post(self.webhook_url, json=message)
            if response.status_code == 200:
                console.print("[green]✅ Slack notification sent[/green]")
                return True
            else:
                console.print(f"[red]❌ Slack error: {response.status_code}[/red]")
                return False
        except Exception as e:
            console.print(f"[red]❌ Error sending to Slack: {str(e)}[/red]")
            return False
    
    def send_summary(self, summary: Dict) -> bool:
        """
        Envía resumen de estadísticas a Slack
        
        Args:
            summary: Dict con {total_tests, avg_pass_rate, avg_duration, ...}
        """
        if not self.webhook_url:
            return False
        
        message = {
            "attachments": [
                {
                    "color": "#667eea",
                    "title": "📊 Smart Test Summary",
                    "fields": [
                        {
                            "title": "Total Tests",
                            "value": str(summary.get("total_tests", 0)),
                            "short": True
                        },
                        {
                            "title": "Avg Pass Rate",
                            "value": f"{summary.get('avg_pass_rate', 0):.1f}%",
                            "short": True
                        },
                        {
                            "title": "Avg Duration",
                            "value": f"{summary.get('avg_duration', 0):.1f}s",
                            "short": True
                        },
                        {
                            "title": "Domains",
                            "value": str(summary.get("domains", 0)),
                            "short": True
                        },
                        {
                            "title": "Best Model",
                            "value": summary.get("best_model", "N/A"),
                            "short": True
                        },
                        {
                            "title": "Time Saved",
                            "value": f"{summary.get('total_time_saved', 0):.1f}h",
                            "short": True
                        }
                    ],
                    "footer": "Smart Test Analytics"
                }
            ]
        }
        
        try:
            response = requests.post(self.webhook_url, json=message)
            return response.status_code == 200
        except:
            return False
    
    def send_error(self, url: str, error: str) -> bool:
        """
        Envía notificación de error a Slack
        """
        if not self.webhook_url:
            return False
        
        message = {
            "attachments": [
                {
                    "color": "#e74c3c",
                    "title": "❌ Test Failed",
                    "fields": [
                        {
                            "title": "URL",
                            "value": url,
                            "short": False
                        },
                        {
                            "title": "Error",
                            "value": error,
                            "short": False
                        }
                    ],
                    "footer": "Smart Test"
                }
            ]
        }
        
        try:
            response = requests.post(self.webhook_url, json=message)
            return response.status_code == 200
        except:
            return False


def setup_slack_webhook() -> str:
    """
    Guía interactiva para configurar webhook de Slack
    
    Returns:
        URL del webhook
    """
    console.print("[cyan]🔗 Slack Webhook Setup[/cyan]")
    console.print()
    console.print("1. Ve a: https://api.slack.com/messaging/webhooks")
    console.print("2. Click 'Create New App'")
    console.print("3. Selecciona tu workspace")
    console.print("4. Activa 'Incoming Webhooks'")
    console.print("5. Copia la URL del webhook")
    console.print()
    
    webhook_url = input("Pega tu Slack webhook URL: ").strip()
    
    if not webhook_url.startswith("https://hooks.slack.com"):
        console.print("[red]❌ URL inválida[/red]")
        return ""
    
    # Guarda en .env
    env_file = Path(".env")
    content = env_file.read_text() if env_file.exists() else ""
    
    if "SLACK_WEBHOOK_URL=" in content:
        content = content.replace(
            [line for line in content.split("\n") if line.startswith("SLACK_WEBHOOK_URL=")][0],
            f"SLACK_WEBHOOK_URL={webhook_url}"
        )
    else:
        content += f"\nSLACK_WEBHOOK_URL={webhook_url}\n"
    
    env_file.write_text(content)
    
    console.print("[green]✅ Webhook guardado en .env[/green]")
    return webhook_url


if __name__ == "__main__":
    # Test
    notifier = SlackNotifier()
    
    if not notifier.webhook_url:
        webhook = setup_slack_webhook()
        notifier = SlackNotifier(webhook)
    
    # Envía test
    test_result = {
        "url": "https://github.com",
        "objective": "Test repository",
        "pass_rate": 95.5,
        "duration": 42.3,
        "status": "success",
        "mode": "balanced"
    }
    
    notifier.send_test_result(test_result)
