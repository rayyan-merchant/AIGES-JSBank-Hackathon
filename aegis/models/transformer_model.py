try:
    import torch
    import torch.nn as nn
except Exception:
    torch = None
    nn = None

class SimpleTimeSeriesTransformer(nn.Module if nn else object):
    def __init__(self, d_model=16, nhead=2, num_layers=1):
        if nn:
            super().__init__()
            self.embed = nn.Linear(1, d_model)
            encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, batch_first=True)
            self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
            self.fc = nn.Linear(d_model, 1)
        else:
            self.encoder = None
    def forward(self, x):
        if nn:
            h = self.embed(x)
            h = self.encoder(h)
            return self.fc(h[:, -1, :])
        return x[:, -1, :]
