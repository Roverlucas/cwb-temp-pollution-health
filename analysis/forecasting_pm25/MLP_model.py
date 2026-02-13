import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

class MLP_model:
    def __init__(self, hidden_layer_sizes, activation='tanh', max_iter=1000, lr=0.01, batch_size=20, device=None):
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.max_iter = max_iter
        self.batch_size = batch_size
        self.lr = lr
    
        self.hidden_layer_sizes = hidden_layer_sizes
        self.activation = activation
        
        self.model = None
        self.is_fitted = False

    def _build_model(self, input_dim):
        layers = []
        prev_size = input_dim
        
        act_fn = {
            'tanh': nn.Tanh(),
            'relu': nn.ReLU(),
            'sigmoid': nn.Sigmoid()
        }.get(self.activation, nn.Sigmoid())
        
        for h in self.hidden_layer_sizes:
            layers.append(nn.Linear(prev_size, h))
            layers.append(act_fn)
            prev_size = h
        
        layers.append(nn.Linear(prev_size, 1))  
        
        model = nn.Sequential(*layers)
        return model.to(self.device)

    def fit(self, X_train, y_train):
        X_train = torch.tensor(X_train, dtype=torch.float32).to(self.device)
        y_train = torch.tensor(y_train, dtype=torch.float32).view(-1, 1).to(self.device)
        
        if self.model is None:
            input_dim = X_train.shape[1]
            self.model = self._build_model(input_dim)
        
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=5, factor=0.5)

        dataset = torch.utils.data.TensorDataset(X_train, y_train)
        loader = torch.utils.data.DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        self.model.train()
        best_loss = float('inf')
        patience_counter = 0
        early_stopping_patience = 10  # pode ajustar o valor
        
        for epoch in range(self.max_iter):
            epoch_loss = 0.0
            for xb, yb in loader:
                optimizer.zero_grad()
                outputs = self.model(xb)
                loss = criterion(outputs, yb)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item() * xb.size(0)
            
            epoch_loss /= len(loader.dataset)
            scheduler.step(epoch_loss)
            
            #print(f"Epoch {epoch+1}/{self.max_iter}, Loss: {epoch_loss:.6f}")
            
            # Early stopping
            if epoch_loss < best_loss:
                best_loss = epoch_loss
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= early_stopping_patience:
                    #print(f"Early stopping ativado após {epoch+1} épocas.")
                    break

        self.is_fitted = True

    def predict(self, X_test):
        if not self.is_fitted:
            raise Exception("Modelo não treinado. Use fit() antes de predict().")
        
        self.model.eval()
        X_test = torch.tensor(X_test, dtype=torch.float32).to(self.device)
        with torch.no_grad():
            preds = self.model(X_test).cpu().numpy()
        
        return preds.flatten()
