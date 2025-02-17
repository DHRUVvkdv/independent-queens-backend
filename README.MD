# Independent Queens Backend

![Winner - Capital One's Best Financial Hack](https://img.shields.io/badge/Winner-Capital%20One's%20Best%20Financial%20Hack-blue)
![HackViolet 2025](https://img.shields.io/badge/HackViolet-2025-purple)
![FastAPI](https://img.shields.io/badge/FastAPI-0.105.0-009688)
![Python](https://img.shields.io/badge/Python-3.11-3776AB)

Backend infrastructure for Independent Queens - an AI-powered women's health and empowerment platform. Winner of Capital One's "Best Financial Hack" at HackViolet 2025.

## 🌟 Features

- 27 RESTful API endpoints for comprehensive platform functionality
- AI/ML integration with OpenAI and Hugging Face
- Secure authentication using AWS Cognito
- Canvas LMS integration for academic schedule synchronization
- Real-time health analytics and recommendations
- MongoDB database integration
- Docker containerization
- AWS Lambda deployment

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker
- MongoDB
- AWS Account
- Required API keys:
  - OpenAI
  - Hugging Face
  - Canvas LMS

### Local Development

1. Clone the repository:

```bash
git clone https://github.com/DHRUVvkdv/independent-queens-backend.git
cd independent-queens-backend
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your credentials
```

5. Run the development server:

```bash
uvicorn main:app --reload
```

### Docker Deployment

1. Build the Docker image:

```bash
docker build -t independent-queens-backend .
```

2. Run the container:

```bash
docker run -p 8000:8000 --env-file .env independent-queens-backend
```

## 📚 API Documentation

### Core Endpoints

1. User Management

   - POST `/api/v1/auth/signup`
   - POST `/api/v1/auth/signin`
   - GET `/api/v1/users/{email}`
   - PATCH `/api/v1/users/{email}`

2. Health Tracking

   - GET `/api/v1/menstrual-health/{email}/phase`
   - GET `/api/v1/menstrual-health/{email}/recommendations`
   - GET `/api/v1/menstrual-health/{email}/suggested-events`

3. Journal Management

   - GET `/api/v1/journals/user/{email}`
   - POST `/api/v1/journals`
   - GET `/api/v1/journals/insights`

4. Marketplace

   - GET `/api/v1/offers`
   - POST `/api/v1/offers`
   - GET `/api/v1/offers/{id}`

5. Canvas Integration
   - GET `/api/v1/canvas/assignments`

## 🛠️ Technology Stack

- **Framework**: FastAPI
- **Database**: MongoDB
- **Authentication**: AWS Cognito
- **AI/ML**:
  - OpenAI
  - Hugging Face
  - LangChain
- **Deployment**:
  - Docker
  - AWS Lambda
- **Testing**: Python unittest
- **Documentation**: FastAPI Swagger UI

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 🌟 Acknowledgments

- HackViolet 2025 organizers
- Capital One for the "Best Financial Hack" award
- The Association of Women in Computing at Virginia Tech

## 📄 License

MIT License
