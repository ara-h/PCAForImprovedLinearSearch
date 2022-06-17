# Applying PCA for a skipping approach to kNN linear search

The purpose of this repository is to demonstrate the algorithm described by
Ajioka et al. [1].

## Background

Given a set of vectors and a query vector $q$, the task of the k nearest
neighbor search is to return the $k$ vectors closest to $q$.

## Demonstration

## Possible use cases

If data is subject to change on relatively small time-scales, a program
application using this approach can be run periodically on a table of
multi-dimensional data to create a new table that offers performance benefits
for the kNN search task.

## References

[1]: Ajioka, Shiro & Tsuge, Satoru & Shishibori, Masami & Kita, Kenji. (2006). Fast Multidimensional Nearest Neighbor Search Algorithm Using Priority Queue. Electrical Engineering in Japan. 164. 69 - 77. 10.1002/eej.20502.
