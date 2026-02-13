import numpy as np
import pandas as pd
from scipy.linalg import pinv
from sklearn.decomposition import PCA

# --- ELM ---
class ExtremeLearningMachine:
    def __init__(self, n_hidden, activation='tanh', random_state=42, C=0.1):
        self.n_hidden = n_hidden
        self.activation = activation
        self.random_state = random_state
        self.C = C  # parâmetro de regularização para train_elm_regularized

    def _activation(self, x):
        if self.activation == 'sigmoid':
            return 1 / (1 + np.exp(-x))
        elif self.activation == 'tanh':
            return np.tanh(x)
        else:
            return x

    def fit(self, X, y, method='pinv'):
        np.random.seed(self.random_state)
        n_features = X.shape[1]
        self.W_h = np.random.uniform(-1, 1, size=(n_features, self.n_hidden))
        self.b_h = np.random.uniform(-1, 1, size=(1, self.n_hidden))
        H = self._activation(X @ self.W_h + self.b_h)

        if method == 'pinv':
            # Método clássico com pseudo-inversa
            H_pinv = pinv(H)
            self.W_out = H_pinv @ y

        elif method == 'quad':
            # Método train_elm (mínimos quadrados)
            self.W_out = self.train_elm(H, y)

        elif method == 'regularization':
            # Método train_elm_regularized (com regularização)
            self.W_out = self.train_elm_regularized(H, y, self.C)

        else:
            raise ValueError(f"Método '{method}' não suportado. Escolha entre 'pinv', 'train_elm' ou 'train_elm_regularized'.")

    def predict(self, X):
        H = self._activation(X @ self.W_h + self.b_h)
        return H @ self.W_out

    def train_elm(self, X_h, d):
        X_h_T = X_h.T
        W_out = np.linalg.pinv(X_h_T @ X_h) @ X_h_T @ d
        return W_out

    def train_elm_regularized(self, X_h, d, C):
        X_h_T = X_h.T
        I = np.eye(X_h.shape[1])
        W_out = np.linalg.inv(I / C + X_h_T @ X_h) @ X_h_T @ d
        return W_out


# --- Função auxiliar: Expansão de Volterra (2ª ordem) ---
def volterra_expansion(X, order=2):
    X_volterra = [X]
    if order >= 2:
        n = X.shape[1]
        quad_terms = [X[:, i] * X[:, j] for i in range(n) for j in range(i, n)]
        X_volterra.append(np.stack(quad_terms, axis=1))
    return np.concatenate(X_volterra, axis=1)


# --- Função auxiliar: PCA ---
def apply_pca(X, n_components=2):
    pca = PCA(n_components=n_components)
    X_reduced = pca.fit_transform(X)
    return X_reduced, pca


# --- ESN ---
class EchoStateNetwork:
    def __init__(self, n_reservoir, spectral_radius, random_state=42):
        self.n_reservoir = n_reservoir
        self.spectral_radius = spectral_radius
        self.random_state = random_state

    def _tanh(self, x):
        return np.tanh(x)

    def fit(self, X, y, volterra=False, pca=False, pca_components=None):
        np.random.seed(self.random_state)
        n_samples, n_features = X.shape

        self.W_in = np.random.uniform(-1, 1, (self.n_reservoir, n_features))

        probs = [0.95, 0.025, 0.025]
        values = [0, 0.4, -0.4]
        W_h = np.random.choice(values, size=(self.n_reservoir, self.n_reservoir), p=probs)

        eigvals = np.linalg.eigvals(W_h)
        emax = np.max(np.abs(eigvals))
        if emax == 0 or np.isnan(emax) or np.isinf(emax):
            emax = 1e-10
        self.W_h = W_h * (self.spectral_radius / emax)

        self.X_reservoir = np.zeros((n_samples, self.n_reservoir))
        for t in range(n_samples):
            u_t = X[t]
            x_prev = self.X_reservoir[t - 1] if t > 0 else np.zeros(self.n_reservoir)
            self.X_reservoir[t] = self._tanh(self.W_in @ u_t + self.W_h @ x_prev)
        # Aplicar PCA, se desejado
        if pca:
            self.X_reservoir, self.pca = apply_pca(self.X_reservoir, n_components=pca_components)
        # Aplicar expansão de Volterra, se desejado
        if volterra:
            self.X_reservoir = volterra_expansion(self.X_reservoir)


        X_pinv = pinv(self.X_reservoir)
        self.W_out = X_pinv @ y

    def predict(self, X):
        n_samples = X.shape[0]
        X_res = np.zeros((n_samples, self.n_reservoir))

        for t in range(n_samples):
            u_t = X[t]
            x_prev = X_res[t - 1] if t > 0 else np.zeros(self.n_reservoir)
            X_res[t] = self._tanh(self.W_in @ u_t + self.W_h @ x_prev)

        # Se houve Volterra ou PCA durante o treinamento, aplicar novamente na predição
        if hasattr(self, 'pca'):
            X_res = self.pca.transform(X_res)
            X_res = volterra_expansion(X_res)
            
        elif hasattr(self, 'X_reservoir') and self.X_reservoir.shape[1] != self.n_reservoir:
            X_res = volterra_expansion(X_res)

        return X_res @ self.W_out
