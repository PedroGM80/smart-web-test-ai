"""
Metrics Collector
Recolecta métricas de reports JSON y envía a InfluxDB
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from rich.console import Console

console = Console()


class MetricsCollector:
    """Recolecta y envía métricas a InfluxDB"""
    
    def __init__(self, 
                 influxdb_url: str = "http://localhost:8086",
                 influxdb_org: str = "smart-test",
                 influxdb_bucket: str = "test_metrics",
                 influxdb_token: str = "smart-test-token"):
        """
        Inicializa collector
        
        Args:
            influxdb_url: URL de InfluxDB
            influxdb_org: Organización en InfluxDB
            influxdb_bucket: Bucket para almacenar datos
            influxdb_token: Token de autenticación
        """
        
        self.url = influxdb_url
        self.org = influxdb_org
        self.bucket = influxdb_bucket
        self.token = influxdb_token
        
        try:
            self.client = InfluxDBClient(
                url=self.url,
                org=self.org,
                token=self.token
            )
            self.write_api = self.client.write_api(write_type=SYNCHRONOUS)
            self._verify_connection()
        except Exception as e:
            console.print(f"[yellow]⚠ InfluxDB no disponible: {e}[/yellow]")
            console.print("[yellow]  Inicia con: docker-compose up[/yellow]")
            self.client = None
    
    def _verify_connection(self):
        """Verifica conexión a InfluxDB"""
        try:
            self.client.ping()
            console.print("[green]✓ Conectado a InfluxDB[/green]")
        except Exception as e:
            console.print(f"[red]✗ Error de conexión: {e}[/red]")
    
    def collect_from_report(self, report_path: str) -> Dict:
        """
        Recolecta métricas de un report JSON
        
        Args:
            report_path: Ruta al report JSON
        
        Returns:
            Dict con métricas recolectadas
        """
        
        try:
            with open(report_path, 'r') as f:
                report = json.load(f)
        except Exception as e:
            console.print(f"[red]Error leyendo report: {e}[/red]")
            return {}
        
        metrics = {
            "url": report.get("url", "unknown"),
            "objectives": report.get("objectives", ""),
            "timestamp": report.get("timestamp", datetime.now().isoformat()),
            "total_actions": report.get("actions_total", 0),
            "passed_actions": report.get("execution", {}).get("passed", 0),
            "failed_actions": report.get("execution", {}).get("failed", 0),
            "pass_rate": self._calculate_pass_rate(report),
            "validation_passed": self._check_validation(report),
            "errors_count": len(report.get("execution", {}).get("errors", []))
        }
        
        return metrics
    
    def _calculate_pass_rate(self, report: Dict) -> float:
        """Calcula porcentaje de éxito"""
        execution = report.get("execution", {})
        total = execution.get("total", 1)
        passed = execution.get("passed", 0)
        
        return (passed / total * 100) if total > 0 else 0
    
    def _check_validation(self, report: Dict) -> bool:
        """Verifica si validación pasó"""
        validation = report.get("validation", "").lower()
        return "pasó" in validation or "passed" in validation
    
    def send_metrics(self, metrics: Dict) -> bool:
        """
        Envía métricas a InfluxDB
        
        Args:
            metrics: Dict con métricas
        
        Returns:
            True si fue exitoso
        """
        
        if not self.client:
            console.print("[yellow]InfluxDB no disponible[/yellow]")
            return False
        
        try:
            # Crea puntos de datos
            points = []
            
            # Punto para resultado general del test
            point = Point("test_execution") \
                .tag("url", metrics.get("url", "unknown")) \
                .field("total_actions", int(metrics.get("total_actions", 0))) \
                .field("passed_actions", int(metrics.get("passed_actions", 0))) \
                .field("failed_actions", int(metrics.get("failed_actions", 0))) \
                .field("pass_rate", float(metrics.get("pass_rate", 0))) \
                .field("validation_passed", 1 if metrics.get("validation_passed") else 0) \
                .field("errors_count", int(metrics.get("errors_count", 0))) \
                .time(metrics.get("timestamp"))
            
            points.append(point)
            
            # Escribe a InfluxDB
            self.write_api.write(bucket=self.bucket, org=self.org, records=points)
            
            console.print(f"[green]✓ Métricas enviadas a InfluxDB[/green]")
            return True
        
        except Exception as e:
            console.print(f"[red]Error enviando métricas: {e}[/red]")
            return False
    
    def process_reports_dir(self, reports_dir: str = "reports") -> int:
        """
        Procesa todos los reports en un directorio
        
        Args:
            reports_dir: Directorio con reports JSON
        
        Returns:
            Número de reports procesados
        """
        
        reports_path = Path(reports_dir)
        
        if not reports_path.exists():
            console.print(f"[yellow]Directorio {reports_dir} no encontrado[/yellow]")
            return 0
        
        json_files = list(reports_path.glob("*.json"))
        processed = 0
        
        console.print(f"[cyan]Procesando {len(json_files)} reports...[/cyan]")
        
        for report_file in sorted(json_files):
            metrics = self.collect_from_report(str(report_file))
            if metrics and self.send_metrics(metrics):
                processed += 1
                console.print(f"  ✓ {report_file.name}")
        
        return processed
    
    def close(self):
        """Cierra conexión"""
        if self.client:
            self.client.close()


def collect_and_send(report_path: str):
    """Función auxiliar para recolectar y enviar un report"""
    
    collector = MetricsCollector()
    metrics = collector.collect_from_report(report_path)
    
    if metrics:
        collector.send_metrics(metrics)
    
    collector.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Procesa un report específico
        collector = MetricsCollector()
        metrics = collector.collect_from_report(sys.argv[1])
        
        if metrics:
            console.print("\n[cyan]Métricas recolectadas:[/cyan]")
            for key, value in metrics.items():
                console.print(f"  {key}: {value}")
            
            collector.send_metrics(metrics)
        
        collector.close()
    else:
        # Procesa directorio completo
        collector = MetricsCollector()
        processed = collector.process_reports_dir("reports")
        console.print(f"\n[green]Total procesados: {processed}[/green]")
        collector.close()
