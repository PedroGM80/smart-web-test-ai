"""
Analytics Dashboard Backend
Genera datos para dashboard visual
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict
import statistics

class DashboardAnalytics:
    """
    Genera estadísticas para dashboard
    """
    
    def __init__(self, repository=None):
        # Test results now come from the database (single source of truth).
        # Repository can be injected; otherwise the default database is used.
        if repository is not None:
            self.repository = repository
        else:
            from database import init_db
            self.repository = init_db().tests
        # Model-learning data keeps its own store (different nature of data)
        self.learning_file = Path("model_learning.json")
    
    def load_results(self) -> List[Dict]:
        """Carga resultados de tests desde la base de datos"""
        return [t.to_dict() for t in self.repository.list_chronological()]
    
    def load_learning(self) -> Dict:
        """Carga datos de learning"""
        if self.learning_file.exists():
            try:
                return json.loads(self.learning_file.read_text())
            except:
                return {}
        return {}
    
    def get_pass_rate_trend(self, days: int = 7) -> Dict:
        """
        Pass rate por día (últimos N días)
        
        Returns:
            {
                "labels": ["Mon", "Tue", ...],
                "data": [92.5, 95.0, ...]
            }
        """
        results = self.load_results()
        
        # Agrupa por fecha
        by_date = defaultdict(list)
        now = datetime.now()
        
        for result in results:
            try:
                ts = datetime.fromisoformat(result["timestamp"])
                days_ago = (now - ts).days
                
                if days_ago < days:
                    date_key = ts.strftime("%a")
                    pass_rate = result.get("pass_rate", 0)
                    by_date[date_key].append(pass_rate)
            except:
                continue
        
        # Calcula promedios
        labels = []
        data = []
        
        for i in range(days-1, -1, -1):
            target_date = now - timedelta(days=i)
            label = target_date.strftime("%a")
            
            if label in by_date:
                avg = statistics.mean(by_date[label])
                data.append(round(avg, 1))
            else:
                data.append(None)
            
            labels.append(label)
        
        return {
            "labels": labels,
            "data": data
        }
    
    def get_model_performance(self) -> Dict:
        """
        Comparativa de modelos
        
        Returns:
            {
                "labels": ["mistral", "neural-chat", ...],
                "success_rate": [95.5, 92.0, ...],
                "speed": [3.2, 2.1, ...],  # tokens/sec
                "runs": [10, 12, ...]
            }
        """
        learning = self.load_learning()
        by_domain = learning.get("by_domain", {})
        
        model_stats = defaultdict(lambda: {
            "runs": 0,
            "successes": 0,
            "total_time": 0
        })
        
        # Agrega por modelo
        for domain, models in by_domain.items():
            for model, stats in models.items():
                model_stats[model]["runs"] += stats.get("runs", 0)
                model_stats[model]["successes"] += stats.get("successes", 0)
                model_stats[model]["total_time"] += stats.get("total_time", 0)
        
        # Calcula métricas
        labels = []
        success_rates = []
        speeds = []
        runs = []
        
        for model, stats in sorted(model_stats.items()):
            if stats["runs"] > 0:
                success_rate = (stats["successes"] / stats["runs"]) * 100
                speed = stats["runs"] / max(stats["total_time"], 1)  # runs per second
                
                labels.append(model)
                success_rates.append(round(success_rate, 1))
                speeds.append(round(speed, 2))
                runs.append(stats["runs"])
        
        return {
            "labels": labels,
            "success_rate": success_rates,
            "speed": speeds,
            "runs": runs
        }
    
    def get_domain_distribution(self) -> Dict:
        """
        Distribución de tests por dominio
        
        Returns:
            {
                "labels": ["github.com", "amazon.com", ...],
                "data": [15, 8, 5, ...]
            }
        """
        results = self.load_results()
        
        domain_counts = defaultdict(int)
        
        for result in results:
            url = result.get("url", "")
            if url:
                # Extrae dominio
                from urllib.parse import urlparse
                domain = urlparse(url).netloc
                domain_counts[domain] += 1
        
        # Top 10 dominios
        sorted_domains = sorted(
            domain_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        labels = [d[0] for d in sorted_domains]
        data = [d[1] for d in sorted_domains]
        
        return {
            "labels": labels,
            "data": data
        }
    
    def get_mode_distribution(self) -> Dict:
        """
        Distribución por modo (speed/balanced/quality)
        
        Returns:
            {
                "labels": ["speed", "balanced", "quality"],
                "data": [15, 25, 10],
                "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1"]
            }
        """
        results = self.load_results()
        
        mode_counts = defaultdict(int)
        
        for result in results:
            mode = result.get("mode", "balanced")
            mode_counts[mode] += 1
        
        colors = {
            "speed": "#FF6B6B",
            "balanced": "#4ECDC4",
            "quality": "#45B7D1"
        }
        
        labels = []
        data = []
        colors_list = []
        
        for mode in ["speed", "balanced", "quality"]:
            if mode_counts[mode] > 0:
                labels.append(mode)
                data.append(mode_counts[mode])
                colors_list.append(colors[mode])
        
        return {
            "labels": labels,
            "data": data,
            "colors": colors_list
        }
    
    def get_summary_stats(self) -> Dict:
        """
        Estadísticas resumidas
        
        Returns:
            {
                "total_tests": 42,
                "avg_pass_rate": 93.5,
                "avg_duration": 35.2,
                "total_time_saved": 1250.4
            }
        """
        results = self.load_results()
        
        if not results:
            return {
                "total_tests": 0,
                "avg_pass_rate": 0,
                "avg_duration": 0,
                "total_time_saved": 0,
                "best_model": "N/A",
                "domains": 0
            }
        
        # Calcula métricas
        pass_rates = [r.get("pass_rate", 0) for r in results]
        durations = [r.get("duration", 0) for r in results]
        
        # Dominios únicos
        domains = set()
        for result in results:
            url = result.get("url", "")
            if url:
                from urllib.parse import urlparse
                domain = urlparse(url).netloc
                domains.add(domain)
        
        # Mejor modelo
        learning = self.load_learning()
        best_model = "N/A"
        best_success = 0
        
        for domain, models in learning.get("by_domain", {}).items():
            for model, stats in models.items():
                if stats["runs"] > 0:
                    success = stats["successes"] / stats["runs"]
                    if success > best_success:
                        best_success = success
                        best_model = model
        
        return {
            "total_tests": len(results),
            "avg_pass_rate": round(statistics.mean(pass_rates), 1) if pass_rates else 0,
            "avg_duration": round(statistics.mean(durations), 1) if durations else 0,
            "total_time_saved": round(sum(durations), 1),
            "best_model": best_model,
            "domains": len(domains)
        }
    
    def calculate_roi(self, manual_test_hours: float = 100) -> Dict:
        """
        Calcula ROI
        
        Args:
            manual_test_hours: Horas de testing manual que ahorraría
        
        Returns:
            {
                "total_tests": 42,
                "hours_per_test_automated": 0.5,
                "hours_per_test_manual": 2,
                "hours_saved": 315,
                "cost_saved": "$6300",
                "roi_percentage": 525,
                "payback_period_days": 14
            }
        """
        results = self.load_results()
        total_tests = len(results)
        
        if total_tests == 0:
            total_tests = 1
        
        # Duración promedio
        durations = [r.get("duration", 0) for r in results]
        avg_duration = statistics.mean(durations) if durations else 30
        
        # Conversiones
        hours_per_test_automated = avg_duration / 3600  # A horas
        hours_per_test_manual = 0.5  # Estimation: 30 min manual
        
        # Cálculos
        time_saved = (hours_per_test_manual - hours_per_test_automated) * total_tests
        
        # Costos (estimación)
        hourly_rate = 50  # $/hora
        cost_saved = time_saved * hourly_rate
        
        # Setup cost (aproximado)
        setup_hours = 20
        setup_cost = setup_hours * hourly_rate
        
        # ROI
        net_savings = cost_saved - setup_cost
        roi_percentage = (net_savings / setup_cost * 100) if setup_cost > 0 else 0
        
        # Payback period
        monthly_savings = (cost_saved / 30)  # daily
        payback_days = setup_cost / monthly_savings if monthly_savings > 0 else 0
        
        return {
            "total_tests": total_tests,
            "avg_duration_seconds": round(avg_duration, 1),
            "hours_per_test_automated": round(hours_per_test_automated, 2),
            "hours_per_test_manual": hours_per_test_manual,
            "hours_saved": round(time_saved, 1),
            "cost_saved": f"${cost_saved:,.0f}",
            "setup_cost": f"${setup_cost:,.0f}",
            "net_savings": f"${net_savings:,.0f}",
            "roi_percentage": round(roi_percentage, 1),
            "payback_period_days": round(payback_days, 1)
        }
    
    def get_all_data(self) -> Dict:
        """
        Retorna todos los datos para el dashboard
        """
        return {
            "summary": self.get_summary_stats(),
            "pass_rate_trend": self.get_pass_rate_trend(),
            "model_performance": self.get_model_performance(),
            "domain_distribution": self.get_domain_distribution(),
            "mode_distribution": self.get_mode_distribution(),
            "roi": self.calculate_roi()
        }
