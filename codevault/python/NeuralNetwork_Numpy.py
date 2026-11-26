# Auto-generated Code Vault for 'NeuralNetwork (Numpy)' [Python]

import numpy as np
from typing import Callable, List, Tuple, Optional


def sigmoid(x: np.ndarray) -> np.ndarray:
    """Sigmoid activation function."""
    return 1.0 / (1.0 + np.exp(-x))


def sigmoid_derivative(x: np.ndarray) -> np.ndarray:
    """Derivative of sigmoid w.r.t. its input (assuming input already passed through sigmoid)."""
    s = sigmoid(x)
    return s * (1 - s)


def relu(x: np.ndarray) -> np.ndarray:
    """Rectified Linear Unit activation."""
    return np.maximum(0, x)


def relu_derivative(x: np.ndarray) -> np.ndarray:
    """Derivative of ReLU."""
    return (x > 0).astype(float)


def tanh(x: np.ndarray) -> np.ndarray:
    """Hyperbolic tangent activation."""
    return np.tanh(x)


def tanh_derivative(x: np.ndarray) -> np.ndarray:
    """Derivative of tanh."""
    return 1.0 - np.tanh(x) ** 2


ACTIVATIONS = {
    "sigmoid": (sigmoid, sigmoid_derivative),
    "relu": (relu, relu_derivative),
    "tanh": (tanh, tanh_derivative),
}


