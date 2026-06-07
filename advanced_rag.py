"""
Advanced RAG - Clustering, Transfer Learning, Defect Prediction
Nivel 2: Máximo valor - Diferencial técnico
"""

import json
from typing import List, Dict, Tuple
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np
from rich.console import Console
from model_learner import ModelLearner
from urllib.parse import urlparse

console = Console()


class AdvancedRAG:
    """
    RAG avanzado con:
    - Clustering automático de dominios similares
    - Transfer learning entre dominios
    - Predicción de defectos
    - Recomendaciones inteligentes
    """
    
    ADVANCED_DATA_FILE = "advanced_rag_data.json"
    
    def __init__(self):
        self.learner = ModelLearner()
        self.advanced_data = self._load_advanced_data()
        self.clusters = None
    
    def _load_advanced_data(self) -> Dict:
        """Carga datos avanzados"""
        if Path(self.ADVANCED_DATA_FILE).exists():
            try:
                with open(self.ADVANCED_DATA_FILE, 'r') as f:
                    return json.load(f)
            except:
                return self._empty_advanced_data()
        return self._empty_advanced_data()
    
    def _empty_advanced_data(self) -> Dict:
        """Estructura vacía"""
        return {
            "domain_clusters": {},
            "defect_predictions": {},
            "transfer_learning": {},
            "insights": []
        }
    
    def _save_advanced_data(self) -> None:
        """Guarda datos avanzados"""
        with open(self.ADVANCED_DATA_FILE, 'w') as f:
            json.dump(self.advanced_data, f, indent=2)
    
    def cluster_domains(self, n_clusters: int = 3) -> Dict:
        """
        Agrupa dominios similares automáticamente
        
        Usa: 
        - Historial de tests
        - Éxito rate
        - Tiempo promedio
        - Tipos de errores
        
        Returns:
            Dict con clusters y dominios
        """
        stats = self.learner.get_stats()
        
        if len(stats["domains_learned"]) < 3:
            console.print("[yellow]⚠ Necesitas al menos 3 dominios para clustering[/yellow]")
            return {}
        
        # Extrae features
        domains = list(stats["by_domain"].keys())
        features = []
        
        for domain in domains:
            domain_data = stats["by_domain"][domain]
            
            # Features para clustering
            avg_success_rate = np.mean([
                (data["successes"] / max(data["runs"], 1)) * 100
                for data in domain_data.values()
            ])
            
            avg_time = np.mean([
                data["total_time"] / max(data["runs"], 1)
                for data in domain_data.values()
            ])
            
            total_tests = sum(data["runs"] for data in domain_data.values())
            
            features.append([avg_success_rate, avg_time, total_tests])
        
        # Normaliza
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Clustering
        n_clusters = min(n_clusters, len(domains))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(features_scaled)
        
        # Agrupa
        clusters = {f"cluster_{i}": [] for i in range(n_clusters)}
        for domain, label in zip(domains, labels):
            clusters[f"cluster_{label}"].append(domain)
        
        self.advanced_data["domain_clusters"] = clusters
        self._save_advanced_data()
        
        return clusters
    
    def predict_defects(self, url: str, objective: str) -> Dict:
        """
        Predice defectos probables basado en histórico
        
        Returns:
            {
                "risk_level": "high/medium/low",
                "probable_defects": [...],
                "recommended_checks": [...],
                "confidence": 0.0-1.0
            }
        """
        domain = urlparse(url).netloc
        stats = self.learner.get_stats()
        
        if domain not in stats["by_domain"]:
            return {
                "risk_level": "unknown",
                "probable_defects": [],
                "recommended_checks": [],
                "confidence": 0.0
            }
        
        domain_data = stats["by_domain"][domain]
        
        # Calcula risk
        success_rates = []
        for model_data in domain_data.values():
            if model_data["runs"] > 0:
                success_rate = (model_data["successes"] / model_data["runs"]) * 100
                success_rates.append(success_rate)
        
        avg_success = np.mean(success_rates) if success_rates else 50
        
        # Determina risk level
        if avg_success > 90:
            risk_level = "low"
            confidence = 0.9
        elif avg_success > 75:
            risk_level = "medium"
            confidence = 0.7
        else:
            risk_level = "high"
            confidence = 0.85
        
        # Defectos probables
        probable_defects = []
        if risk_level == "high":
            probable_defects = [
                "Timeouts en carga",
                "Elementos no encontrados",
                "JavaScript no ejecutado",
                "Redirects inesperados"
            ]
        elif risk_level == "medium":
            probable_defects = [
                "Elementos lentos",
                "Validaciones fuertes",
                "Estados no esperados"
            ]
        
        # Checks recomendados
        recommended_checks = [
            "✓ Aumentar timeouts",
            "✓ Verificar JavaScript",
            "✓ Check de redirects",
            "✓ Wait explícito para elementos",
            "✓ Captura de screenshots"
        ]
        
        return {
            "risk_level": risk_level,
            "probable_defects": probable_defects,
            "recommended_checks": recommended_checks,
            "confidence": confidence,
            "historical_success_rate": avg_success
        }
    
    def transfer_learning(self, source_domain: str, target_domain: str) -> Dict:
        """
        Transfer learning: aplica patrones exitosos de un dominio a otro
        
        Ejemplo:
        - source: github.com (dominio bien conocido)
        - target: gitlab.com (dominio nuevo, similar)
        
        Returns:
            Recomendaciones basadas en dominio similar
        """
        stats = self.learner.get_stats()
        
        source_data = stats["by_domain"].get(source_domain)
        target_data = stats["by_domain"].get(target_domain)
        
        if not source_data:
            return {"status": "source_not_found"}
        
        if not target_data:
            # Usa fuente directamente
            best_model = max(
                source_data.items(),
                key=lambda x: x[1]["successes"] / max(x[1]["runs"], 1)
            )[0]
            
            return {
                "source_domain": source_domain,
                "target_domain": target_domain,
                "recommended_model": best_model,
                "rationale": f"Transfieren knowledge de {source_domain}",
                "expected_success_rate": 0.85,
                "transfer_feasibility": "high"
            }
        
        # Compara similarity
        source_success = max(
            d["successes"] / max(d["runs"], 1)
            for d in source_data.values()
        )
        
        target_success = max(
            d["successes"] / max(d["runs"], 1)
            for d in target_data.values()
        )
        
        similarity = 1 - abs(source_success - target_success)
        
        return {
            "source_domain": source_domain,
            "target_domain": target_domain,
            "similarity": similarity,
            "transfer_feasibility": "high" if similarity > 0.7 else "medium",
            "insights": [
                f"{source_domain} tiene {source_success*100:.1f}% success rate",
                f"{target_domain} tiene {target_success*100:.1f}% success rate",
                f"Transferencia viable: {similarity*100:.1f}%"
            ]
        }
    
    def get_recommendations(self, url: str, objective: str) -> List[str]:
        """
        Recomendaciones inteligentes basadas en:
        - Clustering
        - Predicción de defectos
        - Transfer learning
        - Histórico
        """
        recommendations = []
        domain = urlparse(url).netloc
        
        # Predice defectos
        defects = self.predict_defects(url, objective)
        if defects["risk_level"] == "high":
            recommendations.append(f"⚠️ Risk level alto ({defects['confidence']*100:.0f}% confianza)")
            for defect in defects["probable_defects"][:2]:
                recommendations.append(f"  • Probable: {defect}")
        
        # Clustering insights
        clusters = self.cluster_domains()
        for cluster_name, domains in clusters.items():
            if domain in domains:
                similar_domains = [d for d in domains if d != domain]
                if similar_domains:
                    recommendations.append(f"🔗 Dominios similares: {', '.join(similar_domains[:2])}")
        
        # Transfer learning
        if clusters and domain not in stats.get("by_domain", {}):
            for cluster_name, domains in clusters.items():
                if domains:
                    transfer = self.transfer_learning(domains[0], domain)
                    if "recommended_model" in transfer:
                        recommendations.append(f"📚 Transfer learning: usar {transfer['recommended_model']}")
        
        return recommendations if recommendations else ["✓ Setup óptimo detectado"]
    
    def print_analysis(self, url: str, objective: str) -> None:
        """Imprime análisis completo"""
        from rich.table import Table
        from rich.panel import Panel
        
        console.print(Panel(
            f"[bold cyan]Advanced RAG Analysis[/bold cyan]\n{url}",
            style="cyan"
        ))
        
        # Defectos
        defects = self.predict_defects(url, objective)
        console.print(f"\n[cyan]Risk Level:[/cyan] {defects['risk_level'].upper()}")
        console.print(f"[cyan]Confianza:[/cyan] {defects['confidence']*100:.0f}%")
        
        if defects["probable_defects"]:
            console.print("\n[cyan]Defectos Probables:[/cyan]")
            for d in defects["probable_defects"]:
                console.print(f"  • {d}")
        
        # Recomendaciones
        recommendations = self.get_recommendations(url, objective)
        console.print("\n[cyan]Recomendaciones:[/cyan]")
        for rec in recommendations[:5]:
            console.print(f"  {rec}")
        
        # Clustering
        clusters = self.cluster_domains()
        if clusters:
            console.print("\n[cyan]Domain Clusters:[/cyan]")
            for cluster_name, domains in clusters.items():
                console.print(f"  {cluster_name}: {', '.join(domains)}")


if __name__ == "__main__":
    print("=== Advanced RAG ===\n")
    
    rag = AdvancedRAG()
    
    # Ejemplo
    rag.print_analysis("https://github.com", "Testear repositorio")
