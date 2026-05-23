import torch
from app.ml.predict import EmojiPredictor
import numpy as np
from PIL import Image, ImageDraw
import base64
import io

predictor = EmojiPredictor()

# Try with a thicker line
img = Image.new('RGB', (420, 420), color='black')
draw = ImageDraw.Draw(img)
# Draw a smiley face
draw.ellipse([50, 50, 370, 370], outline='white', width=24) # Face
draw.ellipse([130, 130, 180, 180], fill='white') # Left eye
draw.ellipse([240, 130, 290, 180], fill='white') # Right eye
# Smile
draw.arc([130, 200, 290, 320], start=0, end=180, fill='white', width=24)

buffer = io.BytesIO()
img.save(buffer, format='PNG')
b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

tensor = predictor.preprocess_image(b64)
arr = tensor.numpy().reshape(28, 28)

print("ASCII art for drawn smiley with width 24:")
for row in arr:
    line = "".join(["#" if p > 0.5 else "." for p in row])
    print(line)

with torch.no_grad():
    out = predictor.model(tensor.to(predictor.device))
    probs = torch.softmax(out, dim=1)
    print(f"Prediction: {probs.max().item():.4f} at index {probs.argmax().item()} (Class: {predictor.classes[probs.argmax().item()]['name']})")