class NeuralNetwork:
    """
    A simple fully‑connected feed‑forward neural network using only NumPy.
    Supports an arbitrary number of hidden layers and three activation functions
    (sigmoid, ReLU, tanh).  Uses stochastic gradient descent with optional mini‑batching.
    """

    def __init__(
        self,
        layer_sizes: List[int],
        activation: str = "relu",
        learning_rate: float = 0.01,
        seed: Optional[int] = None,
    ) -> None:
        """
        Parameters
        ----------
        layer_sizes : list of int
            Sizes of each layer, including input and output. Example: [2, 4, 1]
        activation : {"relu", "sigmoid", "tanh"}
            Activation function for all hidden layers. Output layer uses sigmoid for
            binary classification or linear for regression (controlled by loss choice).
        learning_rate : float
            Step size for gradient descent.
        seed : int | None
            Random seed for reproducible weight initialization.
        """
        if activation not in ACTIVATIONS:
            raise ValueError(f"Unsupported activation '{activation}'. Choose from {list(ACTIVATIONS)}")
        self.activation_name = activation
        self.activation, self.activation_derivative = ACTIVATIONS[activation]
        self.learning_rate = float(learning_rate)

        self.rng = np.random.default_rng(seed)
        self.layer_sizes = layer_sizes
        self.n_layers = len(layer_sizes) - 1  # number of weight matrices

        # Weight matrices and bias vectors are stored as lists.
        self.weights: List[np.ndarray] = []
        self.biases: List[np.ndarray] = []
        self._initialize_parameters()

    def _initialize_parameters(self) -> None:
        """Initialize weights with He (for ReLU) or Xavier (for sigmoid/tanh) scheme."""
        for i in range(self.n_layers):
            fan_in = self.layer_sizes[i]
            fan_out = self.layer_sizes[i + 1]

            if self.activation_name == "relu":
                limit = np.sqrt(2.0 / fan_in)
            else:  # sigmoid or tanh
                limit = np.sqrt(1.0 / fan_in)

            w = self.rng.uniform(-limit, limit, size=(fan_in, fan_out))
            b = np.zeros(fan_out)
            self.weights.append(w)
            self.biases.append(b)

    def _forward(self, X: np.ndarray) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Perform a forward pass.

        Returns
        -------
        activations : list of np.ndarray
            Activations per layer (including input X as first element).
        pre_activations : list of np.ndarray
            Linear combinations (z = a·W + b) per layer before activation.
        """
        activations = [X]
        pre_activations = []

        for idx in range(self.n_layers):
            z = activations[-1] @ self.weights[idx] + self.biases[idx]
            pre_activations.append(z)

            # Use sigmoid on output layer if binary classification (2‑class) else linear.
            if idx == self.n_layers - 1:
                a = sigmoid(z) if self.layer_sizes[-1] == 1 else z
            else:
                a = self.activation(z)
            activations.append(a)

        return activations, pre_activations

    def _backward(
        self,
        activations: List[np.ndarray],
        pre_activations: List[np.ndarray],
        y_true: np.ndarray,
    ) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Back‑propagation to compute gradients of loss w.r.t. weights and biases.

        Returns
        -------
        grad_w : list of np.ndarray
            Gradient for each weight matrix.
        grad_b : list of np.ndarray
            Gradient for each bias vector.
        """
        # Determine loss derivative (using mean squared error for simplicity)
        y_pred = activations[-1]
        error = y_pred - y_true  # shape (batch, output)

        grad_w: List[np.ndarray] = [np.zeros_like(w) for w in self.weights]
        grad_b: List[np.ndarray] = [np.zeros_like(b) for b in self.biases]

        # Output layer gradient
        delta = error * (sigmoid_derivative(pre_activations[-1]) if self.layer_sizes[-1] == 1 else 1)

        for layer in reversed(range(self.n_layers)):
            a_prev = activations[layer]  # shape (batch, n_in)
            grad_w[layer] = a_prev.T @ delta / a_prev.shape[0]
            grad_b[layer] = np.mean(delta, axis=0)

            if layer > 0:
                # Propagate delta to previous layer
                dz = delta @ self.weights[layer].T
                delta = dz * self.activation_derivative(pre_activations[layer - 1])

        return grad_w, grad_b

    def _update_parameters(self, grad_w: List[np.ndarray], grad_b: List[np.ndarray]) -> None:
        """Apply SGD update."""
        for i in range(self.n_layers):
            self.weights[i] -= self.learning_rate * grad_w[i]
            self.biases[i] -= self.learning_rate * grad_b[i]

    @staticmethod
    def _mse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Mean squared error."""
        return np.mean((y_true - y_pred) ** 2)

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 1000,
        batch_size: Optional[int] = None,
        verbose: bool = False,
    ) -> None:
        """
        Train the network using SGD.

        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            Training data.
        y : np.ndarray, shape (n_samples, n_outputs)
            Target values.
        epochs : int
            Number of passes over the whole dataset.
        batch_size : int | None
            Size of mini‑batches. If None, use full‑batch gradient descent.
        verbose : bool
            Print loss every 100 epochs if True.
        """
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)

        if batch_size is None:
            batch_size = X.shape[0]

        for epoch in range(1, epochs + 1):
            # Shuffle indices each epoch
            perm = self.rng.permutation(X.shape[0])
            X_shuffled = X[perm]
            y_shuffled = y[perm]

            for start in range(0, X.shape[0], batch_size):
                end = start + batch_size
                xb = X_shuffled[start:end]
                yb = y_shuffled[start:end]

                activations, pre_activations = self._forward(xb)
                grad_w, grad_b = self._backward(activations, pre_activations, yb)
                self._update_parameters(grad_w, grad_b)

            if verbose and (epoch % 100 == 0 or epoch == 1):
                preds = self.predict(X)
                loss = self._mse(y, preds)
                print(f"Epoch {epoch:4d}/{epochs} - Loss: {loss:.6f}")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Return network output for given inputs."""
        X = np.asarray(X, dtype=float)
        activations, _ = self._forward(X)
        return activations[-1]

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> float:
        """Return MSE on a validation set."""
        preds = self.predict(X)
        return self._mse(y, preds)


if __name__ == "__main__":
    # Simple demo: learn XOR truth table
    X_demo = np.array([[0, 0],
                       [0, 1],
                       [1, 0],
                       [1, 1]], dtype=float)

    y_demo = np.array([[0],
                       [1],
                       [1],
                       [0]], dtype=float)

    # Network with 2 inputs, one hidden layer of 4 neurons, 1 output
    nn = NeuralNetwork(layer_sizes=[2, 4, 1],
                       activation="tanh",
                       learning_rate=0.1,
                       seed=42)

    nn.fit(X_demo, y_demo, epochs=5000, batch_size=4, verbose=True)

    predictions = nn.predict(X_demo)
    print("\nPredictions (rounded):")
    print(np.round(predictions, 3))

    print("\nRaw outputs:")
    print(predictions)
