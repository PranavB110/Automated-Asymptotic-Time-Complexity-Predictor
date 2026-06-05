# Time Complexity Predictor

Automated time complexity prediction for code using machine learning. Supports Python, JavaScript, Java, and C++.

## Quick Start

### Prerequisites
- Python 3.13
- Node.js 22

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/time-complexity-predictor.git
cd complexity-predictor

# Backend
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend/complexity-ui
npm install
npm run dev
```

Open http://localhost:5173

### Docker

```bash
docker-compose build
docker-compose up
```

## API

**POST /predict**
```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"code": "for i in range(n): for j in range(n): print(i,j)", "language": "auto"}'
```

Response: `{"complexity": "O(n^2)", "confidence": 79.0, ...}`

**GET /health** — API status
**GET /charts-list** — Visualization charts

## Architecture

- **Backend:** FastAPI + Random Forest (80% accuracy)
- **Frontend:** React + Vite + Monaco Editor
- **ML:** AST feature extraction (15 features) + tree-sitter (multi-language)

## Features

- Real-time complexity prediction (<50ms)
- Multi-language support (Python, JavaScript, Java, C++)
- Session history tracking
- Model analytics & visualizations
- Automatic language detection

## Project Structure   
├── api/main.py           # FastAPI backend
├── model/                # ML training & serialization
├── feature_extraction/   # AST parsers
├── frontend/             # React + Vite
├── data/dataset.py       # 22 training samples
└── docker-compose.yml    # Container orchestration

## Supported Complexities

O(1), O(log n), O(n), O(n log n), O(n²), O(n³), O(2ⁿ)

## Tech Stack

Python 3.13 | FastAPI | React 19 | Scikit-learn | tree-sitter | Docker

## License

MIT

## Status

✅ Production-ready | ⏳ MLOps in progress
