import psycopg2 as psy
import numpy as np
import heapq as hq

from config import config

rng = np.random.default_rng(seed=2022)


# Functions for loading the original data and the transformed data

def matrix_loading_helper(matrix_entry_list, d):
    W = np.empty(shape=(d,d))
    for row in matrix_entry_list:
        W[row[0]][row[1]] = row[2]
    return W


def points_loading_helper(points_list):
    l = []
    ids = []
    for row in points_list:
        ids.append(row[0])
        r = np.around(row[1], decimals=8)
        l.append(r)
    result = np.asarray(l)
    return ids, result


def load_from_database(d):
    """
    d : expected row length of transformation matrix
    """
    conn = None

    try:
        params = config()
        conn = psy.connect(**params)
        cur = conn.cursor()

        cur.execute("SELECT * FROM Points")
        x_rows = cur.fetchall()
        X_ids, X = points_loading_helper(x_rows)

        cur.execute("SELECT * FROM TransformedPoints")
        y_rows = cur.fetchall()
        Y_ids, Y = points_loading_helper(y_rows)

        cur.execute("SELECT * FROM TransformationMatrix")
        w_rows = cur.fetchall()
        W = matrix_loading_helper(w_rows, d)

        cur.execute("SELECT * FROM MeanOffset ORDER BY sample_mean_id DESC LIMIT 1")
        mu_hat = (cur.fetchone())[1]

        cur.close()
        return X_ids, X, Y_ids, Y, W, mu_hat
    except (Exception, psy.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


# To use with heapq

class CompareKV:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __str__(self):
        return f'Point<{self.key}, {self.value}>'

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self,other):
        return self.value > other.value

    def getKey(self):
        return self.key


# The nearest neighbors search
def knn_search(x, ids, q, k, d, N):
    """
    x : data
    ids : their primary keys
    q : the query vector
    k : number of nearest neighbors to return
    d : data dimension
    N : number of observations in data
    """
    iteration_tracker = 0
    h = [] # heap

    # Calculate distances for the first k data
    i = 0
    while (i < k):
        dist = 0.0
        j = 0
        while (j < d):
            iteration_tracker += 1
            dist += (q[j]-x[i][j])*(q[j]-x[i][j])
            j += 1
        hq.heappush(h,CompareKV(i,-dist))
        i += 1

    # h[0].value should maintain the largest distance value

    while (i < N):
        dist = 0.0
        j = 0
        while (j < d):
            iteration_tracker += 1
            dist += (q[j]-x[i][j])*(q[j]-x[i][j])
            j += 1
            if (-dist < h[0].value):
                break
        if (-dist > h[0].value):
            h[0] = CompareKV(i,-dist)
            hq.heapify(h)
        i += 1

    result = []
    for CompareKV_object in h:
        idx = ids[CompareKV_object.key]
        result.append(idx)

    return result, iteration_tracker


def run_comparison(d, N, K):
    Q = rng.uniform(low=-14.0, high=14.0, size=d)
    Q = np.around(Q, decimals=8)

    X_id, X, Y_id, Y, W, mu_hat = load_from_database(d)

    result_1, it1 = knn_search(X, X_id, Q, K, d, N)

    transformed_query = np.dot(np.asarray(Q) - np.asarray(mu_hat), W)

    result_2, it2 = knn_search(Y, Y_id, transformed_query, K, d, N)

    print("Linear search in standard basis: " + str(it1) + " iterations")
    print("Linear search in new basis: " + str(it2) + " iterations")
