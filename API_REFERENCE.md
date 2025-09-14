# Cool Farm Tool - API Reference

## CoolFarmAPIClient Class

### Initialization

```python
from cool_farm_client import CoolFarmAPIClient

# Initialize with default settings (.env file)
client = CoolFarmAPIClient()

# Initialize with custom environment file
client = CoolFarmAPIClient(env_file="custom.env")

# Initialize with custom base URL
client = CoolFarmAPIClient(base_url="https://api.coolfarm.org")
```

### Authentication Methods

#### `test_token() -> bool`
Tests if the current JWT token is valid and working by making a test request to the assessment endpoint.

```python
if client.test_token():
    print("Token is valid")
else:
    print("Token is invalid or expired")
```

**Returns:**
- `True` if token is valid and API is accessible
- `False` if token is expired, invalid, or API is unreachable

### Schema Management Methods

#### `fetch_schemas() -> bool`
**REQUIRED BEFORE USING INTERACTIVE BUILDER**

Downloads and saves assessment schemas for all available pathways to the `schemas/` directory.

```python
success = client.fetch_schemas()
if success:
    print("Schemas downloaded successfully")
    print("You can now use the interactive template builder")
```

**Returns:**
- `True` if schemas were successfully downloaded
- `False` if download failed

**Creates files:**
- `schemas/annuals_v3_schema.json`
- `schemas/perennials_v3_schema.json`
- `schemas/potatoes_v3_schema.json`
- `schemas/paddy_rice_v3_schema.json`

#### `get_pathway_schema(pathway: str) -> Optional[Dict[str, Any]]`
Gets schema for a specific pathway.

```python
schema = client.get_pathway_schema("Annuals v3")
```

**Parameters:**
- `pathway`: Assessment pathway name

**Available Pathways:**
- "Annuals v3"
- "Perennials v3" 
- "Potatoes v3"
- "Paddy Rice v3"

### Soil Data Methods

#### `get_soil_data(latitude: float, longitude: float) -> Optional[Dict[str, Any]]`
Fetches soil characteristics for given coordinates.

**Parameters:**
- `latitude`: Latitude coordinate (-90 to 90)
- `longitude`: Longitude coordinate (-180 to 180)

**Returns:**
- Dictionary containing soil data or None if failed

```python
soil_data = client.get_soil_data(latitude=40.7128, longitude=-74.0060)
if soil_data:
    print(f"Soil class: {soil_data['ipccSoilClass']}")
```

**Response Structure:**
```json
{
  "ipccSoilClass": "Sandy soils",
  "wrbSoilClass": {
    "wrbSoilClassName": "Fluvisols",
    "probability": 85.2
  }
}
```

### Template Methods

#### `get_default_assessment_template(pathway: str = "Annuals v3") -> Optional[Dict[str, Any]]`
Gets a default assessment template for the specified pathway from template files or creates from built-in data.

**Parameters:**
- `pathway`: Assessment pathway name

```python
template = client.get_default_assessment_template("Annuals v3")
```

**Template File Locations:**
- `templates/annuals_v3_template.json`
- `templates/perennials_v3_template.json`
- `templates/potatoes_v3_template.json`
- `templates/paddy_rice_v3_template.json`

#### `create_enhanced_template(pathway: str, latitude: float, longitude: float, output_file: str = None) -> Optional[Dict[str, Any]]`
Creates an enhanced template with automatic soil data integration.

```python
enhanced_template = client.create_enhanced_template(
    pathway="Annuals v3",
    latitude=40.7128,
    longitude=-74.0060,
    output_file="nyc_farm.json"
)
```

**Features:**
- Automatically fetches soil data for coordinates
- Maps IPCC soil classification to Cool Farm soil types
- Updates both farmDetails and cropDetails with soil information
- Saves enhanced template to specified file

**Soil Mapping:**
```python
# IPCC Soil Class → Cool Farm soilCharacteristic
{
    'Sandy soils': 'Low activity clay',
    'Clay soils': 'High activity clay', 
    'Organic soils': 'Organic soils',
    'Other soils': 'High activity clay'  # Default
}

# IPCC Soil Class → Cool Farm cropDetails.soilType
{
    'Sandy soils': 'Coarse',
    'Clay soils': 'Fine',
    'Organic soils': 'Organic',
    'Other soils': 'Medium'  # Default
}
```

