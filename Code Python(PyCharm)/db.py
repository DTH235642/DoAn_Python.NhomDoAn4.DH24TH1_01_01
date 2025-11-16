import pyodbc

CONN_STR = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=DESKTOP-FNA0NBN;"          
    "Database=QuanLySach;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"  # tránh lỗi certificate nếu dùng driver 18
)
# ---------------------- #

def get_conn():
    return pyodbc.connect(CONN_STR, autocommit=True)

def fetch_all(query, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    cols = [column[0] for column in cur.description] if cur.description else []
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return cols, rows

def fetch_one(query, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def execute(query, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    cur.close()
    conn.close()
