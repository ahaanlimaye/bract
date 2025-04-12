# Bract - Subscription Management Platform

Bract is a subscription management platform that helps users track and manage their recurring payments. It connects to users' bank accounts through Plaid, identifies recurring subscriptions, and sends email reminders before payments are due.

## Features

- 🔐 Secure user authentication with Google OAuth
- 💳 Bank account integration through Plaid
- 📧 Automated email reminders for upcoming subscription payments
- 📊 Dashboard to view and manage subscriptions
- 🔄 Automatic subscription detection from transaction data

## Tech Stack

- **Frontend**: React + TypeScript + Vite
- **Backend**: AWS Serverless (Lambda, API Gateway, DynamoDB)
- **Authentication**: AWS Cognito
- **Bank Integration**: Plaid API
- **Email Service**: AWS SES
- **Infrastructure**: AWS SAM (Serverless Application Model)

## Prerequisites

- Node.js (v18 or higher)
- Python (v3.9 or higher)
- AWS CLI
- AWS SAM CLI
- Plaid Developer Account

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/bract.git
cd bract
```

### 2. Set Up Environment Variables

Copy the example environment files and fill in your credentials:

```bash
# Backend
cp .env.example .env

# Frontend
cp frontend/src/aws-exports.example.ts frontend/src/aws-exports.ts
```

### 3. Install Dependencies

```bash
# Install frontend dependencies
cd frontend
npm install

# Install backend dependencies
cd ..
pip install -r requirements.txt
```

### 4. Configure AWS

Make sure you have AWS credentials configured:

```bash
aws configure
```

### 5. Deploy Backend

```bash
sam build
sam deploy --guided
```

### 6. Start Development Server

```bash
# Start frontend
cd frontend
npm run dev

# In a new terminal, start backend
sam local start-api
```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# AWS Cognito Configuration
USER_POOL_ID=your_user_pool_id
CLIENT_ID=your_client_id

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Plaid Configuration
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret
PLAID_ENV=sandbox  # or development or production
```

## Project Structure

```
bract/
├── frontend/           # React frontend application
├── .aws-sam/          # AWS SAM build artifacts
├── template.yaml      # AWS SAM template
├── .env               # Environment variables (not tracked by git)
├── .env.example       # Example environment variables
└── README.md          # This file
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [AWS SAM](https://aws.amazon.com/serverless/sam/)
- [Plaid API](https://plaid.com/docs/)
- [React](https://reactjs.org/)
- [TypeScript](https://www.typescriptlang.org/) 