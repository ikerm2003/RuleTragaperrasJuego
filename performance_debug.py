"""Utilidades de rendimiento para modo debug.

Este modulo concentra la captura, exportacion y visualizacion de metricas de UI.
"""

from __future__ import annotations

import csv
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QLabel, QMessageBox, QPushButton, QVBoxLayout


class PerformanceDebugManager:
    DEFAULT_THRESHOLDS_MS: dict[str, float] = {
        "ui.main.startup_ms": 300.0,
        "ui.main.bootstrap.import_auth_database_ms": 250.0,
        "ui.main.bootstrap.import_login_dialog_ms": 250.0,
        "ui.main.bootstrap.db_init_ms": 500.0,
        "ui.main.bootstrap.load_user_config_ms": 300.0,
        "ui.main.bootstrap.window_init_ms": 500.0,
        "ui.main.launch_poker_ms": 900.0,
        "ui.main.launch_blackjack_ms": 700.0,
        "ui.main.launch_roulette_ms": 700.0,
        "ui.main.launch_slots_ms": 700.0,
        "ui.main.import_poker_ms": 450.0,
        "ui.main.import_blackjack_ms": 350.0,
        "ui.main.import_roulette_ms": 350.0,
        "ui.main.import_slots_ms": 350.0,
        "ui.main.open_poker_ms": 700.0,
        "ui.main.open_blackjack_ms": 550.0,
        "ui.main.open_roulette_ms": 550.0,
        "ui.main.open_slots_ms": 550.0,
        "ui.main.transition_to_poker_ms": 900.0,
        "ui.main.transition_to_blackjack_ms": 700.0,
        "ui.main.transition_to_roulette_ms": 700.0,
        "ui.main.transition_to_slots_ms": 700.0,
        "ui.main.restore_poker_ms": 120.0,
        "ui.main.restore_blackjack_ms": 120.0,
        "ui.main.restore_roulette_ms": 120.0,
        "ui.main.restore_slots_ms": 120.0,
        "ui.main.restore_transition_poker_ms": 120.0,
        "ui.main.restore_transition_blackjack_ms": 120.0,
        "ui.main.restore_transition_roulette_ms": 120.0,
        "ui.main.restore_transition_slots_ms": 120.0,
    }

    def __init__(self, enabled: bool, base_dir: Path, thresholds: dict[str, float] | None = None):
        self.enabled = bool(enabled)
        self.base_dir = Path(base_dir)
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS_MS
        self._metrics: dict[str, list[float]] = {}
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="perf-debug")
        self._io_lock = threading.Lock()

    def is_enabled(self) -> bool:
        return self.enabled

    def record_ui_metric(self, metric_name: str, started_at: float) -> None:
        if not self.enabled:
            return
        elapsed_ms = (time.perf_counter() - started_at) * 1000.0
        self.record_ui_metric_value(metric_name, elapsed_ms)

    def record_ui_metric_value(self, metric_name: str, elapsed_ms: float) -> None:
        if not self.enabled:
            return
        if not isinstance(elapsed_ms, (int, float)):
            return
        elapsed = float(elapsed_ms)
        if elapsed < 0:
            return
        if metric_name not in self._metrics:
            self._metrics[metric_name] = []
        self._metrics[metric_name].append(elapsed)
        if len(self._metrics[metric_name]) > 100:
            self._metrics[metric_name] = self._metrics[metric_name][-100:]

    def record_bootstrap_metrics(self, bootstrap_metrics) -> None:
        if not self.enabled or not isinstance(bootstrap_metrics, dict):
            return
        for metric_name, elapsed_ms in bootstrap_metrics.items():
            if not isinstance(metric_name, str) or not metric_name:
                continue
            self.record_ui_metric_value(metric_name, elapsed_ms)

    def build_metric_summary(self, metric_name: str, samples: list[float]) -> dict:
        ordered = sorted(samples)
        count = len(ordered)
        p95_index = max(0, min(count - 1, int(count * 0.95) - 1))
        avg_ms = sum(ordered) / count
        threshold_ms = self.thresholds.get(metric_name)

        return {
            "count": count,
            "avg_ms": round(avg_ms, 3),
            "min_ms": round(ordered[0], 3),
            "max_ms": round(ordered[-1], 3),
            "p95_ms": round(ordered[p95_index], 3),
            "threshold_ms": threshold_ms,
            "within_threshold": (
                None if threshold_ms is None else round(avg_ms, 3) <= threshold_ms
            ),
        }

    def export_ui_metrics_baseline_async(self, source: str = "main") -> None:
        if not self.enabled or not self._metrics:
            return

        summary = {
            metric: self.build_metric_summary(metric, samples)
            for metric, samples in self._metrics.items()
            if samples
        }
        if not summary:
            return

        snapshot = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "source": source,
            "metrics": summary,
        }
        self._executor.submit(self._append_snapshot, snapshot)

    def _append_snapshot(self, snapshot: dict) -> None:
        report_path = self.base_dir / "performance_baseline.json"
        with self._io_lock:
            data = {"snapshots": []}
            if report_path.exists():
                try:
                    with open(report_path, "r", encoding="utf-8") as f:
                        loaded = json.load(f)
                    if isinstance(loaded, dict) and isinstance(loaded.get("snapshots"), list):
                        data = loaded
                except (OSError, json.JSONDecodeError):
                    data = {"snapshots": []}

            data["snapshots"].append(snapshot)
            data["snapshots"] = data["snapshots"][-200:]

            try:
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except OSError:
                pass

    @staticmethod
    def _compute_metric_alert_level(status, avg_ms, threshold_ms, delta_avg_ms):
        is_avg_number = isinstance(avg_ms, (int, float))
        is_threshold_number = isinstance(threshold_ms, (int, float))
        is_delta_number = isinstance(delta_avg_ms, (int, float))

        if status is False:
            if is_avg_number and is_threshold_number and threshold_ms > 0:
                ratio = avg_ms / threshold_ms
                if ratio >= 1.3:
                    return "CRITICO", "#7f1d1d"
                if ratio >= 1.1:
                    return "ALTO", "#9a3412"
            return "ALTO", "#9a3412"

        if status is True:
            if is_delta_number and delta_avg_ms >= 5.0:
                return "REGRESION", "#92400e"
            return "OK", "#14532d"

        if is_delta_number and delta_avg_ms >= 5.0:
            return "REGRESION", "#92400e"
        return "N/A", "#334155"

    @staticmethod
    def _delta_visual(delta_avg_ms):
        if not isinstance(delta_avg_ms, (int, float)):
            return "-", "#475569"
        if delta_avg_ms >= 5.0:
            return f"{delta_avg_ms:+.3f}", "#b91c1c"
        if delta_avg_ms >= 1.0:
            return f"{delta_avg_ms:+.3f}", "#c2410c"
        if delta_avg_ms <= -1.0:
            return f"{delta_avg_ms:+.3f}", "#15803d"
        return f"{delta_avg_ms:+.3f}", "#475569"

    @classmethod
    def _build_performance_csv_rows(cls, snapshots):
        rows = []
        previous_by_source = {}

        for snap in snapshots:
            if not isinstance(snap, dict):
                continue

            source = snap.get("source", "desconocido")
            timestamp = snap.get("timestamp", "-")
            metrics = snap.get("metrics", {})
            if not isinstance(metrics, dict):
                continue

            previous_metrics = previous_by_source.get(source, {})

            for metric_name, summary in metrics.items():
                if not isinstance(summary, dict):
                    continue

                delta_avg_ms = None
                prev_summary = previous_metrics.get(metric_name)
                if isinstance(prev_summary, dict):
                    prev_avg = prev_summary.get("avg_ms")
                    curr_avg = summary.get("avg_ms")
                    if isinstance(prev_avg, (int, float)) and isinstance(curr_avg, (int, float)):
                        delta_avg_ms = round(curr_avg - prev_avg, 3)

                status = summary.get("within_threshold")
                alert_level, _ = cls._compute_metric_alert_level(
                    status=status,
                    avg_ms=summary.get("avg_ms"),
                    threshold_ms=summary.get("threshold_ms"),
                    delta_avg_ms=delta_avg_ms,
                )

                rows.append(
                    {
                        "timestamp": timestamp,
                        "source": source,
                        "metric": metric_name,
                        "samples": summary.get("count", "-"),
                        "avg_ms": summary.get("avg_ms", "-"),
                        "delta_avg_ms": "-" if delta_avg_ms is None else f"{delta_avg_ms:+.3f}",
                        "p95_ms": summary.get("p95_ms", "-"),
                        "min_ms": summary.get("min_ms", "-"),
                        "max_ms": summary.get("max_ms", "-"),
                        "threshold_ms": summary.get("threshold_ms", "-"),
                        "within_threshold": status,
                        "alert_level": alert_level,
                    }
                )

            previous_by_source[source] = metrics

        return rows

    @staticmethod
    def _parse_snapshot_timestamp(value):
        if not isinstance(value, str) or not value.strip():
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    @staticmethod
    def _format_iso_timestamp(value):
        if not isinstance(value, datetime):
            return ""
        return value.replace(microsecond=0).isoformat()

    @classmethod
    def _get_time_preset_bounds(cls, preset_name, now=None):
        now_dt = now if isinstance(now, datetime) else datetime.now()
        end_dt = now_dt.replace(microsecond=0)

        if preset_name == "Ultima hora":
            start_dt = end_dt - timedelta(hours=1)
        elif preset_name == "Ultimas 24h":
            start_dt = end_dt - timedelta(hours=24)
        elif preset_name == "Ultimos 7 dias":
            start_dt = end_dt - timedelta(days=7)
        elif preset_name == "Todo":
            return None, None
        else:
            return None, None

        return cls._format_iso_timestamp(start_dt), cls._format_iso_timestamp(end_dt)

    @classmethod
    def _filter_performance_snapshots(
        cls,
        snapshots,
        source_filter="Todas",
        metric_filter="Todas",
        start_ts=None,
        end_ts=None,
    ):
        start_dt = cls._parse_snapshot_timestamp(start_ts)
        end_dt = cls._parse_snapshot_timestamp(end_ts)
        filtered = []

        for snap in snapshots:
            if not isinstance(snap, dict):
                continue

            source_raw = snap.get("source", "desconocido")
            source = source_raw if isinstance(source_raw, str) else str(source_raw)
            if source_filter not in (None, "", "Todas") and source != source_filter:
                continue

            ts_raw = snap.get("timestamp")
            ts_dt = cls._parse_snapshot_timestamp(ts_raw)
            if start_dt and (ts_dt is None or ts_dt < start_dt):
                continue
            if end_dt and (ts_dt is None or ts_dt > end_dt):
                continue

            metrics = snap.get("metrics", {})
            if not isinstance(metrics, dict):
                continue

            if metric_filter in (None, "", "Todas"):
                selected_metrics = metrics
            else:
                selected_metrics = {
                    metric_filter: metrics.get(metric_filter)
                }

            selected_metrics = {
                name: summary
                for name, summary in selected_metrics.items()
                if isinstance(summary, dict)
            }

            if not selected_metrics:
                continue

            filtered.append(
                {
                    "timestamp": snap.get("timestamp", "-"),
                    "source": source,
                    "metrics": selected_metrics,
                }
            )

        return filtered

    @classmethod
    def _build_metric_trend_rows(cls, snapshots):
        if not isinstance(snapshots, list):
            return []

        ordered = []
        for index, snap in enumerate(snapshots):
            if not isinstance(snap, dict):
                continue
            ts = cls._parse_snapshot_timestamp(snap.get("timestamp"))
            order_ts = ts if ts is not None else datetime.min
            ordered.append((order_ts, index, snap))

        ordered.sort(key=lambda item: (item[0], item[1]))

        metric_snapshots: dict[str, int] = {}
        metric_sources: dict[str, set[str]] = {}
        metric_avg_values: dict[str, list[float]] = {}
        metric_first_avg: dict[str, float] = {}
        metric_last_avg: dict[str, float] = {}
        metric_min_avg: dict[str, float] = {}
        metric_max_avg: dict[str, float] = {}
        metric_threshold_checks: dict[str, int] = {}
        metric_over_threshold: dict[str, int] = {}

        for _, _, snap in ordered:
            source_raw = snap.get("source", "desconocido")
            source = source_raw if isinstance(source_raw, str) else str(source_raw)
            metrics = snap.get("metrics", {})
            if not isinstance(metrics, dict):
                continue

            for metric_name, summary in metrics.items():
                if not isinstance(metric_name, str) or not isinstance(summary, dict):
                    continue

                metric_snapshots[metric_name] = metric_snapshots.get(metric_name, 0) + 1
                metric_sources.setdefault(metric_name, set()).add(source)

                status = summary.get("within_threshold")
                if isinstance(status, bool):
                    metric_threshold_checks[metric_name] = (
                        metric_threshold_checks.get(metric_name, 0) + 1
                    )
                    if status is False:
                        metric_over_threshold[metric_name] = (
                            metric_over_threshold.get(metric_name, 0) + 1
                        )

                avg_ms = summary.get("avg_ms")
                if not isinstance(avg_ms, (int, float)):
                    continue

                current_avg = float(avg_ms)
                metric_avg_values.setdefault(metric_name, []).append(current_avg)
                metric_first_avg.setdefault(metric_name, current_avg)
                metric_last_avg[metric_name] = current_avg
                metric_min_avg[metric_name] = min(metric_min_avg.get(metric_name, current_avg), current_avg)
                metric_max_avg[metric_name] = max(metric_max_avg.get(metric_name, current_avg), current_avg)

        rows = []
        for metric_name in sorted(metric_snapshots.keys()):
            values = metric_avg_values.get(metric_name, [])
            avg_of_avg = round(sum(values) / len(values), 3) if values else "-"
            first_avg = metric_first_avg.get(metric_name)
            last_avg = metric_last_avg.get(metric_name)
            delta_avg = (
                round(last_avg - first_avg, 3)
                if isinstance(first_avg, (int, float)) and isinstance(last_avg, (int, float))
                else None
            )
            delta_text, delta_color = cls._delta_visual(delta_avg)

            threshold_checks = metric_threshold_checks.get(metric_name, 0)
            breach_text = (
                f"{metric_over_threshold.get(metric_name, 0)}/{threshold_checks}"
                if threshold_checks
                else "-"
            )

            rows.append(
                {
                    "metric": metric_name,
                    "snapshots": metric_snapshots.get(metric_name, 0),
                    "sources": len(metric_sources.get(metric_name, set())),
                    "avg_of_avg_ms": avg_of_avg,
                    "delta_avg_ms": delta_text,
                    "delta_color": delta_color,
                    "first_avg_ms": "-" if first_avg is None else round(first_avg, 3),
                    "last_avg_ms": "-" if last_avg is None else round(last_avg, 3),
                    "min_avg_ms": "-" if metric_name not in metric_min_avg else round(metric_min_avg[metric_name], 3),
                    "max_avg_ms": "-" if metric_name not in metric_max_avg else round(metric_max_avg[metric_name], 3),
                    "threshold_breaches": breach_text,
                }
            )

        return rows

    @classmethod
    def _build_source_trend_rows(cls, snapshots):
        if not isinstance(snapshots, list):
            return []

        ordered = []
        for index, snap in enumerate(snapshots):
            if not isinstance(snap, dict):
                continue
            ts = cls._parse_snapshot_timestamp(snap.get("timestamp"))
            order_ts = ts if ts is not None else datetime.min
            ordered.append((order_ts, index, snap))

        ordered.sort(key=lambda item: (item[0], item[1]))

        source_snapshots: dict[str, int] = {}
        source_metrics: dict[str, set[str]] = {}
        source_avg_values: dict[str, list[float]] = {}
        source_first_avg: dict[str, float] = {}
        source_last_avg: dict[str, float] = {}
        source_min_avg: dict[str, float] = {}
        source_max_avg: dict[str, float] = {}
        source_threshold_checks: dict[str, int] = {}
        source_over_threshold: dict[str, int] = {}

        for _, _, snap in ordered:
            source_raw = snap.get("source", "desconocido")
            source = source_raw if isinstance(source_raw, str) else str(source_raw)
            metrics = snap.get("metrics", {})
            if not isinstance(metrics, dict):
                continue

            source_snapshots[source] = source_snapshots.get(source, 0) + 1
            source_avg_samples = []

            for metric_name, summary in metrics.items():
                if not isinstance(metric_name, str) or not isinstance(summary, dict):
                    continue

                source_metrics.setdefault(source, set()).add(metric_name)

                status = summary.get("within_threshold")
                if isinstance(status, bool):
                    source_threshold_checks[source] = (
                        source_threshold_checks.get(source, 0) + 1
                    )
                    if status is False:
                        source_over_threshold[source] = (
                            source_over_threshold.get(source, 0) + 1
                        )

                avg_ms = summary.get("avg_ms")
                if isinstance(avg_ms, (int, float)):
                    source_avg_samples.append(float(avg_ms))

            if not source_avg_samples:
                continue

            source_avg_values.setdefault(source, []).extend(source_avg_samples)
            snapshot_avg = sum(source_avg_samples) / len(source_avg_samples)
            source_first_avg.setdefault(source, snapshot_avg)
            source_last_avg[source] = snapshot_avg
            source_min_avg[source] = min(source_min_avg.get(source, snapshot_avg), snapshot_avg)
            source_max_avg[source] = max(source_max_avg.get(source, snapshot_avg), snapshot_avg)

        rows = []
        for source in sorted(source_snapshots.keys()):
            values = source_avg_values.get(source, [])
            avg_of_avg = round(sum(values) / len(values), 3) if values else "-"
            first_avg = source_first_avg.get(source)
            last_avg = source_last_avg.get(source)
            delta_avg = (
                round(last_avg - first_avg, 3)
                if isinstance(first_avg, (int, float)) and isinstance(last_avg, (int, float))
                else None
            )
            delta_text, delta_color = cls._delta_visual(delta_avg)

            threshold_checks = source_threshold_checks.get(source, 0)
            breach_text = (
                f"{source_over_threshold.get(source, 0)}/{threshold_checks}"
                if threshold_checks
                else "-"
            )

            rows.append(
                {
                    "source": source,
                    "snapshots": source_snapshots.get(source, 0),
                    "metrics": len(source_metrics.get(source, set())),
                    "avg_of_avg_ms": avg_of_avg,
                    "delta_avg_ms": delta_text,
                    "delta_color": delta_color,
                    "first_avg_ms": "-" if first_avg is None else round(first_avg, 3),
                    "last_avg_ms": "-" if last_avg is None else round(last_avg, 3),
                    "min_avg_ms": "-" if source not in source_min_avg else round(source_min_avg[source], 3),
                    "max_avg_ms": "-" if source not in source_max_avg else round(source_max_avg[source], 3),
                    "threshold_breaches": breach_text,
                }
            )

        return rows

    @staticmethod
    def _classify_main_metric_phase(metric_name):
        if not isinstance(metric_name, str):
            return None
        if metric_name.startswith("ui.main.bootstrap."):
            return "bootstrap"
        if metric_name.startswith("ui.main.import_"):
            return "import"
        if metric_name.startswith("ui.main.open_"):
            return "open"
        if metric_name.startswith("ui.main.transition_to_") or metric_name.startswith("ui.main.restore_transition_"):
            return "transition"
        return None

    @staticmethod
    def _compute_phase_alert_level(threshold_breaches, threshold_checks, delta_avg_ms):
        if isinstance(threshold_checks, int) and threshold_checks > 0 and isinstance(threshold_breaches, int):
            ratio = threshold_breaches / threshold_checks
            if ratio >= 0.4:
                return "CRITICO", "#7f1d1d"
            if ratio > 0.0:
                return "ALTO", "#9a3412"
        if isinstance(delta_avg_ms, (int, float)) and delta_avg_ms >= 5.0:
            return "REGRESION", "#92400e"
        return "OK", "#14532d"

    @classmethod
    def _build_phase_trend_rows(cls, snapshots):
        if not isinstance(snapshots, list):
            return []

        ordered = []
        for index, snap in enumerate(snapshots):
            if not isinstance(snap, dict):
                continue
            ts = cls._parse_snapshot_timestamp(snap.get("timestamp"))
            order_ts = ts if ts is not None else datetime.min
            ordered.append((order_ts, index, snap))

        ordered.sort(key=lambda item: (item[0], item[1]))

        phase_snapshots: dict[str, int] = {}
        phase_sources: dict[str, set[str]] = {}
        phase_metrics: dict[str, set[str]] = {}
        phase_avg_values: dict[str, list[float]] = {}
        phase_first_avg: dict[str, float] = {}
        phase_last_avg: dict[str, float] = {}
        phase_min_avg: dict[str, float] = {}
        phase_max_avg: dict[str, float] = {}
        phase_threshold_checks: dict[str, int] = {}
        phase_threshold_breaches: dict[str, int] = {}

        for _, _, snap in ordered:
            source_raw = snap.get("source", "desconocido")
            source = source_raw if isinstance(source_raw, str) else str(source_raw)
            metrics = snap.get("metrics", {})
            if not isinstance(metrics, dict):
                continue

            phases_seen_in_snapshot: set[str] = set()
            phase_snapshot_values: dict[str, list[float]] = {}

            for metric_name, summary in metrics.items():
                if not isinstance(summary, dict):
                    continue

                phase = cls._classify_main_metric_phase(metric_name)
                if phase is None:
                    continue

                phases_seen_in_snapshot.add(phase)
                phase_sources.setdefault(phase, set()).add(source)
                phase_metrics.setdefault(phase, set()).add(metric_name)

                status = summary.get("within_threshold")
                if isinstance(status, bool):
                    phase_threshold_checks[phase] = phase_threshold_checks.get(phase, 0) + 1
                    if status is False:
                        phase_threshold_breaches[phase] = phase_threshold_breaches.get(phase, 0) + 1

                avg_ms = summary.get("avg_ms")
                if isinstance(avg_ms, (int, float)):
                    phase_snapshot_values.setdefault(phase, []).append(float(avg_ms))

            for phase in phases_seen_in_snapshot:
                phase_snapshots[phase] = phase_snapshots.get(phase, 0) + 1

            for phase, values in phase_snapshot_values.items():
                snapshot_avg = sum(values) / len(values)
                phase_avg_values.setdefault(phase, []).append(snapshot_avg)
                phase_first_avg.setdefault(phase, snapshot_avg)
                phase_last_avg[phase] = snapshot_avg
                phase_min_avg[phase] = min(phase_min_avg.get(phase, snapshot_avg), snapshot_avg)
                phase_max_avg[phase] = max(phase_max_avg.get(phase, snapshot_avg), snapshot_avg)

        phase_order = {"bootstrap": 0, "import": 1, "open": 2, "transition": 3}

        rows = []
        for phase in sorted(phase_snapshots.keys(), key=lambda name: (phase_order.get(name, 99), name)):
            values = phase_avg_values.get(phase, [])
            avg_of_avg = round(sum(values) / len(values), 3) if values else "-"

            first_avg = phase_first_avg.get(phase)
            last_avg = phase_last_avg.get(phase)
            delta_avg = (
                round(last_avg - first_avg, 3)
                if isinstance(first_avg, (int, float)) and isinstance(last_avg, (int, float))
                else None
            )
            delta_text, delta_color = cls._delta_visual(delta_avg)

            threshold_checks = phase_threshold_checks.get(phase, 0)
            threshold_breaches = phase_threshold_breaches.get(phase, 0)
            breach_text = f"{threshold_breaches}/{threshold_checks}" if threshold_checks else "-"
            alert_text, alert_color = cls._compute_phase_alert_level(
                threshold_breaches=threshold_breaches,
                threshold_checks=threshold_checks,
                delta_avg_ms=delta_avg,
            )

            rows.append(
                {
                    "phase": phase,
                    "snapshots": phase_snapshots.get(phase, 0),
                    "sources": len(phase_sources.get(phase, set())),
                    "metrics": len(phase_metrics.get(phase, set())),
                    "avg_of_avg_ms": avg_of_avg,
                    "delta_avg_ms": delta_text,
                    "delta_color": delta_color,
                    "first_avg_ms": "-" if first_avg is None else round(first_avg, 3),
                    "last_avg_ms": "-" if last_avg is None else round(last_avg, 3),
                    "min_avg_ms": "-" if phase not in phase_min_avg else round(phase_min_avg[phase], 3),
                    "max_avg_ms": "-" if phase not in phase_max_avg else round(phase_max_avg[phase], 3),
                    "threshold_breaches": breach_text,
                    "alert_text": alert_text,
                    "alert_color": alert_color,
                }
            )

        return rows

    @staticmethod
    def _parse_delta_value(value):
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = value.strip()
            if cleaned in ("", "-"):
                return None
            try:
                return float(cleaned)
            except ValueError:
                return None
        return None

    @staticmethod
    def _parse_breach_ratio(value):
        if not isinstance(value, str) or "/" not in value:
            return (-1, -1)
        left, right = value.split("/", 1)
        try:
            return (int(left), int(right))
        except ValueError:
            return (-1, -1)

    @classmethod
    def _sort_performance_rows(cls, rows, sort_mode, row_type):
        if not isinstance(rows, list):
            return []

        sortable_rows = [row for row in rows if isinstance(row, dict)]

        if row_type == "detail":
            severity_rank = {"REGRESION": 4, "CRITICO": 3, "ALTO": 2, "OK": 1, "N/A": 0}
            if sort_mode == "avg_desc":
                return sorted(sortable_rows, key=lambda row: cls._sortable_number(row.get("avg_ms")), reverse=True)
            if sort_mode == "delta_desc":
                return sorted(sortable_rows, key=lambda row: cls._sortable_number(cls._parse_delta_value(row.get("delta_avg_ms"))), reverse=True)
            if sort_mode == "severidad_desc":
                return sorted(sortable_rows, key=lambda row: severity_rank.get(row.get("alert_text"), -1), reverse=True)
            return sorted(sortable_rows, key=lambda row: str(row.get("metric", "")).lower())

        if sort_mode == "avg_desc":
            return sorted(sortable_rows, key=lambda row: cls._sortable_number(row.get("avg_of_avg_ms")), reverse=True)
        if sort_mode == "delta_desc":
            return sorted(sortable_rows, key=lambda row: cls._sortable_number(cls._parse_delta_value(row.get("delta_avg_ms"))), reverse=True)
        if sort_mode == "brechas_desc":
            return sorted(sortable_rows, key=lambda row: cls._parse_breach_ratio(row.get("threshold_breaches")), reverse=True)
        if sort_mode == "snapshots_desc":
            return sorted(sortable_rows, key=lambda row: cls._sortable_number(row.get("snapshots")), reverse=True)

        if row_type == "source":
            key_name = "source"
        elif row_type == "phase":
            key_name = "phase"
        else:
            key_name = "metric"
        return sorted(sortable_rows, key=lambda row: str(row.get(key_name, "")).lower())

    @staticmethod
    def _sortable_number(value):
        if isinstance(value, (int, float)):
            return float(value)
        return float("-inf")

    @classmethod
    def _export_performance_csv(cls, snapshots, csv_path: Path):
        rows = cls._build_performance_csv_rows(snapshots)
        if not rows:
            return False, 0

        fieldnames = list(rows[0].keys())
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        return True, len(rows)

    def show_performance_baseline(self, parent, get_text_fn):
        if not self.enabled:
            QMessageBox.information(parent, "Debug", "Las metricas de rendimiento estan desactivadas.")
            return

        dialog = QtWidgets.QDialog(parent)
        dialog.setWindowTitle("Rendimiento UI")
        dialog.setMinimumSize(700, 500)

        layout = QVBoxLayout(dialog)
        controls_layout = QtWidgets.QGridLayout()

        source_label = QLabel("Fuente")
        source_combo = QtWidgets.QComboBox()
        source_combo.addItem("Todas")

        metric_label = QLabel("Metrica")
        metric_combo = QtWidgets.QComboBox()
        metric_combo.addItem("Todas")

        start_label = QLabel("Desde (ISO)")
        start_input = QtWidgets.QLineEdit()
        start_input.setPlaceholderText("2026-03-12T00:00:00")

        end_label = QLabel("Hasta (ISO)")
        end_input = QtWidgets.QLineEdit()
        end_input.setPlaceholderText("2026-03-12T23:59:59")

        preset_label = QLabel("Preset")
        preset_combo = QtWidgets.QComboBox()
        preset_combo.addItems(["Todo", "Ultima hora", "Ultimas 24h", "Ultimos 7 dias"])

        apply_preset_btn = QPushButton("Aplicar preset")

        aggregate_sort_label = QLabel("Orden agregados")
        aggregate_sort_combo = QtWidgets.QComboBox()
        aggregate_sort_combo.addItem("Nombre", "name_asc")
        aggregate_sort_combo.addItem("Avg agregado ↓", "avg_desc")
        aggregate_sort_combo.addItem("Delta periodo ↓", "delta_desc")
        aggregate_sort_combo.addItem("Brechas umbral ↓", "brechas_desc")
        aggregate_sort_combo.addItem("Snapshots ↓", "snapshots_desc")

        detail_sort_label = QLabel("Orden detalle")
        detail_sort_combo = QtWidgets.QComboBox()
        detail_sort_combo.addItem("Severidad ↓", "severidad_desc")
        detail_sort_combo.addItem("Delta ↓", "delta_desc")
        detail_sort_combo.addItem("Avg ↓", "avg_desc")
        detail_sort_combo.addItem("Metrica", "name_asc")

        apply_filter_btn = QPushButton("Aplicar filtros")

        controls_layout.addWidget(source_label, 0, 0)
        controls_layout.addWidget(source_combo, 0, 1)
        controls_layout.addWidget(metric_label, 0, 2)
        controls_layout.addWidget(metric_combo, 0, 3)
        controls_layout.addWidget(start_label, 1, 0)
        controls_layout.addWidget(start_input, 1, 1)
        controls_layout.addWidget(end_label, 1, 2)
        controls_layout.addWidget(end_input, 1, 3)
        controls_layout.addWidget(apply_filter_btn, 0, 4, 2, 1)
        controls_layout.addWidget(preset_label, 2, 0)
        controls_layout.addWidget(preset_combo, 2, 1)
        controls_layout.addWidget(apply_preset_btn, 2, 2, 1, 2)
        controls_layout.addWidget(aggregate_sort_label, 3, 0)
        controls_layout.addWidget(aggregate_sort_combo, 3, 1)
        controls_layout.addWidget(detail_sort_label, 3, 2)
        controls_layout.addWidget(detail_sort_combo, 3, 3)

        layout.addLayout(controls_layout)
        text_browser = QtWidgets.QTextBrowser()

        report_path = self.base_dir / "performance_baseline.json"
        snapshots = []
        filtered_snapshots = []

        def _populate_filter_options(raw_snapshots):
            sources = set()
            metrics = set()
            for snap in raw_snapshots:
                if not isinstance(snap, dict):
                    continue
                source = snap.get("source")
                if isinstance(source, str) and source:
                    sources.add(source)
                snap_metrics = snap.get("metrics", {})
                if isinstance(snap_metrics, dict):
                    metrics.update(name for name in snap_metrics.keys() if isinstance(name, str))

            for source in sorted(sources):
                source_combo.addItem(source)
            for metric_name in sorted(metrics):
                metric_combo.addItem(metric_name)

        def _render_report():
            nonlocal filtered_snapshots
            if not snapshots:
                return

            start_raw = start_input.text().strip() or None
            end_raw = end_input.text().strip() or None

            if start_raw and self._parse_snapshot_timestamp(start_raw) is None:
                text_browser.setHtml(
                    "<h3>Filtro temporal invalido</h3>"
                    "<p>El campo <b>Desde</b> debe usar formato ISO, por ejemplo: 2026-03-12T00:00:00</p>"
                )
                filtered_snapshots = []
                return

            if end_raw and self._parse_snapshot_timestamp(end_raw) is None:
                text_browser.setHtml(
                    "<h3>Filtro temporal invalido</h3>"
                    "<p>El campo <b>Hasta</b> debe usar formato ISO, por ejemplo: 2026-03-12T23:59:59</p>"
                )
                filtered_snapshots = []
                return

            filtered_snapshots = self._filter_performance_snapshots(
                snapshots,
                source_filter=source_combo.currentText(),
                metric_filter=metric_combo.currentText(),
                start_ts=start_raw,
                end_ts=end_raw,
            )

            if not filtered_snapshots:
                text_browser.setHtml(
                    "<h3>Sin datos con los filtros actuales</h3>"
                    "<p>Ajusta fuente, metrica o rango temporal para visualizar resultados.</p>"
                )
                return

            recent = list(reversed(filtered_snapshots[-12:]))
            aggregate_sort_mode = aggregate_sort_combo.currentData()
            detail_sort_mode = detail_sort_combo.currentData()
            trend_rows = self._sort_performance_rows(
                self._build_metric_trend_rows(filtered_snapshots),
                aggregate_sort_mode,
                "metric",
            )
            phase_trend_rows = self._sort_performance_rows(
                self._build_phase_trend_rows(filtered_snapshots),
                aggregate_sort_mode,
                "phase",
            )
            source_trend_rows = self._sort_performance_rows(
                self._build_source_trend_rows(filtered_snapshots),
                aggregate_sort_mode,
                "source",
            )
            html = ["<h2>Snapshots de rendimiento UI</h2>"]
            html.append(
                f"<p>Mostrando {len(recent)} de {len(filtered_snapshots)} snapshots filtrados (max. 12 en pantalla).</p>"
            )

            if phase_trend_rows:
                html.append("<h3>Desglose por fase (main)</h3>")
                html.append(
                    "<table style='width:100%; border-collapse: collapse;' border='1' cellspacing='0' cellpadding='6'>"
                    "<tr>"
                    "<th>Fase</th><th>Snapshots</th><th>Fuentes</th><th>Metricas</th><th>Avg agregado ms</th>"
                    "<th>Delta periodo</th><th>Primero/Ultimo avg</th><th>Min/Max avg</th><th>Brechas umbral</th><th>Alerta</th>"
                    "</tr>"
                )

                for row in phase_trend_rows:
                    phase_badge = (
                        "<span style='display:inline-block; padding:2px 8px;'"
                        f" border-radius:10px; color:#ffffff; background:{row['alert_color']}; font-weight:700;'>"
                        f"{row['alert_text']}</span>"
                    )
                    html.append(
                        "<tr>"
                        f"<td>{row['phase']}</td>"
                        f"<td>{row['snapshots']}</td>"
                        f"<td>{row['sources']}</td>"
                        f"<td>{row['metrics']}</td>"
                        f"<td>{row['avg_of_avg_ms']}</td>"
                        f"<td style='color:{row['delta_color']}; font-weight:700;'>{row['delta_avg_ms']}</td>"
                        f"<td>{row['first_avg_ms']} / {row['last_avg_ms']}</td>"
                        f"<td>{row['min_avg_ms']} / {row['max_avg_ms']}</td>"
                        f"<td>{row['threshold_breaches']}</td>"
                        f"<td>{phase_badge}</td>"
                        "</tr>"
                    )

                html.append("</table><br>")

            if source_trend_rows:
                html.append("<h3>Comparativa agregada por fuente</h3>")
                html.append(
                    "<table style='width:100%; border-collapse: collapse;' border='1' cellspacing='0' cellpadding='6'>"
                    "<tr>"
                    "<th>Fuente</th><th>Snapshots</th><th>Metricas</th><th>Avg agregado ms</th>"
                    "<th>Delta periodo</th><th>Primero/Ultimo avg</th><th>Min/Max avg</th><th>Brechas umbral</th>"
                    "</tr>"
                )

                for row in source_trend_rows:
                    html.append(
                        "<tr>"
                        f"<td>{row['source']}</td>"
                        f"<td>{row['snapshots']}</td>"
                        f"<td>{row['metrics']}</td>"
                        f"<td>{row['avg_of_avg_ms']}</td>"
                        f"<td style='color:{row['delta_color']}; font-weight:700;'>{row['delta_avg_ms']}</td>"
                        f"<td>{row['first_avg_ms']} / {row['last_avg_ms']}</td>"
                        f"<td>{row['min_avg_ms']} / {row['max_avg_ms']}</td>"
                        f"<td>{row['threshold_breaches']}</td>"
                        "</tr>"
                    )

                html.append("</table><br>")

            if trend_rows:
                html.append("<h3>Tendencia agregada por metrica</h3>")
                html.append(
                    "<table style='width:100%; border-collapse: collapse;' border='1' cellspacing='0' cellpadding='6'>"
                    "<tr>"
                    "<th>Metrica</th><th>Snapshots</th><th>Fuentes</th><th>Avg agregado ms</th>"
                    "<th>Delta periodo</th><th>Primero/Ultimo avg</th><th>Min/Max avg</th><th>Brechas umbral</th>"
                    "</tr>"
                )

                for row in trend_rows:
                    html.append(
                        "<tr>"
                        f"<td>{row['metric']}</td>"
                        f"<td>{row['snapshots']}</td>"
                        f"<td>{row['sources']}</td>"
                        f"<td>{row['avg_of_avg_ms']}</td>"
                        f"<td style='color:{row['delta_color']}; font-weight:700;'>{row['delta_avg_ms']}</td>"
                        f"<td>{row['first_avg_ms']} / {row['last_avg_ms']}</td>"
                        f"<td>{row['min_avg_ms']} / {row['max_avg_ms']}</td>"
                        f"<td>{row['threshold_breaches']}</td>"
                        "</tr>"
                    )

                html.append("</table><br>")

            previous_by_source: dict[str, dict] = {}

            for snap in recent:
                source_raw = snap.get("source", "desconocido")
                source = source_raw if isinstance(source_raw, str) else str(source_raw)
                timestamp = snap.get("timestamp", "-")
                metrics = snap.get("metrics", {})

                previous_metrics = previous_by_source.get(source, {})

                html.append(
                    f"<h3>{source.capitalize()} - {timestamp}</h3>"
                )
                html.append(
                    "<table style='width:100%; border-collapse: collapse;' border='1' cellspacing='0' cellpadding='6'>"
                    "<tr>"
                    "<th>Metrica</th><th>Muestras</th><th>Avg ms</th><th>Δ Avg ms</th><th>P95 ms</th><th>Min/Max ms</th><th>Umbral</th><th>Estado</th>"
                    "</tr>"
                )

                if isinstance(metrics, dict):
                    detail_rows = []
                    for metric_name, summary in metrics.items():
                        if not isinstance(summary, dict):
                            continue

                        threshold = summary.get("threshold_ms")
                        threshold_text = "-" if threshold is None else str(threshold)
                        status = summary.get("within_threshold")
                        if status is True:
                            status_text = "OK"
                        elif status is False:
                            status_text = "ALTO"
                        else:
                            status_text = "N/A"

                        delta_value = None
                        prev_summary = None
                        if isinstance(previous_metrics, dict):
                            prev_summary = previous_metrics.get(metric_name)

                        if isinstance(prev_summary, dict):
                            prev_avg = prev_summary.get("avg_ms")
                            curr_avg = summary.get("avg_ms")
                            if isinstance(prev_avg, (int, float)) and isinstance(curr_avg, (int, float)):
                                delta_value = round(curr_avg - prev_avg, 3)

                        delta_text, delta_color = self._delta_visual(delta_value)
                        alert_text, alert_color = self._compute_metric_alert_level(
                            status=status,
                            avg_ms=summary.get("avg_ms"),
                            threshold_ms=threshold,
                            delta_avg_ms=delta_value,
                        )

                        status_badge = (
                            f"<span style='display:inline-block; padding:2px 8px;'"
                            f" border-radius:10px; color:#ffffff; background:{alert_color}; font-weight:700;'>"
                            f"{status_text} / {alert_text}</span>"
                        )

                        detail_rows.append(
                            {
                                "metric": metric_name,
                                "samples": summary.get('count', '-'),
                                "avg_ms": summary.get('avg_ms', '-'),
                                "delta_avg_ms": delta_text,
                                "delta_color": delta_color,
                                "p95_ms": summary.get('p95_ms', '-'),
                                "min_ms": summary.get('min_ms', '-'),
                                "max_ms": summary.get('max_ms', '-'),
                                "threshold_text": threshold_text,
                                "status_badge": status_badge,
                                "alert_text": alert_text,
                            }
                        )

                    for row in self._sort_performance_rows(detail_rows, detail_sort_mode, "detail"):
                        html.append(
                            "<tr>"
                            f"<td>{row['metric']}</td>"
                            f"<td>{row['samples']}</td>"
                            f"<td>{row['avg_ms']}</td>"
                            f"<td style='color:{row['delta_color']}; font-weight:700;'>{row['delta_avg_ms']}</td>"
                            f"<td>{row['p95_ms']}</td>"
                            f"<td>{row['min_ms']} / {row['max_ms']}</td>"
                            f"<td>{row['threshold_text']}</td>"
                            f"<td>{row['status_badge']}</td>"
                            "</tr>"
                        )

                html.append("</table><br>")
                if isinstance(metrics, dict):
                    previous_by_source[source] = metrics

            text_browser.setHtml("".join(html))

        if not report_path.exists():
            text_browser.setHtml(
                "<h3>Sin datos de baseline</h3>"
                "<p>Aun no hay snapshots de rendimiento. Activa debug y cierra una ventana de juego para registrar metricas.</p>"
            )
            source_combo.setEnabled(False)
            metric_combo.setEnabled(False)
            start_input.setEnabled(False)
            end_input.setEnabled(False)
            preset_combo.setEnabled(False)
            apply_preset_btn.setEnabled(False)
            aggregate_sort_combo.setEnabled(False)
            detail_sort_combo.setEnabled(False)
            apply_filter_btn.setEnabled(False)
        else:
            try:
                with open(report_path, "r", encoding="utf-8") as f:
                    payload = json.load(f)
                snapshots = payload.get("snapshots", []) if isinstance(payload, dict) else []
            except (OSError, json.JSONDecodeError):
                snapshots = []

            if not snapshots:
                text_browser.setHtml(
                    "<h3>Sin datos de baseline</h3>"
                    "<p>El archivo existe pero no contiene snapshots validos.</p>"
                )
                source_combo.setEnabled(False)
                metric_combo.setEnabled(False)
                start_input.setEnabled(False)
                end_input.setEnabled(False)
                preset_combo.setEnabled(False)
                apply_preset_btn.setEnabled(False)
                aggregate_sort_combo.setEnabled(False)
                detail_sort_combo.setEnabled(False)
                apply_filter_btn.setEnabled(False)
            else:
                _populate_filter_options(snapshots)
                _render_report()

        def _apply_time_preset():
            preset = preset_combo.currentText()
            start_iso, end_iso = self._get_time_preset_bounds(preset)
            if start_iso is None and end_iso is None:
                start_input.clear()
                end_input.clear()
            else:
                start_input.setText(start_iso)
                end_input.setText(end_iso)
            _render_report()

        apply_preset_btn.clicked.connect(_apply_time_preset)
        apply_filter_btn.clicked.connect(_render_report)
        aggregate_sort_combo.currentIndexChanged.connect(_render_report)
        detail_sort_combo.currentIndexChanged.connect(_render_report)

        layout.addWidget(text_browser)

        export_btn = QPushButton("Exportar CSV")
        export_btn.setEnabled(bool(snapshots))

        def _handle_export_csv():
            if not snapshots:
                QMessageBox.information(
                    parent,
                    "Rendimiento UI",
                    "No hay snapshots para exportar.",
                )
                return

            if not filtered_snapshots:
                QMessageBox.information(
                    parent,
                    "Rendimiento UI",
                    "No hay filas validas con los filtros actuales para exportar.",
                )
                return

            csv_path = self.base_dir / "performance_baseline_history.csv"
            try:
                exported, row_count = self._export_performance_csv(filtered_snapshots, csv_path)
            except OSError as exc:
                QMessageBox.critical(
                    parent,
                    "Rendimiento UI",
                    f"No se pudo exportar el CSV: {exc}",
                )
                return

            if not exported:
                QMessageBox.information(
                    parent,
                    "Rendimiento UI",
                    "No se encontraron filas validas para exportar.",
                )
                return

            QMessageBox.information(
                parent,
                "Rendimiento UI",
                f"CSV exportado en:\n{csv_path.name}\nFilas: {row_count}",
            )

        export_btn.clicked.connect(_handle_export_csv)
        layout.addWidget(export_btn)

        close_btn = QPushButton(get_text_fn("cancel"))
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec()
