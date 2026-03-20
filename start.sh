#!/bin/bash
cd backend

# Create database if it doesn't exist
if [ ! -f plum_ems.db ]; then
  echo "[*] Database not found, generating test data..."
  python generate_data.py
fi

# Start Flask app
python app.py
