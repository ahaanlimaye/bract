const awsConfig = {
  aws_project_region: 'your_region',
  aws_cognito_region: 'your_region',
  aws_user_pools_id: 'your_user_pool_id',
  aws_user_pools_web_client_id: 'your_client_id',
  oauth: {
    domain: 'your_cognito_domain',
    scope: ['email', 'openid', 'profile'],
    redirectSignIn: 'http://localhost:5173/',
    redirectSignOut: 'http://localhost:5173/',
    responseType: 'code',
  },
};

export default awsConfig; 