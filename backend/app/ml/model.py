"""
Emoji ANN Model - Artificial Neural Network for Emoji Recognition

Architecture: Fully Connected Neural Network (not CNN)
- Input:  784 neurons (28x28 pixel flattened grayscale image)
- Hidden: 512 -> 256 -> 128 neurons with BatchNorm + ReLU + Dropout
- Output: 10 neurons (10 emoji classes)
"""

import torch
import torch.nn as nn


# 10 emoji categories - 6 face + 4 objects
EMOJI_CLASSES = [
    {"id": 0, "name": "happy",    "emoji": "😊", "label": "Happy Face"},
    {"id": 1, "name": "sad",      "emoji": "😢", "label": "Sad Face"},
    {"id": 2, "name": "angry",    "emoji": "😠", "label": "Angry Face"},
    {"id": 3, "name": "surprise", "emoji": "😮", "label": "Surprise Face"},
    {"id": 4, "name": "neutral",  "emoji": "😐", "label": "Neutral Face"},
    {"id": 5, "name": "love",     "emoji": "😍", "label": "Love Face"},
    {"id": 6, "name": "heart",    "emoji": "❤️", "label": "Heart"},
    {"id": 7, "name": "star",     "emoji": "⭐", "label": "Star"},
    {"id": 8, "name": "thumbsup", "emoji": "👍", "label": "Thumbs Up"},
    {"id": 9, "name": "sun",      "emoji": "☀️", "label": "Sun"},
]

NUM_CLASSES = len(EMOJI_CLASSES)
INPUT_SIZE = 784  # 28 x 28


class EmojiANN(nn.Module):
    """
    Fully Connected Artificial Neural Network for emoji classification.
    
    Uses 4 layers with BatchNorm and Dropout for regularization.
    This is a pure ANN (no convolution layers) as required by the assignment.
    """

    def __init__(self, input_size=INPUT_SIZE, num_classes=NUM_CLASSES):
        super(EmojiANN, self).__init__()
        
        self.network = nn.Sequential(
            # Layer 1: Input -> 512
            nn.Linear(input_size, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            # Layer 2: 512 -> 256
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            # Layer 3: 256 -> 128
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            # Output Layer: 128 -> num_classes
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        """Forward pass - expects flattened 784-dim input."""
        return self.network(x)

    def predict_proba(self, x):
        """Get probability distribution over classes."""
        self.eval()
        with torch.no_grad():
            logits = self.forward(x)
            probabilities = torch.softmax(logits, dim=1)
        return probabilities


def get_model_summary():
    """Print model architecture summary."""
    model = EmojiANN()
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print(f"{'='*50}")
    print(f"Emoji ANN Model Summary")
    print(f"{'='*50}")
    print(f"Input size:       {INPUT_SIZE} (28x28 flattened)")
    print(f"Output classes:   {NUM_CLASSES}")
    print(f"Total parameters: {total_params:,}")
    print(f"Trainable params: {trainable_params:,}")
    print(f"{'='*50}")
    print(model)
    return model


if __name__ == "__main__":
    get_model_summary()
