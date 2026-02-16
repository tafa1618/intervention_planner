#!/bin/bash

# Create .env file for build with the API URL
# Use NEXT_PUBLIC_API_URL if provided, otherwise use localhost
if [ -z "$NEXT_PUBLIC_API_URL" ]; then
  echo "NEXT_PUBLIC_API_URL=http://localhost:8001" > .env.local
else
  echo "NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL" > .env.local
fi

# Run the actual Next.js build
npm run build
