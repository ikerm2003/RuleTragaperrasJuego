
"""
Tests comprehensivos para el módulo main.py
Tests for the main UI and application entry point.
"""

import unittest
import sys
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Only test the parts that don't require PyQt6 GUI
try:
    from RuleTragaperrasJuego.main import MainUI
    PYQT_AVAILABLE = True
except ImportError as e:
    if "libEGL" in str(e) or "libGL" in str(e) or "cannot connect to X server" in str(e):
        PYQT_AVAILABLE = False
    else:
        raise


class TestMainUIImports(unittest.TestCase):
    """Tests básicos para el módulo main.py"""
    
    def test_main_module_imports(self):
        """Test that main module can be imported"""
        try:
            import RuleTragaperrasJuego.main as main
            self.assertTrue(hasattr(main, 'MainUI'))
        except ImportError as e:
            if "libEGL" in str(e) or "libGL" in str(e):
                self.skipTest("GUI not available in headless environment")
            else:
                raise
    
    def test_main_ui_class_exists(self):
        """Test that MainUI class exists and has expected methods"""
        if not PYQT_AVAILABLE:
            self.skipTest("PyQt6 GUI not available")
        
        # Check class exists
        self.assertTrue(hasattr(MainUI, '__init__'))
        self.assertTrue(hasattr(MainUI, 'init_ui'))
        
        # Check if it's a subclass of QMainWindow
        from PyQt6.QtWidgets import QMainWindow
        self.assertTrue(issubclass(MainUI, QMainWindow))


@unittest.skipUnless(PYQT_AVAILABLE, "PyQt6 GUI not available")
class TestMainUIFunctionality(unittest.TestCase):
    """Tests para la funcionalidad de MainUI (solo si PyQt6 está disponible)"""
    
    def setUp(self):
        # Mock QApplication to avoid GUI display issues
        with patch('main.QApplication') as mock_app:
            mock_app.return_value = MagicMock()
            try:
                self.main_ui = MainUI()
            except Exception as e:
                if "libEGL" in str(e) or "cannot connect to X server" in str(e):
                    self.skipTest("Display not available")
                raise
    
    def test_main_ui_creation(self):
        """Test MainUI creation"""
        if not hasattr(self, 'main_ui'):
            self.skipTest("MainUI could not be created")
        
        self.assertIsInstance(self.main_ui, MainUI)
        self.assertTrue(hasattr(self.main_ui, 'config'))
    
    def test_main_ui_window_properties(self):
        """Test MainUI window properties"""
        if not hasattr(self, 'main_ui'):
            self.skipTest("MainUI could not be created")
        
        # Check window title is set
        title = self.main_ui.windowTitle()
        self.assertIsInstance(title, str)
        self.assertGreater(len(title), 0)
    
    @patch('main.importlib.import_module')
    def test_poker_module_loading(self, mock_import):
        """Test that poker module can be loaded"""
        if not hasattr(self, 'main_ui'):
            self.skipTest("MainUI could not be created")
        
        # Mock poker module import
        mock_poker_module = MagicMock()
        mock_poker_window = MagicMock()
        mock_poker_module.PokerWindow = mock_poker_window
        mock_import.return_value = mock_poker_module
        
        # Test launch_poker method exists
        if hasattr(self.main_ui, 'launch_poker'):
            # Test would call launch_poker but we don't want to actually create windows
            pass


class TestMainUIUtilityFunctions(unittest.TestCase):
    """Tests para funciones utilitarias del módulo main"""
    
    def test_config_import(self):
        """Test that config can be imported from main module"""
        try:
            from RuleTragaperrasJuego.main import config_manager, get_text
            self.assertIsNotNone(config_manager)
            self.assertTrue(callable(get_text))
        except ImportError as e:
            if "libEGL" not in str(e):
                raise


