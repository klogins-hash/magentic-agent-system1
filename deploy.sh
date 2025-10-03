#!/bin/bash

# Self-Building Agent System - Railway Deployment Script

set -e

echo "🚀 Deploying Self-Building Agent System to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if logged in to Railway
if ! railway whoami &> /dev/null; then
    echo "🔐 Please log in to Railway..."
    railway login
fi

# Check for required environment variables
if [ -z "$GROQ_API_KEY" ]; then
    echo "⚠️  GROQ_API_KEY not set. Please set it in Railway dashboard after deployment."
    echo "   Get your key from: https://console.groq.com/keys"
fi

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit - Self-Building Agent System"
fi

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment initiated!"
echo ""
echo "📋 Next steps:"
echo "1. Go to your Railway dashboard: https://railway.app/dashboard"
echo "2. Set the GROQ_API_KEY environment variable"
echo "3. Wait for deployment to complete"
echo "4. Open your app URL and test agent creation!"
echo ""
echo "🧪 Test with: 'Create a customer service agent that helps with product questions'"
