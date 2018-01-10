from kant.db.backends.postgresql import DatabaseWrapper


def test_create_table_should_return_sql_create_table():
    # arrange
    table_name = 'event_store'
    database_wrapper = DatabaseWrapper()
    # act
    sql = database_wrapper.create_table(name=table_name)
    # assert
    assert sql == 'CREATE TABLE event_store'