#### `update_template_coordinates(template_file: str, latitude: float, longitude: float, output_file: str = None) -> bool`
Updates an existing template file with new coordinates and soil data.

```python
success = client.update_template_coordinates(
    template_file="templates/my_template.json",
    latitude=45.5,
    longitude=-73.6,
    output_file="templates/updated_template.json"
)
```

#### `load_assessment_from_file(file_path: str) -> Optional[Dict[str, Any]]`
Loads an assessment template from a JSON file.

```python
template = client.load_assessment_from_file("templates/my_farm.json")
```

### Assessment Methods

#### `calculate_assessment(assessment_data: Dict[str, Any], save_result: bool = True, output_file: str = None, pathway_name: str = None) -> Optional[Dict[str, Any]]`
Calculates a carbon footprint assessment.

**Parameters:**
- `assessment_data`: Complete assessment data dictionary
- `save_result`: Whether to save results to file (default: True)
- `output_file`: Custom output filename (optional)
- `pathway_name`: Pathway name for filename generation (optional)

```python
result = client.calculate_assessment(
    assessment_data=template,
    save_result=True,
    output_file="my_assessment.json"
)
```

**Automatic File Saving:**
- Creates `assessments/` directory if it doesn't exist
- Default filename: `assessment_{pathway}_{timestamp}.json`
- Custom filenames supported via `output_file` parameter

### Utility Methods

#### `get_pathways() -> Optional[List[str]]`
Returns list of available assessment pathways.

```python
pathways = client.get_pathways()
# Returns: ["Annuals v3", "Perennials v3", "Potatoes v3", "Paddy Rice v3"]
```

## InteractiveTemplateBuilder Class

**Note:** The interactive builder requires schema files to be downloaded first using `client.fetch_schemas()`.

### Initialization

```python
from interactive_builder import InteractiveTemplateBuilder

# Initialize with default schema directory
builder = InteractiveTemplateBuilder()

# Initialize with custom schema file
builder = InteractiveTemplateBuilder(schema_file="custom_schema.json")
```

### Prerequisites

Before using the interactive builder, ensure schemas are downloaded:

```bash
python cool_farm_client.py --action fetch-schemas
```

This creates the required schema files in `schemas/` directory.

### Main Methods

#### `build_template(pathway: str = "Annuals v3") -> Dict[str, Any]`
Builds a complete assessment template through interactive prompts.

```python
template = builder.build_template("Annuals v3")
```

**Interactive Process:**
1. Loads appropriate schema for validation
2. Prompts for farm location (coordinates)
3. Automatically fetches soil data
4. Guides through crop configuration
5. Sets up fertilizer applications
6. Validates all inputs against schema
7. Generates complete template

#### `save_template(template: Dict[str, Any], filename: str = None) -> str`
Saves a template to a JSON file.

```python
filename = builder.save_template(template, "my_custom_template.json")
```

**Default Naming:**
- Format: `interactive_{pathway}_{timestamp}.json`
- Saved to `templates/` directory
- Timestamp format: `YYYYMMDD_HHMMSS`

## Template Structure

### Farm Details
```json
{
  "farmDetails": {
    "country": "United States of America",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "climate": "Cool Temperate Moist",
    "soilCharacteristic": "High activity clay",
    "annualAverageTemperature": {
      "value": 20,
      "unit": "°C"
    }
  }
}
```

### Crop Details
```json
{
  "inputData": {
    "cropDetails": {
      "soilType": "Fine",
      "assessmentYear": 2024,
      "sandPercentage": 4,
      "cropType": "Maize",
      "area": {
        "value": 1000,
        "unit": "hectares"
      },
      "cropYield": {
        "value": 1000,
        "unit": "tonnes"
      },
      "farmGate": {
        "value": 500,
        "unit": "tonnes"
      }
    }
  }
}
```

### Fertilizer Applications
```json
{
  "fertiliser": {
    "fertilisers": [
      {
        "predefinedFertiliserType": "Urea - 46% N",
        "predefinedEmissionFactorRegionKey": "N America 2014",
        "predefinedApplicationRate": {
          "value": 150,
          "unit": "kg per hectare"
        }
      }
    ]
  }
}
```

