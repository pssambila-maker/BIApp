"""Utility functions for data connectors."""
from app.models.data_source import DataSource
from app.core.connectors.csv import CSVConnector
from app.core.connectors.excel import ExcelConnector
from app.core.connectors.postgresql import PostgreSQLConnector
from app.core.connectors.mysql import MySQLConnector


def get_connector(data_source: DataSource):
    """
    Get appropriate connector for a data source.

    Args:
        data_source: DataSource model instance

    Returns:
        Connector instance

    Raises:
        ValueError: If data source type is unknown
    """
    connector_map = {
        "csv": CSVConnector,
        "excel": ExcelConnector,
        "postgresql": PostgreSQLConnector,
        "mysql": MySQLConnector,
    }

    connector_class = connector_map.get(data_source.type)
    if not connector_class:
        raise ValueError(f"Unknown data source type: {data_source.type}")

    return connector_class(data_source.connection_config)
