import sqlite3


def get_query_results(query, row_count=None):
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    cursor.execute(query)

    if row_count is not None:
        results = cursor.fetchmany(size=row_count)
    else:
        results = cursor.fetchall()
    connection.close()

    return results


def execute_query(query):
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    cursor.executescript(query)
    connection.close()


def get_user(user_id):
    user = get_query_results(
        "SELECT * FROM user"
        " WHERE id = {}".format(user_id)
    )
    if not user:
        return None
    else:
        user_row = user[0]
        return {
            'id': int(user_row[0]),
            'user_state': user_row[1],
            'desired_type': user_row[2],
            'desired_model': user_row[3],
            'money': int(user_row[4])
        }


def create_user(user_id):
    execute_query(
        "INSERT INTO user"
        " values({}, 'select_operation', 'type', 'model', 1000)"
        .format(user_id)
    )


def update_user(user_id, fields: tuple, field_values: tuple):
    set_expr = ''
    for field, field_value in zip(fields, field_values):
        set_expr += field + '=' + field_value + ','
    set_expr = set_expr[:-1]

    execute_query(
        "UPDATE user SET {}"
        " WHERE id = {}"
        .format(set_expr, user_id)
   )


def insert_device(data):
    execute_query(
        "INSERT INTO device (device_type, model, price, months, seller_id)"
        " VALUES ('{}', '{}', {}, {}, {})"
        .format(*data)
    )


def get_device_with_condition(condition):
    device = get_query_results(
        "SELECT * FROM device"
        " WHERE {}"
        .format(condition),
        row_count=1
    )

    if not device:
        return None
    else:
        device_row = device[0]
        return {
            'id': int(device_row[0]),
            'device_type': device_row[1],
            'model': device_row[2],
            'price': int(device_row[3]),
            'months': int(device_row[4]),
            'seller_id': int(device_row[5])
        }


def delete_device(device_id):
    execute_query(
        "DELETE FROM device"
        " WHERE id = {}".format(device_id)
    )
