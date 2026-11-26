# Auto-generated Code Vault for 'NeuralNetwork' [Python]

import numpy as np
from typing import Callable, List, Tuple, Optional


def sigmoid(x: np.ndarray) -> np.ndarray:
    """Sigmoid activation function."""
    return 1.0 / (1.0 + np.exp(-x))


def sigmoid_derivative(x: np.ndarray) -> np.ndarray:
    """Derivative of sigmoid given the activation output."""
    s = sigmoid(x)
    return s * (1 - s)


def relu(x: np.ndarray) -> np.ndarray:
    """ReLU activation function."""
    return np.maximum(0, x)


def relu_derivative(x: np.ndarray) -> np.ndarray:
    """Derivative of ReLU."""
    return (x > 0).astype(x.dtype)


def softmax(x: np.ndarray) -> np.ndarray:
    """Softmax activation (row‑wise)."""
    e_x = np.exp(x - np.max(x, axis=1, keepdims=True))
    return e_x / np.sum(e_x, axis=1, keepdims=True)


def softmax_derivative(_):
    """Placeholder – gradient for softmax combined with cross‑entropy is simplified."""
    raise NotImplementedError("Use cross‑entropy gradient directly with softmax output.")


def mse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean squared error loss."""
    return np.mean(np.square(y_true - y_pred))


def mse_derivative(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """Derivative of MSE w.r.t. predictions."""
    return 2 * (y_pred - y_true) / y_true.shape[0]


def cross_entropy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Cross‑entropy loss for one‑hot encoded targets."""
    eps = 1e-15
    y_pred = np.clip(y_pred, eps, 1 - eps)
    return -np.mean(np.sum(y_true * np.log(y_pred), axis=1))


