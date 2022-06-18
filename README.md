# Applying PCA for a skipping approach to kNN linear search

The purpose of this repository is to demonstrate a skipping approach to kNN
search, as described by Ajioka et al. [1].

## Background

Given a set of vectors and a query vector $q$, the task of the k nearest
neighbor (kNN) search is to return the $k$ vectors nearest to $q$. In a linear
search, the distance from $q$ is computed for every vector in the set. A running
collection of the $k$ best results is maintained while each vector in the set is
compared sequentially with $q$. An efficient approach maintains this collection
in a priority queue, so that the worst candidate can readily be eliminated once
a better candidate is found (with the next worst candidates kept close-by).
In our case, the priority queue is implemented as a descending heap. The
candidate to be replaced is maintained at the root of the heap.

When we come across a candidate vector $x_i$ and compute its distance from $q$,
we do an arithmetic operation in each dimension:

$$ d(q, x_i) = \sqrt{sum_{j=1}^d (q_j - x_{i,j})^2} $$

Say the worst candidate is distance $r$ from $q$. If the first summand is
already greater than $r$, then the rest of the calculations in the sum are
redundant. We can skip over them and move on to the next candidate. The basic
idea in the proposed algorithm observes that if there is a lot of variability
in the first component, then it is more likely that we can skip the unnecessary
arithmetic operations. We can dimension sort by variance so the distance
computation starts with most highly variable component and continues to the
least variable component. Even better, we can find the principal components of
the vector data: an orthogonal set of unit vectors where the $i$-th vector is in
the direction of greatest variability while being orthogonal to the first
$i - 1$ vectors. The principal components of the data are the eigenvectors of
the sample covariance matrix. Computing the eigenvectors and sorting them
descendingly by the size of their associated eigenvalues gives us an orthogonal
transformation, one that preserves distances and angles between vectors.
Applying this transformation to the data increases the likelihood that we can
detect unnecessary operations early on. 

## Demonstration

## Possible use cases

If data is subject to change on relatively small time-scales, a program
application using this approach can be run periodically on a table of
multi-dimensional data, creating a new table that offers performance benefits
for the kNN search task.

## References

[1]: Ajioka, Shiro & Tsuge, Satoru & Shishibori, Masami & Kita, Kenji. (2006). Fast Multidimensional Nearest Neighbor Search Algorithm Using Priority Queue. Electrical Engineering in Japan. 164. 69 - 77. 10.1002/eej.20502.
