"""
CLI Enhancements - Advanced command line interface for Smart Test
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from tabulate import tabulate
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import csv

from stats_service import StatsService

console = Console()


class CLIEnhancer:
    """
    Advanced CLI commands for Smart Test
    """
    
    def __init__(self):
        self.config_dir = Path.home() / ".smarttest"
        self.cache_dir = self.config_dir / "cache"
        self.history_file = self.config_dir / "history.json"
        self.config_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
    
    # ==================== CONFIG COMMANDS ====================
    
    def config_save(self, config_name: str, config_data: Dict) -> bool:
        """
        Save configuration to file
        
        Usage: smart-test config save test-config
        """
        config_file = self.config_dir / f"{config_name}.json"
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            console.print(f"[green]✅ Config saved: {config_file}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]❌ Error saving config: {str(e)}[/red]")
            return False
    
    def config_load(self, config_name: str) -> Optional[Dict]:
        """
        Load configuration from file
        
        Usage: smart-test config load test-config
        """
        config_file = self.config_dir / f"{config_name}.json"
        
        if not config_file.exists():
            console.print(f"[red]❌ Config not found: {config_name}[/red]")
            return None
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            console.print(f"[green]✅ Config loaded: {config_name}[/green]")
            return config
        except Exception as e:
            console.print(f"[red]❌ Error loading config: {str(e)}[/red]")
            return None
    
    def config_list(self) -> None:
        """
        List all saved configurations
        
        Usage: smart-test config list
        """
        configs = list(self.config_dir.glob("*.json"))
        
        if not configs:
            console.print("[yellow]No saved configurations[/yellow]")
            return
        
        table = Table(title="Saved Configurations")
        table.add_column("Name", style="cyan")
        table.add_column("Size", style="magenta")
        table.add_column("Modified", style="green")
        
        for config_file in configs:
            name = config_file.stem
            size = f"{config_file.stat().st_size} bytes"
            modified = datetime.fromtimestamp(config_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            table.add_row(name, size, modified)
        
        console.print(table)
    
    # ==================== HISTORY COMMANDS ====================
    
    def history_add(self, result: Dict) -> None:
        """Add result to history"""
        history = self._load_history()
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "url": result.get("url"),
            "objective": result.get("objective"),
            "pass_rate": result.get("pass_rate"),
            "duration": result.get("duration"),
            "mode": result.get("mode"),
            "model": result.get("model"),
            "status": result.get("status")
        }
        
        history.append(entry)
        self._save_history(history)
    
    def history_list(self, last_n: int = 10) -> None:
        """
        List test history
        
        Usage: smart-test history --last 10
        """
        history = self._load_history()
        
        if not history:
            console.print("[yellow]No history[/yellow]")
            return
        
        # Get last N
        recent = history[-last_n:]
        
        table = Table(title=f"Last {last_n} Tests")
        table.add_column("URL", style="cyan", width=30)
        table.add_column("Pass Rate", style="magenta", width=12)
        table.add_column("Duration", style="green", width=10)
        table.add_column("Mode", style="yellow", width=10)
        table.add_column("Timestamp", style="blue", width=20)
        
        for entry in reversed(recent):
            url = entry.get("url", "N/A")[:30]
            pass_rate = f"{entry.get('pass_rate', 0):.1f}%"
            duration = f"{entry.get('duration', 0):.1f}s"
            mode = entry.get("mode", "N/A")
            timestamp = entry.get("timestamp", "")[:19]
            table.add_row(url, pass_rate, duration, mode, timestamp)
        
        console.print(table)
    
    def history_clear(self) -> None:
        """Clear all history"""
        if self.history_file.exists():
            self.history_file.unlink()
            console.print("[green]✅ History cleared[/green]")
    
    def _load_history(self) -> List[Dict]:
        """Load history from file"""
        if not self.history_file.exists():
            return []
        
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _save_history(self, history: List[Dict]) -> None:
        """Save history to file"""
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    # ==================== COMPARE COMMANDS ====================
    
    def compare_models(self, model1: str, model2: str, last_n: int = 10) -> None:
        """
        Compare performance of two models
        
        Usage: smart-test compare mistral vs neural-chat
        """
        history = self._load_history()
        
        # Filter by models
        results1 = [h for h in history if h.get("model") == model1]
        results2 = [h for h in history if h.get("model") == model2]
        
        if not results1 or not results2:
            console.print("[red]❌ Insufficient data for comparison[/red]")
            return
        
        # Get last N
        results1 = results1[-last_n:]
        results2 = results2[-last_n:]
        
        # Calculate stats
        stats1 = self._calculate_stats(results1)
        stats2 = self._calculate_stats(results2)
        
        # Display comparison
        table = Table(title=f"Model Comparison: {model1} vs {model2}")
        table.add_column("Metric", style="cyan")
        table.add_column(model1, style="magenta")
        table.add_column(model2, style="green")
        table.add_column("Winner", style="yellow")
        
        metrics = [
            ("Avg Pass Rate", f"{stats1['avg_pass_rate']:.1f}%", f"{stats2['avg_pass_rate']:.1f}%", 
             model1 if stats1['avg_pass_rate'] > stats2['avg_pass_rate'] else model2),
            ("Avg Duration", f"{stats1['avg_duration']:.1f}s", f"{stats2['avg_duration']:.1f}s",
             model2 if stats1['avg_duration'] > stats2['avg_duration'] else model1),
            ("Tests Run", str(stats1['count']), str(stats2['count']), "—"),
        ]
        
        for metric, val1, val2, winner in metrics:
            table.add_row(metric, val1, val2, winner)
        
        console.print(table)
    
    def _calculate_stats(self, results: List[Dict]) -> Dict:
        """Calculate statistics from results (delegates to StatsService)"""
        summary = StatsService.summarize(
            pass_rates=[r.get("pass_rate", 0) for r in results],
            durations=[r.get("duration", 0) for r in results],
        )
        return {
            "avg_pass_rate": summary["avg_pass_rate"],
            "avg_duration": summary["avg_duration"],
            "count": summary["total_tests"],
        }
    
    # ==================== EXPORT COMMANDS ====================
    
    def export_csv(self, output_file: str, last_n: int = None) -> bool:
        """
        Export history to CSV
        
        Usage: smart-test export --csv results.csv
        """
        history = self._load_history()
        
        if not history:
            console.print("[yellow]No data to export[/yellow]")
            return False
        
        if last_n:
            history = history[-last_n:]
        
        try:
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "timestamp", "url", "objective", "pass_rate", 
                    "duration", "mode", "model", "status"
                ])
                writer.writeheader()
                writer.writerows(history)
            
            console.print(f"[green]✅ Exported to {output_file}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]❌ Export failed: {str(e)}[/red]")
            return False
    
    def export_json(self, output_file: str, last_n: int = None) -> bool:
        """
        Export history to JSON
        
        Usage: smart-test export --json results.json
        """
        history = self._load_history()
        
        if not history:
            console.print("[yellow]No data to export[/yellow]")
            return False
        
        if last_n:
            history = history[-last_n:]
        
        try:
            with open(output_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            console.print(f"[green]✅ Exported to {output_file}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]❌ Export failed: {str(e)}[/red]")
            return False
    
    # ==================== STATS COMMANDS ====================
    
    def stats_summary(self, period: str = "all") -> None:
        """
        Show summary statistics
        
        Usage: smart-test stats --last-week
        """
        history = self._load_history()
        
        if not history:
            console.print("[yellow]No data available[/yellow]")
            return
        
        # Filter by period
        if period == "week":
            cutoff = datetime.now() - timedelta(days=7)
            history = [h for h in history 
                      if datetime.fromisoformat(h.get("timestamp", "")) > cutoff]
        elif period == "month":
            cutoff = datetime.now() - timedelta(days=30)
            history = [h for h in history 
                      if datetime.fromisoformat(h.get("timestamp", "")) > cutoff]
        
        if not history:
            console.print("[yellow]No data for this period[/yellow]")
            return
        
        # Calculate stats via the shared service
        summary = StatsService.summarize(
            pass_rates=[h.get("pass_rate", 0) for h in history],
            durations=[h.get("duration", 0) for h in history],
        )

        stats = {
            "Total Tests": summary["total_tests"],
            "Avg Pass Rate": f"{summary['avg_pass_rate']:.1f}%",
            "Avg Duration": f"{summary['avg_duration']:.1f}s",
            "Min Pass Rate": f"{summary['min_pass_rate']:.1f}%",
            "Max Pass Rate": f"{summary['max_pass_rate']:.1f}%",
            "Time Range": f"{history[0].get('timestamp', '')[:10]} to {history[-1].get('timestamp', '')[:10]}"
        }
        
        # Display in panel
        stats_text = "\n".join([f"{k}: {v}" for k, v in stats.items()])
        console.print(Panel(stats_text, title="Test Statistics"))
    
    # ==================== CACHE COMMANDS ====================
    
    def clear_cache(self) -> None:
        """
        Clear local cache
        
        Usage: smart-test clear-cache
        """
        import shutil
        try:
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir()
            console.print("[green]✅ Cache cleared[/green]")
        except Exception as e:
            console.print(f"[red]❌ Error clearing cache: {str(e)}[/red]")


def register_cli_commands(parser):
    """Register all CLI commands to argparse"""
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Config commands
    config_parser = subparsers.add_parser("config", help="Manage configurations")
    config_sub = config_parser.add_subparsers(dest="config_cmd")
    config_sub.add_parser("save", help="Save current config")
    config_sub.add_parser("load", help="Load saved config")
    config_sub.add_parser("list", help="List saved configs")
    
    # History commands
    history_parser = subparsers.add_parser("history", help="View test history")
    history_sub = history_parser.add_subparsers(dest="history_cmd")
    history_list = history_sub.add_parser("list", help="List history")
    history_list.add_argument("--last", type=int, default=10, help="Last N entries")
    history_sub.add_parser("clear", help="Clear history")
    
    # Compare commands
    compare_parser = subparsers.add_parser("compare", help="Compare models")
    compare_parser.add_argument("model1", help="First model")
    compare_parser.add_argument("vs", help="vs")
    compare_parser.add_argument("model2", help="Second model")
    compare_parser.add_argument("--last", type=int, default=10, help="Last N tests")
    
    # Export commands
    export_parser = subparsers.add_parser("export", help="Export results")
    export_parser.add_argument("format", choices=["csv", "json"], help="Export format")
    export_parser.add_argument("output", help="Output file")
    export_parser.add_argument("--last", type=int, help="Last N entries")
    
    # Stats commands
    stats_parser = subparsers.add_parser("stats", help="Show statistics")
    stats_parser.add_argument("--period", choices=["all", "week", "month"], 
                             default="all", help="Time period")
    
    # Cache commands
    subparsers.add_parser("clear-cache", help="Clear local cache")


if __name__ == "__main__":
    cli = CLIEnhancer()
    
    # Test commands
    cli.config_list()
    cli.history_list(5)
    cli.stats_summary()