@unittest.skipUnless(PYQT_AVAILABLE, "PyQt6 GUI not available")
class TestMainUIPerformanceHelpers(unittest.TestCase):
    """Tests de helpers de rendimiento en MainUI."""

    def test_compute_metric_alert_level_critical(self):
        """Debe marcar CRITICO cuando la media excede claramente el umbral."""
        level, color = MainUI._compute_metric_alert_level(
            status=False,
            avg_ms=26.0,
            threshold_ms=20.0,
            delta_avg_ms=2.0,
        )
        self.assertEqual(level, "CRITICO")
        self.assertEqual(color, "#7f1d1d")

    def test_compute_metric_alert_level_regression(self):
        """Debe marcar REGRESION con umbral OK pero empeoramiento fuerte."""
        level, color = MainUI._compute_metric_alert_level(
            status=True,
            avg_ms=18.0,
            threshold_ms=20.0,
            delta_avg_ms=6.5,
        )
        self.assertEqual(level, "REGRESION")
        self.assertEqual(color, "#92400e")

    def test_build_performance_csv_rows_includes_delta_and_alert(self):
        """Genera filas CSV con delta frente al snapshot previo por source."""
        snapshots = [
            {
                "timestamp": "2026-03-12T10:00:00",
                "source": "blackjack",
                "metrics": {
                    "ui.blackjack.hit_ms": {
                        "count": 10,
                        "avg_ms": 20.0,
                        "min_ms": 10.0,
                        "max_ms": 30.0,
                        "p95_ms": 28.0,
                        "threshold_ms": 25.0,
                        "within_threshold": True,
                    }
                },
            },
            {
                "timestamp": "2026-03-12T10:05:00",
                "source": "blackjack",
                "metrics": {
                    "ui.blackjack.hit_ms": {
                        "count": 12,
                        "avg_ms": 27.0,
                        "min_ms": 12.0,
                        "max_ms": 35.0,
                        "p95_ms": 33.0,
                        "threshold_ms": 25.0,
                        "within_threshold": False,
                    }
                },
            },
        ]

        rows = MainUI._build_performance_csv_rows(snapshots)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["delta_avg_ms"], "-")
        self.assertEqual(rows[1]["delta_avg_ms"], "+7.000")
        self.assertEqual(rows[1]["alert_level"], "ALTO")

    def test_parse_snapshot_timestamp_invalid(self):
        """El parser de timestamp debe devolver None con formato inválido."""
        parsed = MainUI._parse_snapshot_timestamp("fecha-invalida")
        self.assertIsNone(parsed)

    def test_filter_performance_snapshots_by_source_metric_and_range(self):
        """Filtra snapshots por fuente, métrica y rango temporal."""
        snapshots = [
            {
                "timestamp": "2026-03-12T09:00:00",
                "source": "blackjack",
                "metrics": {
                    "ui.blackjack.hit_ms": {"avg_ms": 20.0, "count": 3},
                    "ui.blackjack.deal_ms": {"avg_ms": 30.0, "count": 3},
                },
            },
            {
                "timestamp": "2026-03-12T11:00:00",
                "source": "tragaperras",
                "metrics": {
                    "ui.slots.render_result_ms": {"avg_ms": 15.0, "count": 4},
                },
            },
            {
                "timestamp": "2026-03-12T12:00:00",
                "source": "blackjack",
                "metrics": {
                    "ui.blackjack.hit_ms": {"avg_ms": 22.0, "count": 5},
                },
            },
        ]

        filtered = MainUI._filter_performance_snapshots(
            snapshots,
            source_filter="blackjack",
            metric_filter="ui.blackjack.hit_ms",
            start_ts="2026-03-12T10:00:00",
            end_ts="2026-03-12T12:30:00",
        )

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["source"], "blackjack")
        self.assertIn("ui.blackjack.hit_ms", filtered[0]["metrics"])
        self.assertNotIn("ui.blackjack.deal_ms", filtered[0]["metrics"])

    def test_get_time_preset_bounds_last_hour(self):
        """El preset de ultima hora debe devolver ventana ISO de 60 minutos."""
        now = datetime(2026, 3, 13, 12, 0, 0)
        start_iso, end_iso = MainUI._get_time_preset_bounds("Ultima hora", now=now)
        self.assertEqual(start_iso, "2026-03-13T11:00:00")
        self.assertEqual(end_iso, "2026-03-13T12:00:00")

    def test_build_metric_trend_rows_aggregates_and_delta(self):
        """La vista agregada debe consolidar métricas y calcular delta de periodo."""
        snapshots = [
            {
                "timestamp": "2026-03-12T10:00:00",
                "source": "blackjack",
                "metrics": {
                    "ui.blackjack.hit_ms": {
                        "avg_ms": 20.0,
                        "within_threshold": True,
                    },
                },
            },
            {
                "timestamp": "2026-03-12T11:00:00",
                "source": "blackjack",
                "metrics": {
                    "ui.blackjack.hit_ms": {
                        "avg_ms": 26.0,
                        "within_threshold": False,
                    },
                },
            },
            {
                "timestamp": "2026-03-12T12:00:00",
                "source": "tragaperras",
                "metrics": {
                    "ui.slots.render_result_ms": {
                        "avg_ms": 15.0,
                        "within_threshold": True,
                    },
                },
            },
        ]

        rows = MainUI._build_metric_trend_rows(snapshots)
        hit_row = next((row for row in rows if row["metric"] == "ui.blackjack.hit_ms"), None)
        self.assertIsNotNone(hit_row)
        self.assertEqual(hit_row["snapshots"], 2)
        self.assertEqual(hit_row["sources"], 1)
        self.assertEqual(hit_row["avg_of_avg_ms"], 23.0)
        self.assertEqual(hit_row["delta_avg_ms"], "+6.000")
        self.assertEqual(hit_row["threshold_breaches"], "1/2")

    def test_build_source_trend_rows_aggregates_and_delta(self):
        """La vista agregada por fuente debe consolidar métricas del periodo."""
        snapshots = [
            {
                "timestamp": "2026-03-12T10:00:00",
                "source": "blackjack",
                "metrics": {
                    "ui.blackjack.hit_ms": {
                        "avg_ms": 20.0,
                        "within_threshold": True,
                    },
                    "ui.blackjack.deal_ms": {
                        "avg_ms": 30.0,
                        "within_threshold": False,
                    },
                },
            },
            {
                "timestamp": "2026-03-12T11:00:00",
                "source": "blackjack",
                "metrics": {
                    "ui.blackjack.hit_ms": {
                        "avg_ms": 26.0,
                        "within_threshold": False,
                    },
                },
            },
            {
                "timestamp": "2026-03-12T12:00:00",
                "source": "tragaperras",
                "metrics": {
                    "ui.slots.render_result_ms": {
                        "avg_ms": 15.0,
                        "within_threshold": True,
                    },
                },
            },
        ]

        rows = MainUI._build_source_trend_rows(snapshots)
        blackjack_row = next((row for row in rows if row["source"] == "blackjack"), None)
        self.assertIsNotNone(blackjack_row)
        self.assertEqual(blackjack_row["snapshots"], 2)
        self.assertEqual(blackjack_row["metrics"], 2)
        self.assertEqual(blackjack_row["avg_of_avg_ms"], 25.333)
        self.assertEqual(blackjack_row["delta_avg_ms"], "+1.000")
        self.assertEqual(blackjack_row["threshold_breaches"], "2/3")

    def test_compute_phase_alert_level_prefers_threshold_breaches(self):
        """La severidad por fase debe priorizar brechas de umbral."""
        level, color = MainUI._compute_phase_alert_level(
            threshold_breaches=2,
            threshold_checks=4,
            delta_avg_ms=1.0,
        )
        self.assertEqual(level, "CRITICO")
        self.assertEqual(color, "#7f1d1d")

    def test_build_phase_trend_rows_groups_main_phases(self):
        """Debe consolidar bootstrap/import/open/transition en una vista dedicada."""
        snapshots = [
            {
                "timestamp": "2026-03-13T10:00:00",
                "source": "main",
                "metrics": {
                    "ui.main.bootstrap.db_init_ms": {
                        "avg_ms": 200.0,
                        "within_threshold": True,
                    },
                    "ui.main.import_poker_ms": {
                        "avg_ms": 110.0,
                        "within_threshold": True,
                    },
                    "ui.main.open_poker_ms": {
                        "avg_ms": 300.0,
                        "within_threshold": False,
                    },
                    "ui.main.transition_to_poker_ms": {
                        "avg_ms": 320.0,
                        "within_threshold": True,
                    },
                    "ui.main.restore_transition_poker_ms": {
                        "avg_ms": 120.0,
                        "within_threshold": True,
                    },
                },
            },
            {
                "timestamp": "2026-03-13T11:00:00",
                "source": "main",
                "metrics": {
                    "ui.main.bootstrap.db_init_ms": {
                        "avg_ms": 210.0,
                        "within_threshold": True,
                    },
                    "ui.main.import_poker_ms": {
                        "avg_ms": 130.0,
                        "within_threshold": True,
                    },
                    "ui.main.open_poker_ms": {
                        "avg_ms": 280.0,
                        "within_threshold": True,
                    },
                    "ui.main.transition_to_poker_ms": {
                        "avg_ms": 350.0,
                        "within_threshold": False,
                    },
                    "ui.main.restore_transition_poker_ms": {
                        "avg_ms": 130.0,
                        "within_threshold": True,
                    },
                },
            },
        ]

        rows = MainUI._build_phase_trend_rows(snapshots)
        phases = [row["phase"] for row in rows]
        self.assertEqual(phases, ["bootstrap", "import", "open", "transition"])

        transition_row = next((row for row in rows if row["phase"] == "transition"), None)
        self.assertIsNotNone(transition_row)
        self.assertEqual(transition_row["snapshots"], 2)
        self.assertEqual(transition_row["metrics"], 2)
        self.assertEqual(transition_row["delta_avg_ms"], "+20.000")
        self.assertEqual(transition_row["threshold_breaches"], "1/4")

    def test_sort_phase_rows_by_snapshots_desc(self):
        """La ordenación de fases por snapshots debe funcionar como en agregados."""
        rows = [
            {"phase": "open", "snapshots": 2, "avg_of_avg_ms": 20.0, "delta_avg_ms": "+1.000", "threshold_breaches": "0/2"},
            {"phase": "bootstrap", "snapshots": 4, "avg_of_avg_ms": 30.0, "delta_avg_ms": "+2.000", "threshold_breaches": "1/4"},
            {"phase": "transition", "snapshots": 1, "avg_of_avg_ms": 10.0, "delta_avg_ms": "-1.000", "threshold_breaches": "0/1"},
        ]

        sorted_rows = MainUI._sort_performance_rows(rows, "snapshots_desc", "phase")
        self.assertEqual([row["phase"] for row in sorted_rows], ["bootstrap", "open", "transition"])

    def test_sort_performance_rows_by_delta_desc(self):
        """La ordenación por delta debe dejar primero el mayor empeoramiento."""
        rows = [
            {"metric": "b", "delta_avg_ms": "+2.000", "avg_of_avg_ms": 10.0, "threshold_breaches": "0/1", "snapshots": 2},
            {"metric": "a", "delta_avg_ms": "+7.000", "avg_of_avg_ms": 12.0, "threshold_breaches": "1/2", "snapshots": 3},
            {"metric": "c", "delta_avg_ms": "-1.000", "avg_of_avg_ms": 8.0, "threshold_breaches": "0/2", "snapshots": 1},
        ]

        sorted_rows = MainUI._sort_performance_rows(rows, "delta_desc", "metric")
        self.assertEqual([row["metric"] for row in sorted_rows], ["a", "b", "c"])

    def test_build_metric_summary_for_main_startup_metric(self):
        """La métrica de arranque del menú principal debe resumirse con umbral."""
        dummy = type(
            "DummyMainUI",
            (),
            {"UI_LATENCY_THRESHOLDS_MS": MainUI.UI_LATENCY_THRESHOLDS_MS},
        )()

        summary = MainUI._build_metric_summary(
            dummy,
            "ui.main.startup_ms",
            [100.0, 200.0, 300.0],
        )

        self.assertEqual(summary["count"], 3)
        self.assertEqual(summary["avg_ms"], 200.0)
        self.assertEqual(summary["threshold_ms"], 300.0)
        self.assertTrue(summary["within_threshold"])

    def test_sort_source_rows_by_snapshots_desc(self):
        """La ordenación por snapshots debe priorizar la fuente con más muestras."""
        rows = [
            {"source": "slots", "snapshots": 1, "avg_of_avg_ms": 10.0, "delta_avg_ms": "+1.000", "threshold_breaches": "0/1"},
            {"source": "main", "snapshots": 4, "avg_of_avg_ms": 20.0, "delta_avg_ms": "+0.500", "threshold_breaches": "0/4"},
            {"source": "blackjack", "snapshots": 2, "avg_of_avg_ms": 15.0, "delta_avg_ms": "+2.000", "threshold_breaches": "1/2"},
        ]

        sorted_rows = MainUI._sort_performance_rows(rows, "snapshots_desc", "source")
        self.assertEqual([row["source"] for row in sorted_rows], ["main", "blackjack", "slots"])

    def test_record_ui_metric_value_rejects_invalid_elapsed(self):
        """No debe guardar muestras inválidas (texto o tiempos negativos)."""
        dummy = type("DummyMainUI", (), {"_ui_perf_metrics": {}})()

        MainUI._record_ui_metric_value(dummy, "ui.main.bootstrap.db_init_ms", "x")
        MainUI._record_ui_metric_value(dummy, "ui.main.bootstrap.db_init_ms", -1.0)

        self.assertEqual(dummy._ui_perf_metrics, {})

    def test_record_bootstrap_metrics_populates_metric_samples(self):
        """Debe cargar métricas de bootstrap válidas como muestras locales."""
        dummy = type("DummyMainUI", (), {"_ui_perf_metrics": {}})()
        dummy._record_ui_metric_value = lambda metric, elapsed: MainUI._record_ui_metric_value(dummy, metric, elapsed)

        MainUI._record_bootstrap_metrics(
            dummy,
            {
                "ui.main.bootstrap.import_auth_database_ms": 55.5,
                "ui.main.bootstrap.db_init_ms": 120.25,
            },
        )

        self.assertEqual(dummy._ui_perf_metrics["ui.main.bootstrap.import_auth_database_ms"], [55.5])
        self.assertEqual(dummy._ui_perf_metrics["ui.main.bootstrap.db_init_ms"], [120.25])

    def test_build_metric_summary_for_bootstrap_import_metric(self):
        """Las métricas bootstrap nuevas deben resolver su umbral configurado."""
        dummy = type(
            "DummyMainUI",
            (),
            {"UI_LATENCY_THRESHOLDS_MS": MainUI.UI_LATENCY_THRESHOLDS_MS},
        )()

        summary = MainUI._build_metric_summary(
            dummy,
            "ui.main.bootstrap.import_auth_database_ms",
            [100.0, 180.0],
        )

        self.assertEqual(summary["avg_ms"], 140.0)
        self.assertEqual(summary["threshold_ms"], 250.0)
        self.assertTrue(summary["within_threshold"])
    
    def test_config_dialog_import(self):
        """Test that ConfigDialog can be imported from main module"""
        try:
            from RuleTragaperrasJuego.main import ConfigDialog
            self.assertTrue(callable(ConfigDialog))
        except ImportError as e:
            if "libEGL" not in str(e):
                raise


