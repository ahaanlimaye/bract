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

Before you begin, ensure you have the following installed:

- **Node.js** (v18 or higher) - [Download here](https://nodejs.org/)
- **Python** (v3.9 or higher) - [Download here](https://www.python.org/downloads/)
- **AWS CLI** - [Installation guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- **AWS SAM CLI** - [Installation guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- **Git** - [Download here](https://git-scm.com/)

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/bract.git
cd bract
```

### 2. Install Dependencies

```bash
# Install frontend dependencies
cd frontend
npm install

# Install backend dependencies
cd ..
pip install -r backend/requirements.txt
```

### 3. Set Up AWS Account

1. **Create AWS Account**: [Sign up here](https://aws.amazon.com/)
2. **Create IAM User**: 
   - Go to IAM Console → Users → Create User
   - Attach `AdministratorAccess` policy (for development)
   - Create access keys and configure AWS CLI:
   ```bash
   aws configure
   ```

## AWS Service Setup

### 1. Plaid Developer Account

1. **Sign up**: [Plaid Dashboard](https://dashboard.plaid.com/signup)
2. **Create App**: Get your `PLAID_CLIENT_ID` and `PLAID_SECRET`
3. **Choose Environment**: Start with `sandbox` for testing

### 2. Google OAuth Setup

1. **Google Cloud Console**: [Go here](https://console.cloud.google.com/)
2. **Create Project**: New project → Enable Google+ API
3. **OAuth 2.0 Credentials**: 
   - Create OAuth 2.0 Client ID
   - Add authorized redirect URIs (you'll get these after Cognito setup)
   - Save `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`

### 3. Environment Configuration

Create a `.env` file in the root directory:

```env
# AWS Cognito Configuration (you'll get these after deployment)
USER_POOL_ID=
CLIENT_ID=

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Plaid Configuration
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret
PLAID_ENV=sandbox

# React App API URL (you'll get this after deployment)
REACT_APP_API_URL=

# Email Configuration (optional for now)
FROM_EMAIL=your-email@example.com
```

## Backend Deployment

### 1. Build and Deploy

```bash
# Build the SAM application
sam build --use-container

# Deploy (first time)
sam deploy --guided
```

**Important**: Use `--use-container` flag for better environment consistency.

### 2. Deployment Parameters

When prompted during deployment, use these values:

- **Stack Name**: `bract-app` (or your preferred name)
- **AWS Region**: Choose your preferred region (e.g., `us-east-1`)
- **Parameter Overrides**:
  - `GoogleClientId`: Your Google OAuth Client ID
  - `GoogleClientSecret`: Your Google OAuth Client Secret
  - `PlaidClientId`: Your Plaid Client ID
  - `PlaidSecret`: Your Plaid Secret
  - `PlaidEnv`: `sandbox` (for testing)
  - `FromEmail`: Your email address

### 3. Post-Deployment Setup

After successful deployment, you'll get outputs including:
- `UserPoolId` (Cognito User Pool ID)
- `UserPoolClientId` (Cognito Client ID)
- `ApiEndpoint` (API Gateway URL)

**Update your `.env` file** with these values:

```env
USER_POOL_ID=us-east-1_xxxxxxxxx
CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
REACT_APP_API_URL=https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/Prod/
```

### 4. Update Google OAuth Redirect URIs

Go back to Google Cloud Console and add these redirect URIs:
```
https://cognito-idp.us-east-1.amazonaws.com/us-east-1_xxxxxxxxx
https://cognito-idp.us-east-1.amazonaws.com/us-east-1_xxxxxxxxx/
```

## Frontend Configuration

### 1. Update AWS Configuration

The frontend needs to know about your Cognito User Pool. Update `frontend/src/aws-exports.ts`:

```typescript
const awsConfig = {
  aws_project_region: 'us-east-1',
  aws_cognito_region: 'us-east-1',
  aws_user_pools_id: 'us-east-1_xxxxxxxxx', // Your User Pool ID
  aws_user_pools_web_client_id: 'xxxxxxxxxxxxxxxxxxxxxxxxxx', // Your Client ID
  oauth: {
    domain: 'your-domain.auth.us-east-1.amazoncognito.com', // Your Cognito Domain
    scope: ['email', 'openid', 'profile'],
    redirectSignIn: 'http://localhost:5173/', // Local development
    redirectSignOut: 'http://localhost:5173/',
    responseType: 'code'
  }
};

export default awsConfig;
```

### 2. Update API Base URL

In `frontend/src/services/plaidService.ts` and other service files, update the API base URL:

```typescript
const API_BASE_URL = 'https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/Prod/';
```

## Local Development

### 1. Start Frontend

```bash
cd frontend
npm run dev
```

Your app will be available at `http://localhost:5173`

### 2. Test Backend (Optional)

```bash
# In a new terminal
sam local start-api
```

This runs your Lambda functions locally for testing.

## Testing the Application

### 1. User Registration

1. Open `http://localhost:5173`
2. Click "Sign Up" and create an account
3. Verify your email (check Cognito console)

### 2. Link Bank Account

1. Sign in to your account
2. Click "Link Bank Account"
3. Use Plaid Sandbox credentials:
   - **Username**: `user_good`
   - **Password**: `pass_good`
   - **Bank**: Choose any sandbox institution

### 3. View Subscriptions

After linking your account, you should see:
- Your bank accounts
- Recurring transactions (subscriptions)
- Option to set reminders

## Troubleshooting

### Common Issues

1. **"No module named 'plaid'"**
   - Ensure you're in the `bract-lambda` conda environment
   - Run `pip install -r backend/requirements.txt`

2. **"Invalid credentials"**
   - Check your `.env` file has correct values
   - Verify AWS credentials with `aws sts get-caller-identity`

3. **"User pool not found"**
   - Ensure `USER_POOL_ID` in `.env` matches your deployed Cognito User Pool
   - Check the deployment outputs

4. **"Plaid link-initialize.js script was embedded more than once"**
   - This is a development-only warning, not an error
   - The app should still work correctly

### Debugging

- **CloudWatch Logs**: Check Lambda function logs in AWS Console
- **Browser Console**: Check for JavaScript errors
- **Network Tab**: Verify API calls are working

## Production Considerations

Before going to production:

1. **Change Plaid Environment**: Update `PLAID_ENV` to `production`
2. **Verify Email in SES**: Verify your `FROM_EMAIL` in AWS SES
3. **Update Redirect URIs**: Change from `localhost` to your production domain
4. **Security**: Review IAM policies and restrict permissions
5. **Monitoring**: Set up CloudWatch alarms and logging

## Project Structure

```
bract/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API service calls
│   │   └── aws-exports.ts   # AWS configuration
│   ├── package.json
│   └── vite.config.ts
├── backend/                  # AWS Lambda backend
│   ├── src/
│   │   ├── handlers/        # Lambda function handlers
│   │   ├── services/        # Business logic services
│   │   ├── models/          # Data models
│   │   └── requirements.txt # Python dependencies
│   └── template.yaml        # SAM template
├── .aws-sam/                # SAM build artifacts (auto-generated)
├── .env                     # Environment variables (not tracked by git)
├── samconfig.toml           # SAM deployment configuration
└── README.md                # This file
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review CloudWatch logs for backend errors
3. Check browser console for frontend errors
4. Open an issue on GitHub with detailed error information

## Acknowledgments

- [AWS SAM](https://aws.amazon.com/serverless/sam/) - Serverless application framework
- [Plaid API](https://plaid.com/docs/) - Financial data platform
- [React](https://reactjs.org/) - Frontend framework
- [TypeScript](https://www.typescriptlang.org/) - Type-safe JavaScript
- [AWS Cognito](https://aws.amazon.com/cognito/) - User authentication 