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

import pytest
from psycopg2 import ProgrammingError


@pytest.fixture(autouse=True)
def mock_connect(mocker):
    return mocker.patch("psycopg2.connect")

def test_query_select_returns_rows(mock_connect):
    # Arrange
    expected = [(1, "a"), (2, "b")]
    cursor = mock_connect.return_value.cursor.return_value
    cursor.description = True  # simulate SELECT
    cursor.fetchall.return_value = expected

    client = PostgresClient({"dbname":"db", "user":"u", "password":"p"})
    # Act
    rows = client.query("SELECT 1")
    # Assert
    assert rows == expected
    cursor.execute.assert_called_once_with("SELECT 1", None)

def test_query_no_results(mock_connect):
    cursor = mock_connect.return_value.cursor.return_value
    cursor.description = None
    cursor.fetchall.return_value = None

    client = PostgresClient({"dbname":"db", "user":"u", "password":"p"})
    assert client.query("DO NOTHING") is None

def test_query_reconnect_on_closed(mock_connect):
    cursor = mock_connect.return_value.cursor.return_value
    cursor.description = True
    cursor.fetchall.return_value = [(42,)]
    client = PostgresClient({"dbname":"db", "user":"u", "password":"p"})
    client.conn.closed = True
    rows = client.query("SELECT 42")
    assert rows == [(42,)]

def test_query_psycopg2_error_rollback(mock_connect):
    cursor = mock_connect.return_value.cursor.return_value
    cursor.execute.side_effect = ProgrammingError("bad")
    client = PostgresClient({"dbname":"db", "user":"u", "password":"p"})
    with pytest.raises(ProgrammingError):
        client.query("BAD SQL")
    mock_connect.return_value.rollback.assert_called()

@pytest.mark.parametrize("method, sql", [
    ("execute", "INSERT 1"),
    ("execute", "UPDATE foo"),
])
def test_execute_success_and_error(mock_connect, method, sql):
    cursor = mock_connect.return_value.cursor.return_value
    # success
    cursor.rowcount = 3
    client = PostgresClient({"dbname":"db", "user":"u", "password":"p"})
    count = getattr(client, method)(sql)
    assert count == 3
    cursor.execute.assert_called_with(sql, None)
    mock_connect.return_value.commit.assert_called()
    # error
    cursor.execute.side_effect = ProgrammingError("fail")
    with pytest.raises(ProgrammingError):
        getattr(client, method)(sql)
    mock_connect.return_value.rollback.assert_called()

def test_close_closes_connection(mock_connect):
    conn = mock_connect.return_value
    client = PostgresClient({"dbname":"db", "user":"u", "password":"p"})
    client.close()
    conn.close.assert_called()
