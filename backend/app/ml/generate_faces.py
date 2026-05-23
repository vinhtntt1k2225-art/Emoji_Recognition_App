"""
Synthetic Face Emoji Data Generator

Generates 28x28 grayscale images of face emojis with random variations.
6 face categories: happy, sad, angry, surprise, neutral, love

Each face is a circle with different eye/mouth/eyebrow configurations.
Variations include: position offset, size, rotation, noise, stroke width.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import random
import os


def _random_offset(base, max_offset=2):
    """Add random offset to a coordinate."""
    return base + random.randint(-max_offset, max_offset)


def _draw_circle_face(draw, cx, cy, radius, width=1):
    """Draw the base circle face outline."""
    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        outline=255, width=width
    )


def _draw_dot_eyes(draw, cx, cy, radius, eye_size=1):
    """Draw simple dot eyes."""
    eye_y = cy - radius * 0.25
    left_x = cx - radius * 0.35
    right_x = cx + radius * 0.35
    
    left_x = _random_offset(left_x, 1)
    right_x = _random_offset(right_x, 1)
    eye_y_l = _random_offset(eye_y, 1)
    eye_y_r = _random_offset(eye_y, 1)
    
    draw.ellipse([left_x - eye_size, eye_y_l - eye_size, 
                  left_x + eye_size, eye_y_l + eye_size], fill=255)
    draw.ellipse([right_x - eye_size, eye_y_r - eye_size,
                  right_x + eye_size, eye_y_r + eye_size], fill=255)


def _draw_round_eyes(draw, cx, cy, radius, eye_radius=2):
    """Draw round open eyes (for surprise)."""
    eye_y = cy - radius * 0.25
    left_x = cx - radius * 0.35
    right_x = cx + radius * 0.35
    
    left_x = _random_offset(left_x, 1)
    right_x = _random_offset(right_x, 1)
    eye_y = _random_offset(eye_y, 1)
    
    draw.ellipse([left_x - eye_radius, eye_y - eye_radius,
                  left_x + eye_radius, eye_y + eye_radius], outline=255, width=1)
    draw.ellipse([right_x - eye_radius, eye_y - eye_radius,
                  right_x + eye_radius, eye_y + eye_radius], outline=255, width=1)


def _draw_heart_eyes(draw, cx, cy, radius):
    """Draw heart-shaped eyes (for love face)."""
    eye_y = cy - radius * 0.25
    left_x = cx - radius * 0.35
    right_x = cx + radius * 0.35
    
    for ex in [left_x, right_x]:
        ex = _random_offset(ex, 1)
        ey = _random_offset(eye_y, 1)
        s = 2  # heart size
        # Simple heart using two small circles and a triangle
        draw.ellipse([ex - s, ey - s, ex, ey], fill=255)
        draw.ellipse([ex, ey - s, ex + s, ey], fill=255)
        draw.polygon([(ex - s, ey - 0.5), (ex, ey + s), (ex + s, ey - 0.5)], fill=255)


def _draw_smile_mouth(draw, cx, cy, radius, width=1):
    """Draw a smiling mouth (arc curving up)."""
    mouth_y = cy + radius * 0.2
    mouth_w = radius * 0.5
    
    mouth_y = _random_offset(mouth_y, 1)
    
    draw.arc(
        [cx - mouth_w, mouth_y - mouth_w * 0.5,
         cx + mouth_w, mouth_y + mouth_w * 0.8],
        start=0, end=180, fill=255, width=width
    )


def _draw_frown_mouth(draw, cx, cy, radius, width=1):
    """Draw a frowning mouth (arc curving down)."""
    mouth_y = cy + radius * 0.35
    mouth_w = radius * 0.45
    
    mouth_y = _random_offset(mouth_y, 1)
    
    draw.arc(
        [cx - mouth_w, mouth_y - mouth_w * 0.5,
         cx + mouth_w, mouth_y + mouth_w * 0.8],
        start=180, end=360, fill=255, width=width
    )


def _draw_o_mouth(draw, cx, cy, radius, width=1):
    """Draw an O-shaped mouth (for surprise)."""
    mouth_y = cy + radius * 0.3
    mouth_r = radius * 0.2
    
    mouth_y = _random_offset(mouth_y, 1)
    
    draw.ellipse(
        [cx - mouth_r, mouth_y - mouth_r,
         cx + mouth_r, mouth_y + mouth_r],
        outline=255, width=width
    )


def _draw_straight_mouth(draw, cx, cy, radius, width=1):
    """Draw a straight line mouth (for neutral)."""
    mouth_y = cy + radius * 0.3
    mouth_w = radius * 0.35
    
    mouth_y = _random_offset(mouth_y, 1)
    
    draw.line(
        [cx - mouth_w, mouth_y, cx + mouth_w, mouth_y],
        fill=255, width=width
    )


def _draw_angry_brows(draw, cx, cy, radius, width=1):
    """Draw angry angled eyebrows."""
    brow_y = cy - radius * 0.45
    left_x = cx - radius * 0.45
    right_x = cx + radius * 0.45
    
    brow_y = _random_offset(brow_y, 1)
    
    # Left brow: angled down toward center
    draw.line([left_x, brow_y - 1, cx - radius * 0.15, brow_y + 2],
              fill=255, width=width)
    # Right brow: angled down toward center
    draw.line([right_x, brow_y - 1, cx + radius * 0.15, brow_y + 2],
              fill=255, width=width)


def _draw_teardrop(draw, cx, cy, radius):
    """Draw a teardrop (for sad face)."""
    tear_x = cx + radius * 0.45
    tear_y = cy - radius * 0.1
    
    tear_x = _random_offset(tear_x, 1)
    
    draw.line([tear_x, tear_y, tear_x, tear_y + 3], fill=255, width=1)
    draw.ellipse([tear_x - 1, tear_y + 2, tear_x + 1, tear_y + 4], fill=255)


def generate_happy_face(img_size=28):
    """Generate a happy face emoji: dot eyes + smile mouth."""
    img = Image.new('L', (img_size, img_size), 0)
    draw = ImageDraw.Draw(img)
    
    cx, cy = img_size // 2, img_size // 2
    cx = _random_offset(cx, 1)
    cy = _random_offset(cy, 1)
    radius = random.randint(8, 11)
    width = random.choice([1, 2, 3])
    
    _draw_circle_face(draw, cx, cy, radius, width)
    _draw_dot_eyes(draw, cx, cy, radius)
    _draw_smile_mouth(draw, cx, cy, radius, width)
    
    return img


def generate_sad_face(img_size=28):
    """Generate a sad face emoji: dot eyes + frown mouth + teardrop."""
    img = Image.new('L', (img_size, img_size), 0)
    draw = ImageDraw.Draw(img)
    
    cx, cy = img_size // 2, img_size // 2
    cx = _random_offset(cx, 1)
    cy = _random_offset(cy, 1)
    radius = random.randint(8, 11)
    width = random.choice([1, 2, 3])
    
    _draw_circle_face(draw, cx, cy, radius, width)
    _draw_dot_eyes(draw, cx, cy, radius)
    _draw_frown_mouth(draw, cx, cy, radius, width)
    
    # Add teardrop sometimes
    if random.random() > 0.3:
        _draw_teardrop(draw, cx, cy, radius)
    
    return img


def generate_angry_face(img_size=28):
    """Generate an angry face emoji: angry brows + frown mouth."""
    img = Image.new('L', (img_size, img_size), 0)
    draw = ImageDraw.Draw(img)
    
    cx, cy = img_size // 2, img_size // 2
    cx = _random_offset(cx, 1)
    cy = _random_offset(cy, 1)
    radius = random.randint(8, 11)
    width = random.choice([1, 2, 3])
    
    _draw_circle_face(draw, cx, cy, radius, width)
    _draw_dot_eyes(draw, cx, cy, radius)
    _draw_angry_brows(draw, cx, cy, radius, width)
    _draw_frown_mouth(draw, cx, cy, radius, width)
    
    return img


def generate_surprise_face(img_size=28):
    """Generate a surprise face emoji: round eyes + O mouth."""
    img = Image.new('L', (img_size, img_size), 0)
    draw = ImageDraw.Draw(img)
    
    cx, cy = img_size // 2, img_size // 2
    cx = _random_offset(cx, 1)
    cy = _random_offset(cy, 1)
    radius = random.randint(8, 11)
    width = random.choice([1, 2, 3])
    
    _draw_circle_face(draw, cx, cy, radius, width)
    _draw_round_eyes(draw, cx, cy, radius)
    _draw_o_mouth(draw, cx, cy, radius, width)
    
    return img


def generate_neutral_face(img_size=28):
    """Generate a neutral face emoji: dot eyes + straight mouth."""
    img = Image.new('L', (img_size, img_size), 0)
    draw = ImageDraw.Draw(img)
    
    cx, cy = img_size // 2, img_size // 2
    cx = _random_offset(cx, 1)
    cy = _random_offset(cy, 1)
    radius = random.randint(8, 11)
    width = random.choice([1, 2, 3])
    
    _draw_circle_face(draw, cx, cy, radius, width)
    _draw_dot_eyes(draw, cx, cy, radius)
    _draw_straight_mouth(draw, cx, cy, radius, width)
    
    return img


def generate_love_face(img_size=28):
    """Generate a love face emoji: heart eyes + smile mouth."""
    img = Image.new('L', (img_size, img_size), 0)
    draw = ImageDraw.Draw(img)
    
    cx, cy = img_size // 2, img_size // 2
    cx = _random_offset(cx, 1)
    cy = _random_offset(cy, 1)
    radius = random.randint(8, 11)
    width = random.choice([1, 2, 3])
    
    _draw_circle_face(draw, cx, cy, radius, width)
    _draw_heart_eyes(draw, cx, cy, radius)
    _draw_smile_mouth(draw, cx, cy, radius, width)
    
    return img


# Map class IDs to generator functions
FACE_GENERATORS = {
    0: generate_happy_face,
    1: generate_sad_face,
    2: generate_angry_face,
    3: generate_surprise_face,
    4: generate_neutral_face,
    5: generate_love_face,
}

FACE_NAMES = {
    0: "happy",
    1: "sad",
    2: "angry",
    3: "surprise",
    4: "neutral",
    5: "love",
}


def apply_augmentation(img):
    """Apply random augmentation to an image."""
    # Random rotation
    if random.random() > 0.3:
        angle = random.uniform(-15, 15)
        img = img.rotate(angle, fillcolor=0)
    
    # Random slight blur (simulates hand-drawn style)
    if random.random() > 0.6:
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    # Add noise
    if random.random() > 0.4:
        arr = np.array(img, dtype=np.float32)
        noise = np.random.normal(0, random.uniform(5, 15), arr.shape)
        arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(arr)
    
    return img


def generate_face_dataset(samples_per_class=10000, img_size=28, output_dir=None):
    """
    Generate synthetic face emoji dataset.
    
    Returns:
        data: numpy array of shape (total_samples, 784)
        labels: numpy array of shape (total_samples,)
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "data")
    
    os.makedirs(output_dir, exist_ok=True)
    
    all_data = []
    all_labels = []
    
    for class_id, generator in FACE_GENERATORS.items():
        name = FACE_NAMES[class_id]
        print(f"  Generating {samples_per_class} samples for '{name}' (class {class_id})...")
        
        class_data = []
        for i in range(samples_per_class):
            img = generator(img_size)
            img = apply_augmentation(img)
            
            # Convert to numpy array and flatten
            arr = np.array(img, dtype=np.uint8).flatten()
            class_data.append(arr)
        
        class_data = np.array(class_data)
        class_labels = np.full(samples_per_class, class_id, dtype=np.int64)
        
        # Save individual class file
        np.save(os.path.join(output_dir, f"{name}.npy"), class_data)
        
        all_data.append(class_data)
        all_labels.append(class_labels)
        
        print(f"    [OK] Saved {name}.npy ({class_data.shape})")
    
    data = np.concatenate(all_data, axis=0)
    labels = np.concatenate(all_labels, axis=0)
    
    print(f"\n  Total synthetic face data: {data.shape[0]} samples")
    return data, labels


if __name__ == "__main__":
    print("Generating synthetic face emoji dataset...")
    data, labels = generate_face_dataset(samples_per_class=100)  # Small test
    print(f"Data shape: {data.shape}, Labels shape: {labels.shape}")
    
    # Save a few samples as PNG for visual inspection
    output_dir = os.path.join(os.path.dirname(__file__), "data", "samples")
    os.makedirs(output_dir, exist_ok=True)
    
    for class_id in range(6):
        idx = np.where(labels == class_id)[0][:5]
        for i, sample_idx in enumerate(idx):
            img = Image.fromarray(data[sample_idx].reshape(28, 28))
            img = img.resize((112, 112), Image.NEAREST)
            img.save(os.path.join(output_dir, f"{FACE_NAMES[class_id]}_{i}.png"))
    
    print(f"Sample images saved to {output_dir}")
