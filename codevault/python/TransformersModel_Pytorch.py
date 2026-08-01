# Auto-generated Code Vault for 'TransformersModel (Pytorch)' [Python]

import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class Embeddings(nn.Module):
    def __init__(self, vocab_size, embedding_dim, max_len):
        super(Embeddings, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.positional_encoding = nn.Embedding(max_len, embedding_dim)

    def forward(self, x):
        seq_len = x.size(1)
        pos = torch.arange(seq_len, device=x.device).expand(x.size(0), seq_len)
        return self.embedding(x) + self.positional_encoding(pos)

class PositionalEncoding(nn.Module):
    def __init__(self, embedding_dim, max_len):
        super(PositionalEncoding, self).__init__()
        self.embedding_dim = embedding_dim
        self.max_len = max_len
        self.positional_encoding = self._create_positional_encoding()

    def _create_positional_encoding(self):
        encoding = torch.zeros(self.max_len, self.embedding_dim)
        for pos in range(self.max_len):
            for i in range(0, self.embedding_dim, 2):
                encoding[pos, i] = math.sin(pos / (10000 ** ((2 * i) / self.embedding_dim)))
                if i + 1 < self.embedding_dim:
                    encoding[pos, i + 1] = math.cos(pos / (10000 ** ((2 * (i + 1)) / self.embedding_dim)))
        return encoding

    def forward(self, x):
        seq_len = x.size(1)
        return x + self.positional_encoding[:seq_len, :].unsqueeze(0)

class MultiHeadAttention(nn.Module):
    def __init__(self, embedding_dim, num_heads):
        super(MultiHeadAttention, self).__init__()
        self.embedding_dim = embedding_dim
        self.num_heads = num_heads
        self.query_linear = nn.Linear(embedding_dim, embedding_dim)
        self.key_linear = nn.Linear(embedding_dim, embedding_dim)
        self.value_linear = nn.Linear(embedding_dim, embedding_dim)
        self.dropout = nn.Dropout(0.1)

    def forward(self, query, key, value):
        batch_size = query.size(0)
        seq_len = query.size(1)
        query = self.query_linear(query)
        key = self.key_linear(key)
        value = self.value_linear(value)
        query = query.view(batch_size, seq_len, self.num_heads, -1).transpose(1, 2)
        key = key.view(batch_size, seq_len, self.num_heads, -1).transpose(1, 2)
        value = value.view(batch_size, seq_len, self.num_heads, -1).transpose(1, 2)
        attention_scores = torch.matmul(query, key.transpose(-1, -2)) / math.sqrt(query.size(-1))
        attention_weights = F.softmax(attention_scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        attention_output = torch.matmul(attention_weights, value)
        attention_output = attention_output.transpose(1, 2).contiguous().view(batch_size, seq_len, -1)
        return attention_output

class FeedForwardNetwork(nn.Module):
    def __init__(self, embedding_dim):
        super(FeedForwardNetwork, self).__init__()
        self.linear1 = nn.Linear(embedding_dim, embedding_dim)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.1)
        self.linear2 = nn.Linear(embedding_dim, embedding_dim)

    def forward(self, x):
        x = self.relu(self.linear1(x))
        x = self.dropout(x)
        x = self.linear2(x)
        return x

class TransformerLayer(nn.Module):
    def __init__(self, embedding_dim, num_heads):
        super(TransformerLayer, self).__init__()
        self.self_attention = MultiHeadAttention(embedding_dim, num_heads)
        self.feed_forward_network = FeedForwardNetwork(embedding_dim)
        self.layer_norm1 = nn.LayerNorm(embedding_dim)
        self.layer_norm2 = nn.LayerNorm(embedding_dim)

    def forward(self, x):
        attention_output = self.self_attention(x, x, x)
        attention_output = self.layer_norm1(x + attention_output)
        feed_forward_output = self.feed_forward_network(attention_output)
        feed_forward_output = self.layer_norm2(attention_output + feed_forward_output)
        return feed_forward_output

class TransformersModel(nn.Module):
    def __init__(self, vocab_size, embedding_dim, max_len, num_heads, num_layers):
        super(TransformersModel, self).__init__()
        self.embeddings = Embeddings(vocab_size, embedding_dim, max_len)
        self.positional_encoding = PositionalEncoding(embedding_dim, max_len)
        self.transformer_layers = nn.ModuleList([TransformerLayer(embedding_dim, num_heads) for _ in range(num_layers)])
        self.classifier = nn.Linear(embedding_dim, vocab_size)

    def forward(self, x):
        x = self.embeddings(x)
        x = self.positional_encoding(x)
        for layer in self.transformer_layers:
            x = layer(x)
        x = x.mean(dim=1)
        x = self.classifier(x)
        return x

# Example usage
if __name__ == "__main__":
    vocab_size = 10000
    embedding_dim = 512
    max_len = 100
    num_heads = 8
    num_layers = 6
    batch_size = 32
    seq_len = 50

    model = TransformersModel(vocab_size, embedding_dim, max_len, num_heads, num_layers)
    input_ids = torch.randint(0, vocab_size, (batch_size, seq_len))
    output = model(input_ids)
    print(output.shape)
