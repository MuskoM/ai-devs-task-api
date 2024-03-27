import sqlite3

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)


def create_table(conn):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """

    create_table_sql = '''CREATE TABLE IF NOT EXISTS tasks (
                            id integer PRIMARY KEY,
                            name text NOT NULL,
                            isComplete boolean NOT NULL
                            );
    '''
    
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)

def create_task(conn, task):
    """
    Create a new task
    :param conn:
    :param task:
    :return:
    """

    sql = ''' INSERT INTO tasks(name,isComplete)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()

    return cur.lastrowid

def update_task(conn, task):
    """
    update priority, begin_date, and end date of a task
    :param conn:
    :param task:
    :return: project id
    """
    sql = ''' UPDATE tasks
              SET isComplete = ? 
              WHERE name = ?'''
    cur = conn.cursor()
    c :sqlite3.Cursor = cur.execute(sql, task)
    conn.commit()


def get_task(conn, taskName):
    sql = ''' SELECT *
              FROM tasks
              WHERE name = ?
    '''
    cur = conn.cursor()
    return cur.execute(sql, taskName)


def get_tasks(conn):
    sql = ''' SELECT *
              FROM tasks
    '''
    cur = conn.cursor()
    return cur.execute(sql)