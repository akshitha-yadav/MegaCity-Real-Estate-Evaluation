import torch
import torch.nn as nn
import torch.nn.functional as F

class GCN(nn.Module):
    def __init__(self, in_features):
        super(GCN, self).__init__()
        self.fc1 = nn.Linear(in_features, 16)
        self.fc2 = nn.Linear(16, 1)

    def forward(self, x, adj):
        x = torch.matmul(adj, x)
        x = F.relu(self.fc1(x))
        x = torch.matmul(adj, x)
        x = self.fc2(x)
        return x