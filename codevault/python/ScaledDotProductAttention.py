# Auto-generated Code Vault for 'ScaledDotProductAttention' [Python]

import numpy as np

class ScaledDotProductAttention:
    def __init__(self, scale=None):
        """
        Initialize the Scaled Dot-Product Attention mechanism.

        Args:
            scale (float, optional): The scaling factor. Defaults to None, which means the scaling factor will be the square root of the key's embedding dimension.
        """
        self.scale = scale

    def _calculate_scale(self, key):
        """
        Calculate the scaling factor if it's not provided.

        Args:
            key (np.ndarray): The key matrix.

        Returns:
            float: The scaling factor.
        """
        if self.scale is None:
            return 1 / np.sqrt(key.shape[-1])
        return self.scale

    def _calculate_attention_weights(self, query, key):
        """
        Calculate the attention weights using the scaled dot-product attention mechanism.

        Args:
            query (np.ndarray): The query matrix.
            key (np.ndarray): The key matrix.

        Returns:
            np.ndarray: The attention weights.
        """
        scale = self._calculate_scale(key)
        attention_weights = np.matmul(query, key.T) * scale
        return np.softmax(attention_weights, axis=-1)

    def forward(self, query, key, value):
        """
        Calculate the output of the Scaled Dot-Product Attention mechanism.

        Args:
            query (np.ndarray): The query matrix.
            key (np.ndarray): The key matrix.
            value (np.ndarray): The value matrix.

        Returns:
            np.ndarray: The output matrix.
        """
        attention_weights = self._calculate_attention_weights(query, key)
        output = np.matmul(attention_weights, value)
        return output


def main():
    # Generate random matrices for Query, Key, and Value
    np.random.seed(0)
    query = np.random.rand(4, 4)
    key = np.random.rand(4, 4)
    value = np.random.rand(4, 4)

    # Initialize the Scaled Dot-Product Attention mechanism
    attention = ScaledDotProductAttention()

    # Calculate the output matrix
    output = attention.forward(query, key, value)

    # Print the output matrix
    print("Query Matrix:")
    print(query)
    print("\nKey Matrix:")
    print(key)
    print("\nValue Matrix:")
    print(value)
    print("\nOutput Matrix:")
    print(output)


if __name__ == "__main__":
    main()