### Complete Template Structure
```json
{
  "pathway": "Annuals v3",
  "farmIdentifier": "farm_01",
  "farmDetails": {
    "country": "United Kingdom of Great Britain and Northern Ireland",
    "latitude": 51.28,
    "longitude": 0.52,
    "climate": "Cool Temperate Moist",
    "soilCharacteristic": "High activity clay",
    "annualAverageTemperature": {
      "value": 20,
      "unit": "°C"
    }
  },
  "inputData": {
    "cropDetails": {
      "soilType": "Fine",
      "assessmentYear": 2024,
      "sandPercentage": 4,
      "cropType": "Maize",
      "area": {
        "value": 1000,
        "unit": "hectares"
      },
      "cropYield": {
        "value": 1000,
        "unit": "tonnes"
      },
      "farmGate": {
        "value": 500,
        "unit": "tonnes"
      }
    },
    "fertiliser": {
      "fertilisers": [
        {
          "predefinedFertiliserType": "Urea - 46% N",
          "predefinedEmissionFactorRegionKey": "N America 2014",
          "predefinedApplicationRate": {
            "value": 150,
            "unit": "kg per hectare"
          }
        }
      ]
    }
  }
}
```

## Command Line Interface

### Setup Commands

```bash
# Test JWT token
python cool_farm_client.py --action test

# Download schemas (required for interactive builder)
python cool_farm_client.py --action fetch-schemas

# List available pathways
python cool_farm_client.py --action pathways
```

### Data Retrieval Commands

```bash
# Get soil data for coordinates
python cool_farm_client.py --action soil-data --latitude 40.7128 --longitude -74.0060
```

### Template Management Commands

```bash
# Create enhanced template with soil data
python cool_farm_client.py --action enhance-template --pathway "Annuals v3" --latitude 40.7 --longitude -74.0 --output-file farm.json

# Update existing template coordinates
python cool_farm_client.py --action update-coords --input-file templates/farm.json --latitude 45.5 --longitude -73.6
```

### Assessment Commands

```bash
# Run assessment from template file
python cool_farm_client.py --action assess --input-file templates/farm.json

# Run assessment with default template
python cool_farm_client.py --action assess --pathway "Annuals v3"

# Run assessment with custom output file
python cool_farm_client.py --action assess --input-file templates/farm.json --output-file my_results.json
```

### Interactive Builder

```bash
# Start interactive template builder (requires schemas)
python interactive_builder.py
```

## Error Handling

### Common Error Responses

#### Schema Files Missing
```
FileNotFoundError: Schema file not found
```
**Solution:** Download schemas first:
```bash
python cool_farm_client.py --action fetch-schemas
```

#### Invalid JWT Token (401)
```
❌ JWT token expired or invalid!
```
**Solution:** Refresh your JWT token from the browser

#### Bad Request (400)
```
❌ Bad request - check your assessment data
Error details: {...}
```
**Solution:** Verify your template data matches the expected schema

#### Network Timeout
```
❌ Request timed out - Cool Farm API might be slow
```
**Solution:** Retry the request or check your internet connection

#### Token Expiry Warning
```
⚠️ JWT token expires in 0:45:23
Consider getting a fresh token soon.
```
**Solution:** Proactively refresh your token

## Best Practices

### 1. Schema Management
- Always run `fetch_schemas()` before using the interactive builder
- Schemas are downloaded once and cached locally
- Re-download schemas if API schemas are updated

### 2. Token Management
- Check token expiry regularly using `test_token()`
- Refresh tokens proactively before expiration
- Store tokens securely in environment files

### 3. Template Validation
- Use the interactive builder for schema-validated templates
- Validate coordinates before fetching soil data
- Test templates with small datasets first

### 4. Error Handling
```python
try:
    # Ensure schemas are available
    if not client.fetch_schemas():
        print("Failed to download schemas")
        return
    
    # Create and run assessment
    result = client.calculate_assessment(template)
    if result:
        print("Assessment successful")
    else:
        print("Assessment failed")
except Exception as e:
    print(f"Error: {e}")
```

