import numpy as np
import psycopg2 as psy
from scipy.stats import multivariate_normal

from config import config

rng = np.random.default_rng(seed=2022)


def random_sample(d, N, scale, alpha=0.4, beta=0.4):
    """
    d : dimension of data, i.e. number of features in each observation
    N : number of observations
    scale : scale beta distribution to get different magnitudes in covariance
    alpha : beta distribution shape parameter, must be > 0
    beta : beta distribution shape parameter, must be > 0

    Default values for shape parameters chosen to illustrate a scenario where
    there are both strong and weak associative relationships in the data
    """
    # Generate a random covariance matrix.

    # First, generate a real d by d matrix
    U = scale * rng.beta(a=alpha, b=beta, size=(d,d))
    # Then, compute U^{T}U to get a real positive-definite matrix
    V = np.dot(U.T, U)

    # Use this matrix to specify a normal distribution. Draw N samples from it.

    data = multivariate_normal.rvs(cov=V, size=N)
    data = np.around(data, decimals=8)

    return data


def insert_points(data):
    """ insert data into database """
    records = []
    for i in range(0,np.shape(data)[0]):
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
    pass
