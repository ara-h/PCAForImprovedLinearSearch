import psycopg2
from config import config


def create_tables():
    commands = (
        """
        DROP TABLE IF EXISTS Points
        """,
        """
        CREATE TABLE Points (
        point_id SERIAL PRIMARY KEY,
        vec DOUBLE PRECISION ARRAY
        )
        """,
    )

    conn = None

    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        for command in commands:
            cur.execute(command)

        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    create_tables()
