import torch
import torch.nn as nn
import torch.nn.functional as F

from torch.autograd import Variable

from .linear_block import LinearBlock


class PoolingPredictor(nn.Module):
    def __init__(self, layers, drops, pool_type):
        super().__init__()
        self.layers = nn.ModuleList([LinearBlock(layers[i], layers[i+1], drops[i]) for i in range(len(layers) - 1)])
        self.pool_type = pool_type
    
    def forward(self, input1, input2):
        s1 = Variable(torch.tensor(input1, dtype=torch.float), requires_grad=True)
        s2 = Variable(torch.tensor(input2, dtype=torch.float), requires_grad=True)
        
        if self.pool_type == "max":
            x1, _ = torch.max(s1, 0)
            x2, _ = torch.max(s2, 0)
        elif self.pool_type == "avg":
            x1 = torch.mean(s1, 0)
            x2 = torch.mean(s2, 0)
        else:
            print("um, that's an invalid pooling type")
        
        diff = (x1-x2).abs()
        mult = x1 * x2
        x = torch.cat((diff, mult), 0).view(1, -1)
        for l in self.layers:
            l_x = l(x)
            x = F.relu(l_x)
        
        return l_x
