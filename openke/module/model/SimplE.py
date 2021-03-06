import torch
import torch.nn as nn

from .Model import Model

from configs import Config


class SimplE(Model):
    def __init__(self, ent_tot, rel_tot):
        super(SimplE, self).__init__(ent_tot, rel_tot)

        self.dim = Config.embedding_dim
        self.ent_embeddings = nn.Embedding(self.ent_tot, self.dim)
        self.rel_embeddings = nn.Embedding(self.rel_tot, self.dim)
        self.rel_inv_embeddings = nn.Embedding(self.rel_tot, self.dim)

        nn.init.xavier_uniform_(self.ent_embeddings.weight.data)
        nn.init.xavier_uniform_(self.rel_embeddings.weight.data)
        nn.init.xavier_uniform_(self.rel_inv_embeddings.weight.data)

    @staticmethod
    def _calc_avg(h, t, r, r_inv):
        return (torch.sum(h * r * t, -1) + torch.sum(h * r_inv * t, -1))/2

    @staticmethod
    def _calc_ingr(h, r, t):
        return torch.sum(h * r * t, -1)

    def forward(self, data):
        batch_h = data['batch_h']
        batch_t = data['batch_t']
        batch_r = data['batch_r']
        h = self.ent_embeddings(batch_h)
        t = self.ent_embeddings(batch_t)
        r = self.rel_embeddings(batch_r)
        r_inv = self.rel_inv_embeddings(batch_r)
        score = self._calc_avg(h, t, r, r_inv)
        return score

    def regularization(self, data):
        batch_h = data['batch_h']
        batch_t = data['batch_t']
        batch_r = data['batch_r']
        h = self.ent_embeddings(batch_h)
        t = self.ent_embeddings(batch_t)
        r = self.rel_embeddings(batch_r)
        r_inv = self.rel_inv_embeddings(batch_r)
        regul = (torch.mean(h ** 2) + torch.mean(t ** 2) + torch.mean(r ** 2) + torch.mean(r_inv ** 2)) / 4
        return regul

    def predict(self, data):
        batch_h = data['batch_h']
        batch_t = data['batch_t']
        batch_r = data['batch_r']
        h = self.ent_embeddings(batch_h)
        t = self.ent_embeddings(batch_t)
        r = self.rel_embeddings(batch_r)
        score = -self._calc_ingr(h, r, t)
        return score.cpu().data.numpy()
