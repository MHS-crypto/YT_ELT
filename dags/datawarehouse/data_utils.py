from airflow.providers.postgres.hooks.postgres import PostgresHook
from pyscopg2.extras import RealidctCursor

table = "yt_api"


def get_postgres_connection():
    pg_hook = PostgresHook(postgres_conn_id="postgres_db_yt_elt", database="yt_elt")
    conn = pg_hook.get_conn()
    cur = conn.cursor(cursor_factory=RealidctCursor)
    return conn, cur


def close_postgres_connection(conn, cur):
    cur.close()
    conn.close()


def create_schema(schema):
    conn, cur = get_postgres_connection()
    query = f"CREATE SCHEMA IF NOT EXISTS {schema};"
    cur.execute(query)
    conn.commit()
    close_postgres_connection(conn, cur)


def create_table(schema):
    conn, cur = get_postgres_connection()
    if schema == "staging":
        table_sql = f"""
        CREATE TABLE IF NOT EXISTS {schema}.{table} (
                    "Video_ID" VARCHAR(11) PRIMARY KEY NOT NULL,
                    "Video_Title" TEXT NOT NULL,
                    "Upload_Date" TIMESTAMP NOT NULL,
                    "Duration" VARCHAR(20) NOT NULL,
                    "Video_Views" INT,
                    "Likes_Count" INT,
                    "Comments_Count" INT   
                );
        """
    else:
        table_sql = f"""
                  CREATE TABLE IF NOT EXISTS {schema}.{table} (
                      "Video_ID" VARCHAR(11) PRIMARY KEY NOT NULL,
                      "Video_Title" TEXT NOT NULL,
                      "Upload_Date" TIMESTAMP NOT NULL,
                      "Duration" TIME NOT NULL,
                      "Video_Type" VARCHAR(10) NOT NULL,
                      "Video_Views" INT,
                      "Likes_Count" INT,
                      "Comments_Count" INT    
                  ); 
              """
    cur.execute(table_sql)
    conn.commit()
    close_postgres_connection(conn, cur)


def get_video_ids(cur, schema):

    cur.execute(f"""SELECT "Video_ID" FROM {schema}.{table};""")
    ids = cur.fetchall()

    video_ids = [row["Video_ID"] for row in ids]

    return video_ids
