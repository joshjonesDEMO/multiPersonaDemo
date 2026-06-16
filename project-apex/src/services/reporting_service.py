"""
ReportingService: pre-existing static reports and CSV exports.

Owner: BI Team
Language: Python/Flask (legacy)

Limited FastAPI auth integration. Do not route AnalyticsService data
through ReportingService — use the dbt marts layer instead.
"""
from typing import Any


class ReportingService:
    """Legacy static reports and CSV exports (Flask-based)."""

    def generate_csv_export(self, report_type: str, filters: dict[str, Any]) -> str:
        """Generate a CSV export for the given report type."""
        return f"report_{report_type}_{filters.get('team_id', 'all')}.csv"

    def list_available_reports(self) -> list[str]:
        """Return list of legacy report types."""
        return ["monthly_throughput", "quarterly_cycle_time", "team_comparison"]
