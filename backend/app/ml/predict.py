"""
Prediction module for Emoji ANN Model.

Handles:
- Loading the trained model
- Preprocessing canvas images (base64 -> tensor)
- Running inference and returning top predictions
"""

import os
import io
import base64
import numpy as np
import torch
from PIL import Image, ImageOps, ImageFilter

from .model import EmojiANN, EMOJI_CLASSES, NUM_CLASSES, INPUT_SIZE


class EmojiPredictor:
    """Loads trained ANN model and provides prediction interface."""

    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), "emoji_model.pth")
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.model_path = model_path
        self.classes = EMOJI_CLASSES
        
        self._load_model()

    def _load_model(self):
        """Load the trained model from disk."""
        if not os.path.exists(self.model_path):
            print(f"[WARN] Model file not found: {self.model_path}")
            print("  Please run train.py first to train the model.")
            return
        
        try:
            checkpoint = torch.load(self.model_path, map_location=self.device, weights_only=False)
            
            self.model = EmojiANN(
                input_size=checkpoint.get('input_size', INPUT_SIZE),
                num_classes=checkpoint.get('num_classes', NUM_CLASSES),
            ).to(self.device)
            
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.eval()
            
            val_acc = checkpoint.get('val_accuracy', 'N/A')
            epoch = checkpoint.get('epoch', 'N/A')
            print(f"[OK] Model loaded (epoch {epoch}, val_acc: {val_acc}%)")
        
        except Exception as e:
            print(f"[FAIL] Error loading model: {e}")
            self.model = None

    def preprocess_image(self, image_data: str) -> torch.Tensor:
        """
        Preprocess a base64 encoded canvas image for model input.
        
        The canvas image is typically white strokes on a black background.
        We need to convert it to 28x28 grayscale and normalize.
        """
        # Decode base64
        if "," in image_data:
            image_data = image_data.split(",")[1]
        
        image_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(image_bytes))
        
        # Convert to grayscale
        img = img.convert('L')
        
        # Invert if needed (canvas usually has white bg, we need white strokes on black)
        img_array = np.array(img)
        
        # Check if the image is predominantly white (white background)
        # If mean > 128, it's white-bg with dark strokes -> invert
        if img_array.mean() > 128:
            img = ImageOps.invert(img)
        
        # Find bounding box of the drawing and crop with padding
        img_array = np.array(img)
        rows = np.any(img_array > 20, axis=1)
        cols = np.any(img_array > 20, axis=0)
        
        if rows.any() and cols.any():
            rmin, rmax = np.where(rows)[0][[0, -1]]
            cmin, cmax = np.where(cols)[0][[0, -1]]
            
            # Add padding
            pad = 4
            rmin = max(0, rmin - pad)
            rmax = min(img_array.shape[0] - 1, rmax + pad)
            cmin = max(0, cmin - pad)
            cmax = min(img_array.shape[1] - 1, cmax + pad)
            
            # Crop tightly
            img_array = img_array[rmin:rmax+1, cmin:cmax+1]
            
            # Make square
            h, w = img_array.shape
            size = max(h, w)
            square = np.zeros((size, size), dtype=np.uint8)
            y_offset = (size - h) // 2
            x_offset = (size - w) // 2
            square[y_offset:y_offset+h, x_offset:x_offset+w] = img_array
            
            img = Image.fromarray(square)
        
        # Resize to 20x20 (Quick Draw standard format)
        img = img.resize((20, 20), Image.LANCZOS)
        
        # Place inside 28x28 black canvas
        final_img = Image.new('L', (28, 28), 0)
        final_img.paste(img, (4, 4))
        
        # Boost brightness to ensure lines are fully white after resize
        arr = np.array(final_img, dtype=np.float32)
        arr = np.clip(arr * 1.5, 0, 255).astype(np.uint8)
        
        # Convert to tensor and normalize
        tensor = torch.FloatTensor(arr.flatten() / 255.0)
        tensor = tensor.unsqueeze(0)  # Add batch dimension
        
        return tensor

    def predict(self, image_data: str, top_k: int = 3):
        """
        Predict emoji from base64 encoded canvas image.
        
        Args:
            image_data: Base64 encoded image string
            top_k: Number of top predictions to return
        
        Returns:
            List of dicts with emoji info and confidence scores
        """
        if self.model is None:
            return [{
                "class_id": -1,
                "name": "error",
                "emoji": "❓",
                "label": "Model not loaded",
                "confidence": 0.0
            }]
        
        # Preprocess
        tensor = self.preprocess_image(image_data).to(self.device)
        
        # Predict
        with torch.no_grad():
            logits = self.model(tensor)
            probabilities = torch.softmax(logits, dim=1)
        
        # Get top-k predictions
        top_probs, top_indices = torch.topk(probabilities, min(top_k, NUM_CLASSES))
        
        results = []
        for prob, idx in zip(top_probs[0], top_indices[0]):
            cls = self.classes[idx.item()]
            results.append({
                "class_id": cls["id"],
                "name": cls["name"],
                "emoji": cls["emoji"],
                "label": cls["label"],
                "confidence": round(prob.item() * 100, 2),
            })
        
        return results

    @property
    def is_ready(self):
        """Check if model is loaded and ready for prediction."""
        return self.model is not None


# Singleton predictor instance
_predictor = None


def get_predictor() -> EmojiPredictor:
    """Get or create the singleton predictor instance."""
    global _predictor
    if _predictor is None:
        _predictor = EmojiPredictor()
    return _predictor
