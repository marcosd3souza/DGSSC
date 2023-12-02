import numpy as np
# from matplotlib import pyplot as plt
# from scipy import sparse
# from scipy.ndimage import gaussian_filter
from sklearn.metrics import pairwise_distances

# NTD
# import tensorly as tl
from sklearn.neighbors import kneighbors_graph
# from tensorly.decomposition import non_negative_tucker, tucker

#NMF
from sklearn.decomposition import NMF

from src import RNMF


class MatrixFactorization:
    def __init__(self, X, D=None, verbose=False):
        if D is None:
            self.D = pairwise_distances(X)
            self.X = np.sort(X, axis=0)
        else:
            self.D = D
        self.verbose = verbose
        self.errors = []
        if verbose:
            print(f'initial dispersion in D: {np.std(self.D.flatten())}')

    def rNMF(self, n_components=10):
        rnmf = RNMF.RobustNMF(self.D, n_components, 2, 30)
        rnmf.fit()

        return rnmf.W.dot(rnmf.H) + rnmf.S

    def NMF(self, n_components=5):
        nmf = NMF(
            n_components=n_components,
            init='random',
            max_iter=300
        )

        W = nmf.fit_transform(self.D)
        H = nmf.components_

        # error = nmf.reconstruction_err_

        return W.dot(H)

    def similarity_graph(self):

        best_D, _ = self.nNMF()

        S = kneighbors_graph(best_D, n_neighbors=5, mode='connectivity').toarray()

        # best_D = pairwise_distances(best_W)
        return S

    def nNMF(self, n_components=10):
        nmf = NMF(
            n_components=n_components,
            init='random',
            max_iter=300
        )

        D_control = self.D

        # best_D = None
        best_loss = np.inf
        candidates = []
        for it in range(30):
            W = nmf.fit_transform(D_control)
            H = nmf.components_

            error = nmf.reconstruction_err_
            self.errors.append(error)

            W_norm = np.linalg.norm(W, axis=1).reshape(-1, 1)
            H_norm = np.linalg.norm(H, axis=0).reshape(1, -1)

            # if error < best_loss:
            #     best_loss = error
            #     best_D = D_control
                # best_W = W

            D_control = W_norm.dot(H_norm)
            candidates.append(D_control)

            if error == np.inf:
                break

            # print(f'it: {it} - recon error: {error}')
        derivatives = [abs(self.errors[i] - self.errors[i-1]) - abs(self.errors[i+1] - self.errors[i]) for i in range(2, 20)]
        idx = np.where(np.array(derivatives) < 0)[0][1] + 2
        best_D = candidates[idx]

        # for i, v in enumerate(derivatives):
        #     if v < 0:
        #         best_D = candidates[i+2]
        #         break

        return best_D, best_loss
