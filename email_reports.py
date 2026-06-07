"""
Email Reports - Envía resúmenes automáticos por email
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
from rich.console import Console

console = Console()


class EmailReporter:
    """
    Envía reportes por email
    """
    
    def __init__(self, 
                 smtp_server: str = "smtp.gmail.com",
                 smtp_port: int = 587,
                 sender_email: Optional[str] = None,
                 sender_password: Optional[str] = None):
        """
        Args:
            smtp_server: SMTP server (default: Gmail)
            smtp_port: SMTP port (default: 587)
            sender_email: Email remitente
            sender_password: Password remitente
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email or self._load_from_env("SENDER_EMAIL")
        self.sender_password = sender_password or self._load_from_env("SENDER_PASSWORD")
    
    def _load_from_env(self, key: str) -> Optional[str]:
        """Carga variable desde .env"""
        env_file = Path(".env")
        if env_file.exists():
            for line in env_file.read_text().split("\n"):
                if line.startswith(f"{key}="):
                    return line.split("=", 1)[1].strip()
        return None
    
    def _generate_html(self, summary: Dict, recipients: List[str]) -> str:
        """
        Genera HTML bonito del reporte
        """
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .header p {{
            margin: 5px 0 0 0;
            opacity: 0.9;
        }}
        .content {{
            padding: 30px;
        }}
        .stat {{
            display: inline-block;
            width: 48%;
            margin: 1%;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 28px;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}
        .stat-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }}
        .highlight {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #666;
            border-top: 1px solid #eee;
        }}
        a {{
            color: #667eea;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Smart Test Daily Report</h1>
            <p>{datetime.now().strftime("%A, %B %d, %Y")}</p>
        </div>
        
        <div class="content">
            <div class="stat">
                <div class="stat-label">Total Tests</div>
                <div class="stat-value">{summary.get('total_tests', 0)}</div>
            </div>
            
            <div class="stat">
                <div class="stat-label">Pass Rate</div>
                <div class="stat-value">{summary.get('avg_pass_rate', 0):.1f}%</div>
            </div>
            
            <div class="stat">
                <div class="stat-label">Avg Duration</div>
                <div class="stat-value">{summary.get('avg_duration', 0):.1f}s</div>
            </div>
            
            <div class="stat">
                <div class="stat-label">Domains</div>
                <div class="stat-value">{summary.get('domains', 0)}</div>
            </div>
            
            <div style="clear: both; margin: 20px 0;">
                <h3 style="margin-top: 0;">Key Metrics</h3>
                
                <div class="stat">
                    <div class="stat-label">Best Model</div>
                    <div class="stat-value" style="font-size: 18px;">{summary.get('best_model', 'N/A')}</div>
                </div>
                
                <div class="stat">
                    <div class="stat-label">Time Saved</div>
                    <div class="stat-value" style="font-size: 18px;">{summary.get('total_time_saved', 0) / 3600:.1f}h</div>
                </div>
            </div>
            
            <div class="highlight">
                <strong>💡 Quick Insight:</strong><br>
                Your tests are running with a <strong>{summary.get('avg_pass_rate', 0):.1f}%</strong> pass rate, 
                averaging <strong>{summary.get('avg_duration', 0):.1f} seconds</strong> each.
                Keep up the good work!
            </div>
            
            <p style="text-align: center; margin-top: 30px;">
                <a href="http://localhost:8000/dashboard.html" style="background: #667eea; color: white; padding: 10px 20px; border-radius: 6px; display: inline-block;">
                    View Full Dashboard
                </a>
            </p>
        </div>
        
        <div class="footer">
            <p>Smart Test • AI-Powered Testing Platform</p>
            <p>This is an automated daily report. Configuration: Check your .env file</p>
        </div>
    </div>
</body>
</html>
"""
    
    def send_daily_report(self, recipients: List[str], summary: Dict) -> bool:
        """
        Envía reporte diario
        
        Args:
            recipients: Lista de emails
            summary: Dict con estadísticas
        
        Returns:
            bool: Success
        """
        if not self.sender_email or not self.sender_password:
            console.print("[yellow]⚠️  EMAIL credentials not configured[/yellow]")
            return False
        
        try:
            # Crea mensaje
            message = MIMEMultipart("alternative")
            message["Subject"] = f"Smart Test Daily Report - {datetime.now().strftime('%Y-%m-%d')}"
            message["From"] = self.sender_email
            message["To"] = ", ".join(recipients)
            
            # HTML
            html = self._generate_html(summary, recipients)
            html_part = MIMEText(html, "html")
            message.attach(html_part)
            
            # Envía
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipients, message.as_string())
            
            console.print(f"[green]✅ Report sent to {', '.join(recipients)}[/green]")
            return True
        
        except Exception as e:
            console.print(f"[red]❌ Error sending email: {str(e)}[/red]")
            return False
    
    def send_alert(self, recipients: List[str], alert_type: str, details: Dict) -> bool:
        """
        Envía alerta en tiempo real
        
        Args:
            recipients: Emails
            alert_type: "high_failure_rate" | "timeout" | "error"
            details: Info del alerta
        """
        if not self.sender_email or not self.sender_password:
            return False
        
        titles = {
            "high_failure_rate": "⚠️ High Failure Rate Detected",
            "timeout": "⏱️ Timeout Alert",
            "error": "❌ Test Error"
        }
        
        subject = f"[Alert] Smart Test - {titles.get(alert_type, 'Alert')}"
        
        html = f"""
<html>
<body style="font-family: Arial; background: #f5f5f5; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h2 style="color: #e74c3c;">{titles.get(alert_type)}</h2>
        
        <p><strong>URL:</strong> {details.get('url', 'N/A')}</p>
        <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Details:</strong> {details.get('message', 'No additional details')}</p>
        
        <p style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px;">
            Smart Test • Automated Testing Platform
        </p>
    </div>
</body>
</html>
"""
        
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = ", ".join(recipients)
            
            html_part = MIMEText(html, "html")
            message.attach(html_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipients, message.as_string())
            
            return True
        except:
            return False


def setup_email() -> bool:
    """
    Guía interactiva para configurar email
    """
    console.print("[cyan]📧 Email Configuration[/cyan]")
    console.print()
    console.print("Para usar Gmail:")
    console.print("1. Ve a: https://myaccount.google.com/apppasswords")
    console.print("2. Crea 'App password' para 'Mail'")
    console.print("3. Copia la contraseña (16 caracteres)")
    console.print()
    
    sender_email = input("Tu email: ").strip()
    sender_password = input("App password: ").strip()
    
    # Guarda en .env
    env_file = Path(".env")
    content = env_file.read_text() if env_file.exists() else ""
    
    if "SENDER_EMAIL=" not in content:
        content += f"\nSENDER_EMAIL={sender_email}"
    if "SENDER_PASSWORD=" not in content:
        content += f"\nSENDER_PASSWORD={sender_password}"
    
    env_file.write_text(content)
    
    console.print("[green]✅ Email configured[/green]")
    return True


if __name__ == "__main__":
    # Test
    reporter = EmailReporter()
    
    if not reporter.sender_email:
        setup_email()
        reporter = EmailReporter()
    
    # Envía reporte de prueba
    summary = {
        "total_tests": 42,
        "avg_pass_rate": 93.5,
        "avg_duration": 35.2,
        "domains": 8,
        "best_model": "mistral",
        "total_time_saved": 1260.5
    }
    
    recipients = [reporter.sender_email]  # A ti mismo para test
    reporter.send_daily_report(recipients, summary)