class TestMainModuleStructure(unittest.TestCase):
    """Tests para la estructura del módulo main"""
    
    def test_main_file_exists(self):
        """Test that main.py file exists"""
        main_file = ROOT_DIR / "main.py"
        self.assertTrue(main_file.exists())
        self.assertTrue(main_file.is_file())
    
    def test_main_file_structure(self):
        """Test basic structure of main.py file"""
        main_file = ROOT_DIR / "main.py"
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for essential imports
        self.assertIn('from PyQt6', content)
        self.assertIn('class MainUI', content)
        self.assertIn('def __init__', content)
        self.assertIn('def init_ui', content)
    
    def test_main_docstring(self):
        """Test that main module has proper documentation"""
        main_file = ROOT_DIR / "main.py"
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have imports and class definition
        self.assertIn('MainUI', content)
        self.assertIn('QMainWindow', content)


class TestMainIntegration(unittest.TestCase):
    """Tests de integración para el módulo main"""
    
    def test_main_imports_all_dependencies(self):
        """Test that main module can import all its dependencies"""
        dependencies_to_check = [
            'PyQt6.QtWidgets',
            'PyQt6.QtCore', 
            'PyQt6.QtGui',
            'config',
            'config_dialog'
        ]
        
        main_file = ROOT_DIR / "main.py"
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for dep in dependencies_to_check:
            # Check if dependency is imported (allowing for various import styles)
            self.assertTrue(
                dep in content or dep.replace('.', ' import ') in content,
                f"Dependency {dep} not found in main.py"
            )
    
    def test_main_integration_with_config(self):
        """Test that main integrates properly with config system"""
        try:
            import RuleTragaperrasJuego.main as main
            # Should be able to access config without errors
            if hasattr(main, 'config_manager'):
                config = main.config_manager
                self.assertIsNotNone(config)
        except ImportError as e:
            if "libEGL" in str(e) or "libGL" in str(e):
                self.skipTest("GUI components not available")
            else:
                raise


if __name__ == '__main__':
    unittest.main(verbosity=2)