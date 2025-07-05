import pytest

from database.postgres import DatabaseConfig, PostgresClient


@pytest.mark.parametrize("bad_config, err_field", [
    ({"dbname": "", "user": "u", "password": "p"}, "dbname"),
    ({"dbname": "db", "user": " ", "password": "p"}, "user"),
    ({"dbname": "db", "user": "u", "password": ""}, "password"),
])
def test_database_config_invalid(bad_config, err_field):
    with pytest.raises(ValueError) as exc:
        DatabaseConfig(**bad_config)
    assert err_field in str(exc.value)


@pytest.fixture(autouse=True)
def mock_connect(mocker):
    return mocker.patch("database.postgres.psycopg2.connect")

def test_query_select_returns_rows(mock_connect):
    # Arrange
    expected = [(1, "a"), (2, "b")]
    cm = mock_connect.return_value
    cursor = cm.cursor.return_value.__enter__.return_value
    cursor.description = True
    cursor.fetchall.return_value = expected

    client = PostgresClient({"dbname":"db", "user":"u", "password":"p"})
    # Act
    rows = client.query("SELECT 1")
    # Assert
    assert rows == expected
    cursor.execute.assert_called_once_with("SELECT 1", None)


def test_close_closes_connection(mock_connect):
    conn = mock_connect.return_value
    conn.closed = False
    client = PostgresClient({"dbname":"db", "user":"u", "password":"p"})
    client.close()
    conn.close.assert_called()
