"""
Download Quick Draw dataset (.npy format) for non-face emoji categories.
- Star, Sun: downloaded from Google Quick Draw
- Heart, Thumbs Up: generated synthetically (not available in Quick Draw)
"""

import os
import math
import random
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFilter


# Quick Draw categories that actually exist (mapped to class IDs)
QUICKDRAW_CATEGORIES = {
    7: "star",
    9: "sun",
}

# Synthetic categories (not in Quick Draw)
SYNTHETIC_CATEGORIES = {
    6: "heart",
    8: "thumbs up",
}

BASE_URL = "https://storage.googleapis.com/quickdraw_dataset/full/numpy_bitmap"


# ============================================================
# Synthetic shape generators
# ============================================================

def _random_offset(base, max_offset=2):
    return base + random.randint(-max_offset, max_offset)


def generate_heart_image(img_size=28):
    """Generate a heart shape using parametric curves."""
    img = Image.new('L', (img_size, img_size), 0)
    draw = ImageDraw.Draw(img)

    cx = img_size // 2 + random.randint(-1, 1)
    cy = img_size // 2 + random.randint(-1, 1)
    scale = random.uniform(0.32, 0.42) * img_size
    width = random.choice([1, 1, 2])

    # Heart shape using parametric equation
    points = []
    for t_deg in range(0, 360, 5):
        t = math.radians(t_deg)
        x = scale * 0.9 * (16 * math.sin(t) ** 3) / 16
        y = -scale * 0.85 * (13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)) / 16
        points.append((cx + x, cy + y + scale * 0.1))

    # Draw outline
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=255, width=width)
    draw.line([points[-1], points[0]], fill=255, width=width)

    # Random fill sometimes
    if random.random() > 0.4:
        # Fill by flood-filling from center
        try:
            from PIL import ImageDraw as ID2
            # Simple fill: draw filled polygon
            draw.polygon(points, fill=255, outline=255)
        except:
            pass

    return img


def generate_thumbsup_image(img_size=28):
    """Generate a thumbs-up shape."""
    img = Image.new('L', (img_size, img_size), 0)
    draw = ImageDraw.Draw(img)

    cx = img_size // 2 + random.randint(-1, 1)
    cy = img_size // 2 + random.randint(-1, 1)
    width = random.choice([1, 1, 2])
    s = random.uniform(0.8, 1.1)  # scale factor

    # Thumb (vertical rectangle/oval going up)
    thumb_w = int(3 * s)
    thumb_h = int(8 * s)
    thumb_x = cx - 1
    thumb_top = cy - thumb_h
    draw.rounded_rectangle(
        [thumb_x - thumb_w, thumb_top, thumb_x + thumb_w, cy - int(1 * s)],
        radius=int(2 * s), outline=255, fill=255 if random.random() > 0.5 else 0, width=width
    )

    # Fist/palm (wider rectangle below)
    fist_w = int(6 * s)
    fist_h = int(5 * s)
    fist_top = cy - int(1 * s)
    draw.rounded_rectangle(
        [cx - fist_w, fist_top, cx + fist_w - int(2 * s), fist_top + fist_h],
        radius=int(2 * s), outline=255, fill=255 if random.random() > 0.5 else 0, width=width
    )

    # Finger lines on fist
    if random.random() > 0.3:
        for i in range(2, 4):
            ly = fist_top + int(i * s * 1.3)
            draw.line(
                [cx - fist_w + int(2*s), ly, cx + fist_w - int(4*s), ly],
                fill=180, width=1
            )

    return img


def apply_shape_augmentation(img):
    """Apply random augmentation to shape images."""
    # Random rotation
    if random.random() > 0.3:
        angle = random.uniform(-15, 15)
        img = img.rotate(angle, fillcolor=0)

    # Slight blur
    if random.random() > 0.5:
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))

    # Add noise
    if random.random() > 0.4:
        arr = np.array(img, dtype=np.float32)
        noise = np.random.normal(0, random.uniform(5, 15), arr.shape)
        arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(arr)

    return img


