import numpy as np
import os
import sys
import torch
from app.ml.model import EmojiANN

model = EmojiANN()
checkpoint = torch.load('app/ml/emoji_model.pth', map_location='cpu', weights_only=False)
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

files = ['app/ml/data/star.npy', 'app/ml/data/happy.npy']
for f in files:
    if os.path.exists(f):
        data = np.load(f)
        print(f'{f} shape: {data.shape}, min: {data.min()}, max: {data.max()}, mean: {data.mean()}')
        
        sample = data[0].astype(np.float32) / 255.0
        tensor = torch.FloatTensor(sample).unsqueeze(0)
        with torch.no_grad():
            out = model(tensor)
            probs = torch.softmax(out, dim=1)
            print(f'Prediction for first sample of {f}: max prob {probs.max().item():.4f} at index {probs.argmax().item()}')