### 5. File Organization
```
project/
├── .env                           # JWT token
├── schemas/                       # Downloaded from API (required!)
│   ├── annuals_v3_schema.json
│   ├── perennials_v3_schema.json
│   ├── potatoes_v3_schema.json
│   └── paddy_rice_v3_schema.json
├── templates/                     # Template files
│   ├── annuals_v3_template.json    # Default templates
│   ├── interactive_*.json          # Interactive builder output
│   └── enhanced_*.json             # Enhanced templates with soil data
└── assessments/                   # Results
    └── assessment_*.json
```

## Troubleshooting

### Interactive Builder Issues

#### "Schema file not found" Error
1. Verify schemas directory exists: `ls schemas/`
2. Download schemas: `python cool_farm_client.py --action fetch-schemas`
3. Check network connectivity and token validity

#### Builder Exits or Crashes
1. Ensure valid JWT token: `python cool_farm_client.py --action test`
2. Check schema files are valid JSON
3. Verify Python version compatibility (3.7+)

### Token Issues
1. Verify token is correctly copied (no extra spaces)
2. Check token expiry with `test_token()`
3. Refresh token from browser if expired
4. Ensure `.env` file format is correct

### Template Issues
1. Validate JSON syntax using online validators
2. Check required fields are present using schemas
3. Verify enum values match schema definitions
4. Use interactive builder for guaranteed valid templates

### API Issues
1. Check internet connectivity
2. Verify API endpoint URLs are accessible
3. Review request/response logs for debugging
4. Test with minimal assessment data

## Workflow Examples

### Complete Workflow with Interactive Builder

```bash
# 1. Setup and test
python cool_farm_client.py --action test

# 2. Download schemas (required!)
python cool_farm_client.py --action fetch-schemas

# 3. Create template interactively
python interactive_builder.py

# 4. Run assessment
python cool_farm_client.py --action assess --input-file templates/interactive_annuals_v3_20241201_143022.json
```

### Programmatic Workflow

```python
from cool_farm_client import CoolFarmAPIClient

# Initialize and setup
client = CoolFarmAPIClient()

# Download schemas (required for validation)
if not client.fetch_schemas():
    print("Failed to download schemas")
    exit(1)

# Create enhanced template
template = client.create_enhanced_template(
    pathway="Annuals v3",
    latitude=40.7128,
    longitude=-74.0060,
    output_file="nyc_farm.json"
)

# Customize template (edit JSON file manually or programmatically)
# ... modify template as needed ...

# Run assessment
result = client.calculate_assessment(
    template,
    output_file="nyc_assessment.json"
)

if result:
    print("Assessment completed successfully!")
```

### Batch Processing Multiple Farms

```python
farms = [
    {"name": "Farm_A", "lat": 40.7, "lon": -74.0},
    {"name": "Farm_B", "lat": 41.8, "lon": -87.6},
    {"name": "Farm_C", "lat": 37.7, "lon": -122.4}
]

client = CoolFarmAPIClient()

# Ensure schemas are available
client.fetch_schemas()

for farm in farms:
    print(f"Processing {farm['name']}...")
    
    # Create enhanced template
    template = client.create_enhanced_template(
        pathway="Annuals v3",
        latitude=farm["lat"],
        longitude=farm["lon"],
        output_file=f"{farm['name']}_template.json"
    )
    
    if template:
        # Run assessment
        result = client.calculate_assessment(
            template,
            output_file=f"{farm['name']}_assessment.json"
        )
        
        if result:
            print(f"✅ {farm['name']} assessment completed")
        else:
            print(f"❌ {farm['name']} assessment failed")
```

## Advanced Usage

### Template Customization

```python
# Load and modify template
template = client.get_default_assessment_template("Annuals v3")

# Customize crop details
template["inputData"]["cropDetails"]["cropType"] = "Wheat"
template["inputData"]["cropDetails"]["area"]["value"] = 500
template["inputData"]["cropDetails"]["cropYield"]["value"] = 750

# Add custom fertilizers
fertilizer = {
    "predefinedFertiliserType": "Ammonium Nitrate - 35% N",
    "predefinedEmissionFactorRegionKey": "Europe 2014",
    "predefinedApplicationRate": {
        "value": 100,
        "unit": "kg per hectare"
    }
}
template["inputData"]["fertiliser"]["fertilisers"].append(fertilizer)

# Run assessment with customized template
result = client.calculate_assessment(template)
```