def cross_entropy_derivative(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """Derivative of cross‑entropy loss w.r.t. softmax predictions."""
    eps = 1e-15
    y_pred = np.clip(y_pred, eps, 1 - eps)
    return (y_pred - y_true) / y_true.shape[0]


class Layer:
    """Fully connected layer with optional activation."""

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        activation: Callable[[np.ndarray], np.ndarray] = lambda x: x,
        activation_derivative: Callable[[np.ndarray], np.ndarray] = lambda x: np.ones_like(x),
    ):
        """
        Parameters
        ----------
        input_dim : int
            Number of input features.
        output_dim : int
            Number of neurons in the layer.
        activation : Callable
            Activation function applied to the linear output.
        activation_derivative : Callable
            Derivative of the activation function (w.r.t. linear output).
        """
        limit = np.sqrt(6 / (input_dim + output_dim))
        self.weights = np.random.uniform(-limit, limit, (input_dim, output_dim))
        self.biases = np.zeros((1, output_dim))
        self.activation = activation
        self.activation_derivative = activation_derivative

        # Cache for backward pass
        self._input: Optional[np.ndarray] = None
        self._linear_output: Optional[np.ndarray] = None

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Compute forward pass."""
        self._input = x
        self._linear_output = x @ self.weights + self.biases
        return self.activation(self._linear_output)

    def backward(self, grad_output: np.ndarray, learning_rate: float) -> np.ndarray:
        """
        Backpropagate through this layer.

        Parameters
        ----------
        grad_output : np.ndarray
            Gradient of loss w.r.t. layer output.
        learning_rate : float
            Step size for parameter update.

        Returns
        -------
        np.ndarray
            Gradient of loss w.r.t. layer input.
        """
        if self._input is None or self._linear_output is None:
            raise RuntimeError("Must call forward() before backward().")

        # Gradient w.r.t. linear output (pre‑activation)
        grad_activation = grad_output * self.activation_derivative(self._linear_output)

        # Gradients w.r.t. parameters
        grad_weights = self._input.T @ grad_activation
        grad_biases = np.sum(grad_activation, axis=0, keepdims=True)

        # Parameter update
        self.weights -= learning_rate * grad_weights
        self.biases -= learning_rate * grad_biases

        # Return gradient w.r.t. input for previous layer
        return grad_activation @ self.weights.T


class NeuralNetwork:
    """Simple feed‑forward neural network using only NumPy."""

    def __init__(self):
        self.layers: List[Layer] = []
        self.loss_fn: Callable[[np.ndarray, np.ndarray], float] = mse
        self.loss_grad_fn: Callable[[np.ndarray, np.ndarray], np.ndarray] = mse_derivative

    def add_layer(
        self,
        output_dim: int,
        activation: str = "linear",
    ) -> None:
        """
        Append a fully connected layer.

        Parameters
        ----------
        output_dim : int
            Number of neurons in the new layer.
        activation : str
            Name of activation function ('linear', 'sigmoid', 'relu', 'softmax').
        """
        activation = activation.lower()
        act_fn, act_grad = {
            "linear": (lambda x: x, lambda x: np.ones_like(x)),
            "sigmoid": (sigmoid, sigmoid_derivative),
            "relu": (relu, relu_derivative),
            "softmax": (softmax, softmax_derivative),  # gradient handled specially
        }[activation]

        input_dim = self.layers[-1].weights.shape[1] if self.layers else None
        if input_dim is None:
            raise ValueError("First layer must be added after defining input dimension via `initialize`.")
        self.layers.append(Layer(input_dim, output_dim, act_fn, act_grad))

    def initialize(self, input_dim: int) -> None:
        """
        Define the input dimension of the network. Must be called before adding the first layer.

        Parameters
        ----------
        input_dim : int
            Number of features for the input data.
        """
        if self.layers:
            raise RuntimeError("Network already initialized.")
        # Dummy first layer to hold the input dimension; will be replaced on first add_layer call.
        self._input_dim = input_dim

    def _create_first_layer(self, output_dim: int, activation: str) -> None:
        """Internal helper to create the first layer based on stored input dimension."""
        activation = activation.lower()
        act_fn, act_grad = {
            "linear": (lambda x: x, lambda x: np.ones_like(x)),
            "sigmoid": (sigmoid, sigmoid_derivative),
            "relu": (relu, relu_derivative),
            "softmax": (softmax, softmax_derivative),
        }[activation]
        self.layers.append(Layer(self._input_dim, output_dim, act_fn, act_grad))

    def add_layer(
        self,
        output_dim: int,
        activation: str = "linear",
    ) -> None:
        """Public method to add layers; handles first layer creation."""
        if not hasattr(self, "_input_dim"):
            raise RuntimeError("Call `initialize(input_dim)` before adding layers.")
        if not self.layers:
            self._create_first_layer(output_dim, activation)
        else:
            self._add_subsequent_layer(output_dim, activation)

    def _add_subsequent_layer(self, output_dim: int, activation: str) -> None:
        activation = activation.lower()
        act_fn, act_grad = {
            "linear": (lambda x: x, lambda x: np.ones_like(x)),
            "sigmoid": (sigmoid, sigmoid_derivative),
            "relu": (relu, relu_derivative),
            "softmax": (softmax, softmax_derivative),
        }[activation]
        input_dim = self.layers[-1].weights.shape[1]
        self.layers.append(Layer(input_dim, output_dim, act_fn, act_grad))

    def set_loss(self, loss: str = "mse") -> None:
        """
        Choose a loss function.

        Parameters
        ----------
        loss : str
            'mse' for mean squared error or 'cross_entropy' for classification.
        """
        loss = loss.lower()
        if loss == "mse":
            self.loss_fn = mse
            self.loss_grad_fn = mse_derivative
        elif loss == "cross_entropy":
            self.loss_fn = cross_entropy
            self.loss_grad_fn = cross_entropy_derivative
        else:
            raise ValueError(f"Unsupported loss '{loss}'. Choose 'mse' or 'cross_entropy'.")

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Run a forward pass through all layers."""
        for layer in self.layers:
            x = layer.forward(x)
        return x

    def backward(self, y_true: np.ndarray, y_pred: np.ndarray, learning_rate: float) -> None:
        """Backpropagate error and update parameters."""
        grad = self.loss_grad_fn(y_true, y_pred)
        # Special case: if last activation is softmax with cross‑entropy, gradient is already (y_pred - y_true)
        for layer in reversed(self.layers):
            grad = layer.backward(grad, learning_rate)

    def predict(self, x: np.ndarray) -> np.ndarray:
        """Return network output for given input."""
        return self.forward(x)

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 100,
        batch_size: int = 32,
        learning_rate: float = 0.01,
        verbose: bool = True,
        validation_data: Optional[Tuple[np.ndarray, np.ndarray]] = None,
    ) -> List[float]:
        """
        Train the network using mini‑batch gradient descent.

        Returns
        -------
        List[float]
            Training loss per epoch.
        """
        n_samples = X.shape[0]
        history = []

        for epoch in range(1, epochs + 1):
            # Shuffle data each epoch
            indices = np.random.permutation(n_samples)
            X_shuffled = X[indices]
            y_shuffled = y[indices]

            epoch_loss = 0.0
            for start in range(0, n_samples, batch_size):
                end = start + batch_size
                xb = X_shuffled[start:end]
                yb = y_shuffled[start:end]

                preds = self.forward(xb)
                loss = self.loss_fn(yb, preds)
                epoch_loss += loss * xb.shape[0]

                self.backward(yb, preds, learning_rate)

            epoch_loss /= n_samples
            history.append(epoch_loss)

            if verbose:
                msg = f"Epoch {epoch}/{epochs} - loss: {epoch_loss:.6f}"
                if validation_data:
                    val_X, val_y = validation_data
                    val_pred = self.predict(val_X)
                    val_loss = self.loss_fn(val_y, val_pred)
                    msg += f" - val_loss: {val_loss:.6f}"
                print(msg)

        return history


if __name__ == "__main__":
    # Simple demonstration on a synthetic binary classification problem (XOR)
    np.random.seed(42)

    # XOR dataset
    X = np.array([[0, 0],
                  [0, 1],
                  [1, 0],
                  [1, 1]], dtype=np.float32)
    y = np.array([[0],
                  [1],
                  [1],
                  [0]], dtype=np.float32)  # one‑hot not needed for binary cross‑entropy

    # Build network
    nn = NeuralNetwork()
    nn.initialize(input_dim=2)
    nn.add_layer(output_dim=4, activation="relu")
    nn.add_layer(output_dim=1, activation="sigmoid")
    nn.set_loss("mse")  # Using MSE for simplicity on binary output

    # Train
    nn.fit(X, y, epochs=5000, batch_size=4, learning_rate=0.1, verbose=False)

    # Predict
    preds = nn.predict(X)
    print("Input:\n", X)
    print("Predicted probabilities:\n", preds)
    print("Rounded predictions:\n", np.rint(preds))
