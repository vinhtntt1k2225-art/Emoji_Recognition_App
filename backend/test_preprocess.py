import torch
from app.ml.predict import EmojiPredictor
import numpy as np
from PIL import Image, ImageDraw
import base64
import io

predictor = EmojiPredictor()

# Create a mock canvas image (black background, white line)
img = Image.new('RGB', (420, 420), color='black')
draw = ImageDraw.Draw(img)
draw.line((100, 100, 300, 300), fill='white', width=8)

# Convert to base64
buffer = io.BytesIO()
img.save(buffer, format='PNG')
b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

# Preprocess
tensor = predictor.preprocess_image(b64)
arr = tensor.numpy().reshape(28, 28)

print(f"Tensor shape: {tensor.shape}, min: {tensor.min().item()}, max: {tensor.max().item()}, mean: {tensor.mean().item()}")
print("ASCII art:")
for row in arr:
    line = "".join(["#" if p > 0.5 else "." for p in row])
    print(line)

# Predict
with torch.no_grad():
    out = predictor.model(tensor.to(predictor.device))
    probs = torch.softmax(out, dim=1)
    print(f"Prediction: {probs.max().item():.4f} at index {probs.argmax().item()} (Class: {predictor.classes[probs.argmax().item()]['name']})")
