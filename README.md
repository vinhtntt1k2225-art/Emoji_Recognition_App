# 🎨 Emoji Recognizer

> AI-powered emoji recognition from hand-drawn sketches using Artificial Neural Network

## 📋 Overview

Ứng dụng web cho phép người dùng vẽ emoji bằng chuột trên canvas, sau đó sử dụng mô hình **Artificial Neural Network (ANN)** để nhận dạng emoji đã vẽ.

### Tech Stack
- **Frontend**: React 18 + TypeScript + Tailwind CSS v4 + Framer Motion
- **Backend**: Python FastAPI
- **AI Model**: PyTorch ANN (Fully Connected Neural Network)
- **Auth**: JWT + SQLite + bcrypt
- **Dataset**: Hybrid (Synthetic face data + Google Quick Draw)

### Supported Emojis (10 loại)
| Face Emojis | Other Emojis |
|:---|:---|
| 😊 Happy | ❤️ Heart |
| 😢 Sad | ⭐ Star |
| 😠 Angry | 👍 Thumbs Up |
| 😮 Surprise | ☀️ Sun |
| 😐 Neutral | |
| 😍 Love | |

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 2. Train the ANN Model

```bash
cd backend
python -m app.ml.train --samples 10000 --epochs 30
```

Quá trình training sẽ:
- Generate 60,000 synthetic face emoji images
- Download 40,000 Quick Draw images (heart, star, thumbs up, sun)
- Train mô hình ANN 4 layers
- Lưu model vào `backend/app/ml/emoji_model.pth`

### 3. Start the Backend

```bash
cd backend
python run.py
```

Server chạy tại: http://localhost:8000

### 4. Start the Frontend

```bash
cd frontend
npm run dev
```

App chạy tại: http://localhost:5173

---

## 🧠 ANN Architecture

```
Input (784) → Linear(512) + BatchNorm + ReLU + Dropout(0.3)
           → Linear(256) + BatchNorm + ReLU + Dropout(0.3)
           → Linear(128) + BatchNorm + ReLU + Dropout(0.2)
           → Linear(10) → Softmax → Prediction
```

- **Input**: 28×28 grayscale image flattened to 784 dimensions
- **Hidden layers**: 3 layers with BatchNorm + ReLU activation + Dropout
- **Output**: 10 classes with Softmax probability distribution
- **Total parameters**: ~530K

---

## 📁 Project Structure

```
emoji-recognizer/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app + API routes
│   │   ├── auth.py           # JWT authentication
│   │   ├── database.py       # SQLite database
│   │   ├── models.py         # Pydantic schemas
│   │   └── ml/
│   │       ├── model.py      # ANN model definition
│   │       ├── train.py      # Training script
│   │       ├── predict.py    # Inference logic
│   │       ├── generate_faces.py  # Synthetic face data
│   │       └── download_data.py   # Quick Draw downloader
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page views
│   │   ├── hooks/            # Auth context
│   │   ├── services/         # API client
│   │   └── index.css         # Design system
│   └── ...
└── README.md
```

---

## 👥 API Endpoints

| Method | Endpoint | Auth | Description |
|:---|:---|:---|:---|
| POST | `/api/auth/register` | ❌ | Register new user |
| POST | `/api/auth/login` | ❌ | Login, get JWT |
| GET | `/api/auth/me` | ✅ | Get current user |
| POST | `/api/predict` | ✅ | Predict emoji from drawing |
| GET | `/api/history` | ✅ | Get prediction history |
| GET | `/api/categories` | ❌ | List supported emojis |
| GET | `/api/health` | ❌ | Health check |

---

## 🎓 Bài tập - Trí Tuệ Nhân Tạo

**Đề bài**: Thiết kế app nhận dạng các Emoji đơn giản vẽ trên màn hình bằng chuột

**Mô hình**: Artificial Neural Network (ANN) - Fully Connected Network
- Không sử dụng CNN (Convolutional Neural Network)
- Sử dụng thuần ANN với các fully connected layers
- Đạt accuracy ~85-90% trên validation set
