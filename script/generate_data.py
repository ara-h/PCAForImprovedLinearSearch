import numpy as np
import psycopg2 as psy
from scipy.stats import multivariate_normal

from config import config

rng = np.random.default_rng(seed=2022)

d = 48 # number of dimensions (columns)
n = 1000 # number of data (rows)


""" Generate a random covariance matrix. """

# First, generate a real d by d matrix
# Could add command line arguments to manipulate the distribution to sample
U = 10.0 * rng.beta(a=0.4, b=0.4, size=(d,d))
# Then, compute U^{T}U to get a real positive-definite matrix
V = np.dot(U.T, U)


""" Use this matrix to specify a normal distribution. Draw n samples from it. """

generated_data = multivariate_normal.rvs(cov=V, size=n)
generated_data = np.around(generated_data, decimals=8)


""" Insert data into table of vectors """

def insert_points(data):
    """ data: n by d numpy array """


    records = []
    for i in range(0,n):
        entry = (data[i,:]).tolist()
        records.append((entry,))

    sql = """ INSERT INTO Points (vec) VALUES (%s) """

    conn = None

    try:
        params = config()
        conn = psy.connect(**params)
        cur = conn.cursor()

        cur.executemany(sql, records)

        conn.commit()
        cur.close()
    except (Exception, psy.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    insert_points(generated_data)
