import torch
import torch.nn as nn
import torch.nn.functional as F

from torch.autograd import Variable

from .linear_block import LinearBlock


class POSEncoder2(nn.Module):
    def __init__(self, embedding_dim, batch_size, pos_tags, evaluate=False):
        """
        Sentence embedding model using dependency parse structure.
        Args:
            embedding_dim (int): dimension of word/phrase/sentence embeddings
            batch_size (int): training batch size (1 until I work out how to parallelise)
            dependency_map (dict): map of dependency labels to index (used for defining params)
            evaluate (bool): Indicator as to whether we want to evaluate embeddings.
        """
        super().__init__()
        self.embedding_dim = embedding_dim
        self.batch_size = batch_size
        self.pos_tags = pos_tags
        self.num_params = max(list(self.pos_tags.values())) + 1
        self.params = nn.ModuleList([nn.Linear(self.embedding_dim, self.embedding_dim) for _ in range(self.num_params)])
        self.evaluate = evaluate

    def recur(self, node):
        x = Variable(torch.tensor([node.embedding], dtype=torch.float), requires_grad=True)
        x = F.relu(self.params[self.pos_tags[node.pos]](x))
        zs = torch.stack([self.recur(c) for c in node.chidren] + [x])
        z, _ = torch.max(zs, 0)

        if self.evaluate:
            # fix
            node.representation = z.detach().numpy()
            node.embedding = x.detach().numpy()

        return z

    def forward(self, input):
        with torch.set_grad_enabled(self.training):
            output = self.recur(input)
            if self.evaluate:
                return input
            return output