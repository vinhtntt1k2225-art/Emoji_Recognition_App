"""
Training script for Emoji ANN Model.

Steps:
1. Generate synthetic face emoji data (6 classes)
2. Download Quick Draw data (4 classes)
3. Combine, shuffle, split into train/val
4. Train the ANN model
5. Save the trained model
"""

import os
import sys
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.model import EmojiANN, NUM_CLASSES, EMOJI_CLASSES
from ml.generate_faces import generate_face_dataset
from ml.download_data import download_quickdraw_data


def prepare_dataset(samples_per_class=10000):
    """Prepare combined dataset from synthetic + Quick Draw data."""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    
    print("=" * 60)
    print("STEP 1: Generate synthetic face emoji data")
    print("=" * 60)
    face_data, face_labels = generate_face_dataset(
        samples_per_class=samples_per_class,
        output_dir=data_dir
    )
    
    print("\n" + "=" * 60)
    print("STEP 2: Download Quick Draw data")
    print("=" * 60)
    qd_data, qd_labels = download_quickdraw_data(
        samples_per_class=samples_per_class,
        output_dir=data_dir
    )
    
    # Combine
    print("\n" + "=" * 60)
    print("STEP 3: Combine and prepare dataset")
    print("=" * 60)
    
    all_data = np.concatenate([face_data, qd_data], axis=0).astype(np.float32)
    all_labels = np.concatenate([face_labels, qd_labels], axis=0)
    
    # Normalize pixel values to [0, 1]
    all_data = all_data / 255.0
    
    # Shuffle
    indices = np.random.permutation(len(all_data))
    all_data = all_data[indices]
    all_labels = all_labels[indices]
    
    # Split train/val (80/20)
    split_idx = int(len(all_data) * 0.8)
    train_data = all_data[:split_idx]
    train_labels = all_labels[:split_idx]
    val_data = all_data[split_idx:]
    val_labels = all_labels[split_idx:]
    
    print(f"  Total samples: {len(all_data)}")
    print(f"  Train samples: {len(train_data)}")
    print(f"  Val samples:   {len(val_data)}")
    
    # Class distribution
    print(f"\n  Class distribution (train):")
    for cls in EMOJI_CLASSES:
        count = np.sum(train_labels == cls["id"])
        print(f"    [{cls['id']}] {cls['label']}: {count}")
    
    return train_data, train_labels, val_data, val_labels


def train_model(
    samples_per_class=10000,
    epochs=30,
    batch_size=128,
    learning_rate=0.001,
    patience=5,
):
    """Train the Emoji ANN model."""
    
    # Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\nUsing device: {device}")
    
    # Prepare data
    train_data, train_labels, val_data, val_labels = prepare_dataset(samples_per_class)
    
    # Create DataLoaders
    train_dataset = TensorDataset(
        torch.FloatTensor(train_data),
        torch.LongTensor(train_labels)
    )
    val_dataset = TensorDataset(
        torch.FloatTensor(val_data),
        torch.LongTensor(val_labels)
    )
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # Model
    model = EmojiANN(num_classes=NUM_CLASSES).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=3, factor=0.5)
    
    # Training loop
    print("\n" + "=" * 60)
    print("STEP 4: Training ANN Model")
    print("=" * 60)
    
    best_val_acc = 0.0
    patience_counter = 0
    model_path = os.path.join(os.path.dirname(__file__), "emoji_model.pth")
    
    for epoch in range(epochs):
        # Train
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for batch_data, batch_labels in train_loader:
            batch_data = batch_data.to(device)
            batch_labels = batch_labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(batch_data)
            loss = criterion(outputs, batch_labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = outputs.max(1)
            train_total += batch_labels.size(0)
            train_correct += predicted.eq(batch_labels).sum().item()
        
        train_acc = 100.0 * train_correct / train_total
        avg_train_loss = train_loss / len(train_loader)
        
        # Validate
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for batch_data, batch_labels in val_loader:
                batch_data = batch_data.to(device)
                batch_labels = batch_labels.to(device)
                
                outputs = model(batch_data)
                loss = criterion(outputs, batch_labels)
                
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                val_total += batch_labels.size(0)
                val_correct += predicted.eq(batch_labels).sum().item()
        
        val_acc = 100.0 * val_correct / val_total
        avg_val_loss = val_loss / len(val_loader)
        
        scheduler.step(avg_val_loss)
        
        current_lr = optimizer.param_groups[0]['lr']
        print(f"  Epoch [{epoch+1:2d}/{epochs}] "
              f"Train Loss: {avg_train_loss:.4f} | Train Acc: {train_acc:.2f}% | "
              f"Val Loss: {avg_val_loss:.4f} | Val Acc: {val_acc:.2f}% | "
              f"LR: {current_lr:.6f}")
        
        # Early stopping
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            
            # Save best model
            torch.save({
                'model_state_dict': model.state_dict(),
                'num_classes': NUM_CLASSES,
                'input_size': 784,
                'val_accuracy': val_acc,
                'epoch': epoch + 1,
                'classes': EMOJI_CLASSES,
            }, model_path)
            print(f"    -> Best model saved! (Val Acc: {val_acc:.2f}%)")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"\n  Early stopping at epoch {epoch+1} (no improvement for {patience} epochs)")
                break
    
    print(f"\n{'='*60}")
    print(f"Training Complete!")
    print(f"{'='*60}")
    print(f"  Best Validation Accuracy: {best_val_acc:.2f}%")
    print(f"  Model saved to: {model_path}")
    
    return model, best_val_acc


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train Emoji ANN Model")
    parser.add_argument("--samples", type=int, default=10000,
                        help="Samples per class (default: 10000)")
    parser.add_argument("--epochs", type=int, default=30,
                        help="Number of training epochs (default: 30)")
    parser.add_argument("--batch-size", type=int, default=128,
                        help="Batch size (default: 128)")
    parser.add_argument("--lr", type=float, default=0.001,
                        help="Learning rate (default: 0.001)")
    
    args = parser.parse_args()
    
    train_model(
        samples_per_class=args.samples,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
    )
