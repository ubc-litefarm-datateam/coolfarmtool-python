# Cool Farm Tool - Carbon Footprint Assessment API Client

A comprehensive Python client for the Cool Farm Tool API that enables carbon footprint assessments for agricultural operations.

## Quick Start Guide

### Prerequisites

- Python 3.7+
- Cool Farm API account with valid JWT token

### Step-by-Step Setup

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Configure Authentication

Create a `.env` file in your project root:

```bash
COOL_FARM_JWT_TOKEN=your_jwt_token_here
```

### OR

#### Run the following command in terminal

```bash
bash setup.sh         
```

**How to get your JWT token:**

1. Go to https://testing.api.cfp.coolfarm.org
2. Log in with your credentials
3. Open browser DevTools (F12) → Network tab
4. Refresh the page
5. Look for API requests with `Authorization: Bearer eyJ...`
6. Copy the token part (everything after "Bearer ")

#### 3. Test Your Setup

```bash
python cool_farm_client.py --action test
```

You should see: `✅ Token valid - assessment endpoint working`

#### 4. Download Assessment Schemas (Required!)

**This step is required before using the interactive builder:**

```bash
python cool_farm_client.py --action fetch-schemas
```

This downloads schema files to `schemas/` directory:

- `annuals_v3_schema.json`
- `perennials_v3_schema.json` 
- `potatoes_v3_schema.json`
- `paddy_rice_v3_schema.json`

#### 5. Use the Interactive Builder (Few changess need to be made!)

```bash
python interactive_builder.py
```

The interactive builder will:

1. Load the appropriate schema for validation
2. Guide you through farm location setup
3. Automatically fetch soil data from your coordinates
4. Help you configure crop details
5. Set up fertilizer applications
6. Generate a complete assessment template
7. Save the template for later use

#### 6. Run Your Assessment

```bash
python cool_farm_client.py --action assess --input-file templates/your_template.json
```

## Usage Examples

### Basic Workflow

```bash
# 1. Test your token
python cool_farm_client.py --action test

# 2. Download schemas (first time only)
python cool_farm_client.py --action fetch-schemas

# 3. Create a template interactively
python interactive_builder.py

# 4. Run assessment
python cool_farm_client.py --action assess --input-file templates/interactive_annuals_v3_20241201_143022.json
```

### Advanced Usage

#### Get Soil Data for Coordinates

```bash
python cool_farm_client.py --action soil-data --latitude 40.7128 --longitude -74.0060
```

#### Create Enhanced Template with Soil Data

```bash
python cool_farm_client.py --action enhance-template --pathway "Annuals v3" --latitude 40.7 --longitude -74.0 --output-file nyc_farm.json
```

#### Update Existing Template Coordinates

```bash
python cool_farm_client.py --action update-coords --input-file templates/my_template.json --latitude 45.5 --longitude -73.6
```

#### Run Assessment with Default Template

```bash
python cool_farm_client.py --action assess --pathway "Annuals v3"
```

## Available Assessment Pathways

- **Annuals v3** - Annual crops (wheat, corn, soybeans, etc.)
- **Perennials v3** - Perennial crops (fruit trees, nuts, etc.)
- **Potatoes v3** - Potato cultivation
- **Paddy Rice v3** - Rice cultivation in flooded fields

## File Structure After Setup

```
your-project/
├── .env                           # Your JWT token
├── cool_farm_client.py           # Main API client
├── interactive_builder.py        # Interactive template builder
├── schemas/                       # Downloaded from API (required!)
│   ├── annuals_v3_schema.json
│   ├── perennials_v3_schema.json
│   ├── potatoes_v3_schema.json
│   └── paddy_rice_v3_schema.json
├── templates/                     # Generated templates
│   ├── annuals_v3_template.json
│   ├── interactive_annuals_v3_*.json
│   └── enhanced_*.json
└── assessments/                   # Assessment results
    └── assessment_*.json
```

## Troubleshooting

### Common Issues

#### "Schema file not found" Error

This means you skipped step 4. The interactive builder requires schema files:

```bash
python cool_farm_client.py --action fetch-schemas
```

#### Token Issues