def generate_synthetic_category(category, samples_per_class, output_dir):
    """Generate synthetic data for a category not in Quick Draw."""
    generators = {
        "heart": generate_heart_image,
        "thumbs up": generate_thumbsup_image,
    }

    generator = generators[category]
    print(f"  Generating {samples_per_class} synthetic samples for '{category}'...")

    class_data = []
    for _ in range(samples_per_class):
        img = generator(28)
        img = apply_shape_augmentation(img)
        arr = np.array(img, dtype=np.uint8).flatten()
        class_data.append(arr)

    class_data = np.array(class_data)
    filepath = os.path.join(output_dir, f"{category}.npy")
    np.save(filepath, class_data)
    print(f"    [OK] Generated {category}.npy ({class_data.shape})")

    return class_data


def download_quickdraw_data(samples_per_class=10000, output_dir=None):
    """
    Get data for non-face emoji categories.
    Star & Sun from Quick Draw, Heart & Thumbs Up generated synthetically.

    Returns:
        data: numpy array of shape (total_samples, 784)
        labels: numpy array of shape (total_samples,)
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "data")

    os.makedirs(output_dir, exist_ok=True)

    all_data = []
    all_labels = []

    # Combine both category dicts
    all_categories = {}
    all_categories.update(QUICKDRAW_CATEGORIES)
    all_categories.update(SYNTHETIC_CATEGORIES)

    for class_id in sorted(all_categories.keys()):
        category = all_categories[class_id]

        if class_id in SYNTHETIC_CATEGORIES:
            # Generate synthetic data
            filepath = os.path.join(output_dir, f"{category}.npy")

            # Check if valid synthetic data already exists
            needs_regen = True
            if os.path.exists(filepath):
                try:
                    existing = np.load(filepath)
                    # If file is tiny (fallback random data), regenerate
                    if existing.shape[0] >= samples_per_class and existing.mean() > 10:
                        needs_regen = False
                        print(f"  '{category}' synthetic data exists, reusing...")
                except:
                    pass

            if needs_regen:
                generate_synthetic_category(category, samples_per_class, output_dir)

            raw_data = np.load(os.path.join(output_dir, f"{category}.npy"))

        else:
            # Download from Quick Draw
            filename = f"{category}.npy"
            filepath = os.path.join(output_dir, filename)
            url = f"{BASE_URL}/{requests.utils.quote(category)}.npy"

            if not os.path.exists(filepath):
                print(f"  Downloading '{category}' from Quick Draw...")
                try:
                    response = requests.get(url, stream=True, timeout=120)
                    response.raise_for_status()

                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    print(f"    [OK] Downloaded {filename}")
                except Exception as e:
                    print(f"    [FAIL] Failed to download {category}: {e}")
                    print(f"    -> Generating fallback synthetic data")
                    # Generate simple fallback
                    fallback = np.random.randint(0, 50, (samples_per_class, 784), dtype=np.uint8)
                    np.save(filepath, fallback)
            else:
                print(f"  '{category}' already downloaded, skipping...")

            raw_data = np.load(filepath)

        # Sample data
        if len(raw_data) > samples_per_class:
            indices = np.random.choice(len(raw_data), samples_per_class, replace=False)
            class_data = raw_data[indices]
        else:
            class_data = raw_data[:samples_per_class]

        class_labels = np.full(len(class_data), class_id, dtype=np.int64)

        all_data.append(class_data)
        all_labels.append(class_labels)

        print(f"    Using {len(class_data)} samples for '{category}' (class {class_id})")

    data = np.concatenate(all_data, axis=0)
    labels = np.concatenate(all_labels, axis=0)

    print(f"\n  Total non-face data: {data.shape[0]} samples")
    return data, labels


if __name__ == "__main__":
    print("Preparing non-face emoji data...")
    data, labels = download_quickdraw_data(samples_per_class=100)
    print(f"Data shape: {data.shape}, Labels shape: {labels.shape}")
