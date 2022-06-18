import psycopg2 as psy
import numpy as np

from config import config

def load_from_database():
    conn = None

    try:
        params = config()
        conn = psy.connect(**params)
        cur = conn.cursor()

        cur.execute("SELECT * FROM points")
        rows = cur.fetchall()

        # Convert to numpy array
        l = []
        ids = []
        for row in rows:
            ids.append(row[0])
            l.append(row[1])

        vector_data = np.asarray(l)

        cur.close()
        return vector_data,ids
    except (Exception, psy.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def center_data(data):
    centered_data = np.zeros_like(data)

    sample_mean = []
    for col in range(data.shape[1]):
        m = np.mean(data[:,col])
        sample_mean.append(m)
        centered_data[:,col] = data[:,col] - m

    return sample_mean, centered_data


def get_sorting_permutation(eigenvalues):
    """
    Get the permutation matrix that, when applied to the data, results in the
    desired ordering. We do this to get a list of vectors in the eigenbasis,
    descendingly sorted by the size of the associated eigenvalue.
    """
    enum_eig = list(enumerate(eigenvalues.tolist()))
    sorted_eig_desc = sorted(enum_eig, key=lambda e: e[1], reverse=True)

    # Get map from new index to old index
    sigma = {i[1][0] : i[0] for i in enumerate(sorted_eig_desc)}

    d = len(sigma)
    I_n = np.eye(N=d, dtype=int) # An array of the standard basis vectors
    rows = [I_n[sigma[i],:] for i in range(d)] # Permute the rows by applying the map sigma
    P = np.array(rows) # Our permutation matrix as an ndarray

    return P


def get_sorted_eigendecomposition(X):
    """
    Return W, the matrix describing the desired transformation
    X : centered data matrix
    """
    C = np.cov(X.T)
    e_vals, e_vecs = np.linalg.eig(C)

    P = get_sorting_permutation(e_vals)

    W = (np.dot(P, e_vecs.T)).T

    return W


def apply_PCA_transformation(X):
    sample_mean, X_centered = center_data(X)
    W = get_sorted_eigendecomposition(X_centered)
    T = np.dot(X_centered, W)

    return sample_mean, W, T


def upload_transformed_data():
    X, X_id = load_from_database()

    mu_hat, W, T = apply_PCA_transformation(X)

    # Prepare data for insertion
    W_tuples = [(x[0][0],x[0][1],x[1]) for x in np.ndenumerate(W)]
    T_tuples = [(x[0],x[1].tolist()) for x in zip(X_id, T)]


    # Prepare SQL statements

    command1 = (
        """
        CREATE TABLE TransformedPoints (
        point_id SERIAL PRIMARY KEY,
        vec DOUBLE PRECISION ARRAY
        )
        """
    )

    command2 = (
        """
        CREATE TABLE TransformationMatrix (
        RowNo SMALLINT NOT NULL,
        ColNo SMALLINT NOT NULL,
        CellVal DOUBLE PRECISION DEFAULT 0,
        CONSTRAINT PK_MatrixEntry PRIMARY KEY (RowNo,ColNo)
        )
        """
    )

    command3 = (
        """
        CREATE TABLE MeanOffset (
        sample_mean_id SERIAL PRIMARY KEY,
        vec DOUBLE PRECISION ARRAY
        )
        """
    )

    conn = None
    try:
        params = config()
        conn = psy.connect(**params)
        cur = conn.cursor()

        # Establish table and insert sample mean
        cur.execute(""" DROP TABLE IF EXISTS MeanOffset """)
        cur.execute(command3)
        sql = """ INSERT INTO MeanOffset (vec) VALUES (%s) """
        cur.execute(sql, (mu_hat,))

        # Establish table and insert transformation matrix data
        cur.execute(""" DROP TABLE IF EXISTS TransformationMatrix """)
        cur.execute(command2)
        sql = """ INSERT INTO TransformationMatrix (RowNo,ColNo,CellVal) VALUES (%s,%s,%s) """
        cur.executemany(sql, W_tuples)

        # Establish table and insert transformed point data
        cur.execute(""" DROP TABLE IF EXISTS TransformedPoints """)
        cur.execute(command1)
        sql = """ INSERT INTO TransformedPoints (point_id,vec) VALUES (%s,%s) """
        cur.executemany(sql,T_tuples)

        conn.commit()
        cur.close()
    except (Exception, psy.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
