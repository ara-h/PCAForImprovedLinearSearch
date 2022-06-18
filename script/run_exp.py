from sys import argv
from create_tables import create_tables
import generate_data
from transform_data import upload_transformed_data
from knn_search import run_comparison



if __name__ == "__main__":
    create_tables()

    # Expect five arguments: dimension, sample size, scale for random
    # covariance, number of neighbors
    _, d, N, s, k = argv
    d = int(d)
    N = int(N)
    s = float(s)
    k = int(k)

    # Randomly generate normally distributed data and upload
    generated_data = generate_data.random_sample(d, N, s)
    generate_data.insert_points(generated_data)

    # Do the PCA data transformation
    upload_transformed_data()

    # Run linear search with priority queue, first on original data and then on
    # transformed data
    run_comparison(d, N, k)
