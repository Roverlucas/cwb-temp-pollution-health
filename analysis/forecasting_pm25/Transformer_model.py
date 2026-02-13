import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error

class TransformerRegressor(nn.Module):
    def __init__(self, input_size, d_model=64, nhead=4, num_layers=2):
        super(TransformerRegressor, self).__init__()
        self.input_proj = nn.Linear(input_size, d_model)
        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc = nn.Linear(d_model, 1)

    def forward(self, x):
        x = self.input_proj(x)  # (batch, seq_len, d_model)
        x = self.transformer(x)  # (batch, seq_len, d_model)
        x = self.fc(x[:, -1, :])  # apenas último time step
        return x

def train_transformer_pytorch(X_train, y_train, X_test, y_test,
                              d_model=64, nhead=4, num_layers=2, epochs=100,
                              lr=0.001, batch_size=20):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Normalização
    scaler_x = MinMaxScaler()
    scaler_y = MinMaxScaler()
    X_train_scaled = scaler_x.fit_transform(X_train)
    X_test_scaled = scaler_x.transform(X_test)
    y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1))

    # Reshape para [batch, seq_len, input_size]
    X_train_torch = torch.tensor(X_train_scaled, dtype=torch.float32).unsqueeze(1).to(device)
    y_train_torch = torch.tensor(y_train_scaled, dtype=torch.float32).to(device)
    X_test_torch = torch.tensor(X_test_scaled, dtype=torch.float32).unsqueeze(1).to(device)

    # Dataset e DataLoader
    train_dataset = torch.utils.data.TensorDataset(X_train_torch, y_train_torch)
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    # Modelo
    model = TransformerRegressor(input_size=X_train.shape[1],
                                 d_model=d_model, nhead=nhead, num_layers=num_layers).to(device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    # Treinamento
    model.train()
    for epoch in range(epochs):
        for xb, yb in train_loader:
            yb = yb.view(-1, 1)
            optimizer.zero_grad()
            out = model(xb)
            loss = criterion(out, yb)
            loss.backward()
            optimizer.step()

    # Previsão
    model.eval()
    with torch.no_grad():
        y_pred_scaled = model(X_test_torch).cpu().numpy()

    y_pred = scaler_y.inverse_transform(y_pred_scaled)
    return y_pred.flatten()