import pytest
from unittest.mock import MagicMock, patch
from src.database.handler import DatabaseHandler
from config.constants import Constants

@pytest.fixture
def db_handler():
    """Fixture to create a DatabaseHandler with dummy credentials."""
    return DatabaseHandler(
        host="localhost",
        port=3306,
        user="test",
        password="test",
        database="test_db"
    )

def test_insert_feeding_record_sql(db_handler):
    """Test that insert_feeding_record executes the correct SQL."""
    with patch("pymysql.connect") as mock_connect:
        # Setup mock cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Run the method
        result = db_handler.insert_feeding_record(
            food_weight=50.5,
            amount=2500.0,
            status_mount="normal",
            motor="open"
        )
        
        # Verify success
        assert result is True
        
        # Verify SQL execution
        mock_cursor.execute.assert_called_once()
        args, _ = mock_cursor.execute.call_args
        query = args[0]
        params = args[1]
        
        assert "INSERT INTO" in query
        assert Constants.TABLE_FEEDING_HISTORY in query
        assert params == (50.5, 2500.0, "normal", "open")
        mock_conn.commit.assert_called_once()

def test_get_latest_weight_parsing(db_handler):
    """Test parsing of database results for latest weight."""
    with patch("pymysql.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Simulate returning a record
        mock_cursor.fetchone.return_value = {Constants.COLUMN_FOOD_WEIGHT: 75.0}
        
        weight = db_handler.get_latest_food_weight()
        
        assert weight == 75.0
        assert "SELECT" in mock_cursor.execute.call_args[0][0]
