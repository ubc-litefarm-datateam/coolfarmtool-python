#!/bin/bash

# Setup script for Cool Farm Interactive Template Builder

echo "Setting up Cool Farm Interactive Template Builder..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install rich python-dotenv requests

# Create necessary directories
echo "Creating directories..."
mkdir -p templates
mkdir -p schemas
mkdir -p assessments

# Download schemas if API client is available
echo "Attempting to download schemas..."
if [ -f "cool_farm_client.py" ]; then
    python cool_farm_client.py --action fetch-schemas
    echo "Schemas downloaded successfully"
else
    echo "cool_farm_client.py not found - you'll need to download schemas manually"
fi

echo "Setup complete!"
echo ""
echo "To run the interactive template builder:"
echo "python interactive_template_builder.py"
echo ""
echo "Make sure you have your JWT token configured in .env:"
echo "COOL_FARM_JWT_TOKEN=your_token_here"