- **401 Unauthorized**: Your token is expired or invalid
- **Solution**: Get a fresh token from the browser (step 2 above)
- **Test with**: `python cool_farm_client.py --action test`

#### Interactive Builder Not Working

1. Ensure schemas are downloaded: `python cool_farm_client.py --action fetch-schemas`
2. Check that `schemas/` directory exists with JSON files
3. Verify your token is valid: `python cool_farm_client.py --action test`

#### Network Issues

- Check your internet connection
- Verify the API endpoint is accessible
- Try: `python cool_farm_client.py --action test`

### Getting Help

#### Command Help

```bash
python cool_farm_client.py --help
```

#### Available Actions

```bash
python cool_farm_client.py --action pathways  # List available pathways
```

## API Client Features

### Soil Data Integration

Automatically fetches and integrates soil characteristics based on GPS coordinates:

- IPCC soil classification
- WRB soil classification
- Automatic mapping to Cool Farm soil types

### Template Management

- Interactive template builder with schema validation
- Enhanced templates with soil data integration
- Template coordinate updates
- Default templates for all pathways

### Assessment Execution

- Full assessment calculations
- Comprehensive error handling
- Automatic result saving
- Batch processing capabilities

### Token Management

- JWT token validation and expiry checking
- Automatic token refresh guidance
- Comprehensive authentication debugging

## Integration Examples

### Programmatic Usage

```python
from cool_farm_client import CoolFarmAPIClient

# Initialize client
client = CoolFarmAPIClient()

# Test connection
if client.test_token():
    print("Connected to Cool Farm API")

# Get soil data
soil_data = client.get_soil_data(latitude=40.7, longitude=-74.0)

# Create enhanced template
template = client.create_enhanced_template(
    pathway="Annuals v3",
    latitude=40.7,
    longitude=-74.0,
    output_file="my_farm.json"
)

# Run assessment
result = client.calculate_assessment(template)
```

### Batch Processing

```python
# Process multiple farms
farms = [
    {"lat": 40.7, "lon": -74.0, "name": "Farm_A"},
    {"lat": 41.8, "lon": -87.6, "name": "Farm_B"}
]

for farm in farms:
    template = client.create_enhanced_template(
        pathway="Annuals v3",
        latitude=farm["lat"],
        longitude=farm["lon"],
        output_file=f"{farm['name']}_template.json"
    )
    
    result = client.calculate_assessment(
        template, 
        output_file=f"{farm['name']}_assessment.json"
    )
```

## Command Reference

### Essential Commands

```bash
# Test connection
python cool_farm_client.py --action test

# Create enhanced template with soil data
python cool_farm_client.py --action enhance-template --pathway "Annuals v3" --latitude LAT --longitude LON --output-file FILE.json

# Quick assessment with default template
python cool_farm_client.py --action assess --pathway "Annuals v3"
```

### Data Retrieval

```bash
# Get available pathways
python cool_farm_client.py --action pathways

# Get soil data for location
python cool_farm_client.py --action soil-data --latitude LAT --longitude LON
```

### Template Management

```bash
# Create enhanced template with soil data
python cool_farm_client.py --action enhance-template --pathway "PATHWAY" --latitude LAT --longitude LON --output-file FILE.json

# Update template coordinates
python cool_farm_client.py --action update-coords --input-file TEMPLATE.json --latitude LAT --longitude LON
```

### Assessment Execution

```bash
# Run assessment from template file
python cool_farm_client.py --action assess --input-file templates/my_template.json

# Run assessment with custom output
python cool_farm_client.py --action assess --input-file templates/my_template.json --output-file my_results.json
```

## Next Steps

1. **Customize Templates**: Edit generated template files to add specific farm details
2. **Try Different Pathways**: Experiment with perennials, potatoes, or rice assessments
3. **Batch Processing**: Process multiple farms or scenarios
4. **API Integration**: Integrate the client into your own applications
5. **Advanced Features**: Explore fertilizer optimization and scenario comparisons

For detailed API documentation, see `API_REFERENCE.md`.

## Support

- Check the troubleshooting section above
- Review `API_REFERENCE.md` for detailed documentation
- Ensure your JWT token is current and valid
- Verify all required schema files are downloaded