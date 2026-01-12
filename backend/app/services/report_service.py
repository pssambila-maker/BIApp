"""Report service for generating and exporting reports."""
import io
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from uuid import UUID

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.core.query.executor import QueryExecutor
from app.core.query.sql_generator import SQLGenerator
from app.models.dashboard import Dashboard, DashboardWidget
from app.models.saved_query import SavedQuery
from app.models.semantic import SemanticEntity


class ReportService:
    """Service for generating reports from dashboards or saved queries."""

    def __init__(self):
        self.executor = QueryExecutor()
        self.export_dir = Path(settings.export_dir) / "reports"
        self.export_dir.mkdir(parents=True, exist_ok=True)

    async def execute_dashboard_queries(
        self,
        dashboard_id: UUID,
        user_id: UUID,
        db: AsyncSession
    ) -> Dict[str, pd.DataFrame]:
        """
        Execute all widget queries in a dashboard.

        Args:
            dashboard_id: Dashboard ID
            user_id: User ID (for ownership validation)
            db: Database session

        Returns:
            Dict mapping widget IDs to DataFrames

        Raises:
            ValueError: If dashboard not found or user doesn't own it
        """
        # Load dashboard with widgets
        result = await db.execute(
            select(Dashboard)
            .options(selectinload(Dashboard.widgets))
            .where(
                Dashboard.id == dashboard_id,
                Dashboard.owner_id == user_id
            )
        )
        dashboard = result.scalar_one_or_none()

        if not dashboard:
            raise ValueError(f"Dashboard {dashboard_id} not found or not accessible")

        widget_results = {}

        for widget in dashboard.widgets:
            try:
                df = await self._execute_widget_query(widget, user_id, db)
                widget_results[str(widget.id)] = df
            except Exception as e:
                # Log error but continue with other widgets
                print(f"Error executing widget {widget.id}: {e}")
                widget_results[str(widget.id)] = pd.DataFrame()

        return widget_results

    async def execute_saved_query(
        self,
        saved_query_id: UUID,
        user_id: UUID,
        db: AsyncSession
    ) -> pd.DataFrame:
        """
        Execute a saved query.

        Args:
            saved_query_id: SavedQuery ID
            user_id: User ID (for ownership validation)
            db: Database session

        Returns:
            DataFrame with query results

        Raises:
            ValueError: If saved query not found or user doesn't own it
        """
        # Load saved query
        result = await db.execute(
            select(SavedQuery).where(
                SavedQuery.id == saved_query_id,
                SavedQuery.owner_id == user_id
            )
        )
        saved_query = result.scalar_one_or_none()

        if not saved_query:
            raise ValueError(f"SavedQuery {saved_query_id} not found or not accessible")

        # Load entity
        result = await db.execute(
            select(SemanticEntity)
            .options(
                selectinload(SemanticEntity.dimensions),
                selectinload(SemanticEntity.measures)
            )
            .where(SemanticEntity.id == saved_query.entity_id)
        )
        entity = result.scalar_one_or_none()

        if not entity:
            raise ValueError(f"Entity {saved_query.entity_id} not found")

        # Extract query config
        config = saved_query.query_config
        dimension_ids = config.get('dimension_ids', [])
        measure_ids = config.get('measure_ids', [])
        filters = config.get('filters', [])
        limit = config.get('limit', 10000)

        # Generate SQL
        generator = SQLGenerator(entity)
        sql, params = generator.generate_sql(
            dimension_ids,
            measure_ids,
            filters,
            limit
        )

        # Find data source and execute
        data_source = await self.executor.find_data_source(
            entity.primary_table,
            user_id,
            db
        )

        df = await self.executor.execute_query(sql, params, data_source, db)
        return df

    async def _execute_widget_query(
        self,
        widget: DashboardWidget,
        user_id: UUID,
        db: AsyncSession
    ) -> pd.DataFrame:
        """Execute query for a single widget."""
        config = widget.query_config
        entity_id = config.get('entity_id')

        if not entity_id:
            raise ValueError(f"Widget {widget.id} has no entity_id")

        # Load entity
        result = await db.execute(
            select(SemanticEntity)
            .options(
                selectinload(SemanticEntity.dimensions),
                selectinload(SemanticEntity.measures)
            )
            .where(SemanticEntity.id == entity_id)
        )
        entity = result.scalar_one_or_none()

        if not entity:
            raise ValueError(f"Entity {entity_id} not found")

        # Extract query parameters
        dimension_ids = config.get('dimensions', [])
        measure_ids = config.get('measures', [])
        filters = config.get('filters', [])
        limit = config.get('limit', 1000)

        # Generate SQL
        generator = SQLGenerator(entity)
        sql, params = generator.generate_sql(
            dimension_ids,
            measure_ids,
            filters,
            limit
        )

        # Find data source and execute
        data_source = await self.executor.find_data_source(
            entity.primary_table,
            user_id,
            db
        )

        df = await self.executor.execute_query(sql, params, data_source, db)
        return df

    def generate_excel(
        self,
        data: pd.DataFrame,
        output_path: Optional[Path] = None,
        sheet_name: str = "Report"
    ) -> Path:
        """
        Generate Excel file from DataFrame.

        Args:
            data: DataFrame to export
            output_path: Output file path (auto-generated if None)
            sheet_name: Excel sheet name

        Returns:
            Path to generated Excel file
        """
        if output_path is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_path = self.export_dir / f"report_{timestamp}.xlsx"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to Excel with formatting
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            data.to_excel(writer, index=False, sheet_name=sheet_name)

            # Auto-adjust column widths
            worksheet = writer.sheets[sheet_name]
            for idx, col in enumerate(data.columns):
                max_length = max(
                    data[col].astype(str).str.len().max(),
                    len(str(col))
                )
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)

        return output_path

    def generate_csv(
        self,
        data: pd.DataFrame,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Generate CSV file from DataFrame.

        Args:
            data: DataFrame to export
            output_path: Output file path (auto-generated if None)

        Returns:
            Path to generated CSV file
        """
        if output_path is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_path = self.export_dir / f"report_{timestamp}.csv"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        data.to_csv(output_path, index=False)

        return output_path

    def generate_pdf(
        self,
        data: pd.DataFrame,
        output_path: Optional[Path] = None,
        title: str = "Report"
    ) -> Path:
        """
        Generate PDF file from DataFrame using weasyprint.

        Args:
            data: DataFrame to export
            output_path: Output file path (auto-generated if None)
            title: Report title

        Returns:
            Path to generated PDF file
        """
        if output_path is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_path = self.export_dir / f"report_{timestamp}.pdf"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert DataFrame to HTML table
        html_table = data.to_html(index=False, classes='data-table', border=0)

        # Create styled HTML document
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <style>
                @page {{
                    size: A4 landscape;
                    margin: 2cm;
                }}
                body {{
                    font-family: Arial, sans-serif;
                    font-size: 10pt;
                }}
                h1 {{
                    color: #333;
                    font-size: 18pt;
                    margin-bottom: 20px;
                }}
                .metadata {{
                    font-size: 9pt;
                    color: #666;
                    margin-bottom: 20px;
                }}
                table.data-table {{
                    border-collapse: collapse;
                    width: 100%;
                    font-size: 9pt;
                }}
                table.data-table th {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 8px;
                    text-align: left;
                    border: 1px solid #ddd;
                }}
                table.data-table td {{
                    padding: 6px;
                    border: 1px solid #ddd;
                }}
                table.data-table tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <div class="metadata">
                Generated on: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}<br>
                Total Rows: {len(data):,}
            </div>
            {html_table}
        </body>
        </html>
        """

        # Generate PDF using weasyprint
        try:
            from weasyprint import HTML
            HTML(string=html_content).write_pdf(output_path)
        except ImportError:
            raise ImportError("weasyprint is not installed. Install with: pip install weasyprint")

        return output_path

    def generate_html_email(
        self,
        data: pd.DataFrame,
        title: str = "Report",
        max_rows: int = 100
    ) -> str:
        """
        Generate HTML email body with data table.

        Args:
            data: DataFrame to include
            title: Email title
            max_rows: Maximum rows to include (to avoid huge emails)

        Returns:
            HTML string for email body
        """
        # Limit rows for email
        display_data = data.head(max_rows)
        truncated = len(data) > max_rows

        html_table = display_data.to_html(index=False, classes='data-table', border=0)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    color: #333;
                }}
                h2 {{
                    color: #4CAF50;
                }}
                .metadata {{
                    font-size: 12px;
                    color: #666;
                    margin-bottom: 15px;
                }}
                table.data-table {{
                    border-collapse: collapse;
                    width: 100%;
                    font-size: 12px;
                }}
                table.data-table th {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px;
                    text-align: left;
                    border: 1px solid #ddd;
                }}
                table.data-table td {{
                    padding: 8px;
                    border: 1px solid #ddd;
                }}
                table.data-table tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 11px;
                    color: #999;
                }}
            </style>
        </head>
        <body>
            <h2>{title}</h2>
            <div class="metadata">
                Generated on: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}<br>
                Total Rows: {len(data):,}
                {f'<br><em>(Showing first {max_rows} rows. Full data attached.)</em>' if truncated else ''}
            </div>
            {html_table}
            <div class="footer">
                This is an automated report from your BI Platform.
            </div>
        </body>
        </html>
        """

        return html_content

    async def generate_all_formats(
        self,
        data: pd.DataFrame,
        formats: List[str],
        report_name: str,
        report_dir: Path
    ) -> Dict[str, Path]:
        """
        Generate multiple formats at once.

        Args:
            data: DataFrame to export
            formats: List of formats ('excel', 'csv', 'pdf')
            report_name: Base name for files
            report_dir: Directory to save files

        Returns:
            Dict mapping format to file path
        """
        report_dir.mkdir(parents=True, exist_ok=True)
        generated_files = {}

        for fmt in formats:
            try:
                if fmt == 'excel':
                    path = report_dir / f"{report_name}.xlsx"
                    generated_files['excel'] = self.generate_excel(data, path)
                elif fmt == 'csv':
                    path = report_dir / f"{report_name}.csv"
                    generated_files['csv'] = self.generate_csv(data, path)
                elif fmt == 'pdf':
                    path = report_dir / f"{report_name}.pdf"
                    generated_files['pdf'] = self.generate_pdf(data, path, report_name)
            except Exception as e:
                print(f"Error generating {fmt}: {e}")
                continue

        return generated_files
