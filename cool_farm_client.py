import requests
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import base64
import argparse
import sys

# Soil Data Lookup
# python cool_farm_client.py --action soil-data --latitude 51.28 --longitude 0.52
# Create Enhanced Template
# python cool_farm_client.py --action enhance-template --pathway "Annuals v3" --latitude 51.28 --longitude 0.52 --output-file my_farm_template.json
# Update Existing Template Coordinates
# python cool_farm_client.py --action update-coords --input-file templates/my_template.json --latitude 45.5 --longitude -73.6
# Workflow Example
# 1. Create an enhanced template with soil data:
# python cool_farm_client.py --action enhance-template --pathway "Annuals v3" --latitude 40.7128 --longitude -74.0060 --output-file nyc_farm_template.json
# 2. Edit the template file to customize crop details, fertilizers, etc.
# 3. Run assessment with your customized template:
# python cool_farm_client.py --action assess --input-file templates/nyc_farm_template.json

class CoolFarmAPIClient:
    """
    Enhanced Cool Farm API client with soil data fetching capabilities
    Handles JWT token management and provides flexible assessment methods
    """
    
    def __init__(self, env_file: str = ".env", base_url: str = "https://testing.api.cfp.coolfarm.org"):
        """
        Initialize the Cool Farm API client
        
        Args:
            env_file: Path to environment file containing JWT token
            base_url: Base URL for the Cool Farm API
        """
        load_dotenv(env_file)
        self.base_url = base_url
        self.jwt_token = os.getenv("COOL_FARM_JWT_TOKEN", "").strip()
        
        if self.jwt_token:
            self._check_token_expiry()
        else:
            print("❌ No JWT token found in environment")
            self._show_token_instructions()
    
    def _decode_jwt_expiry(self) -> Optional[datetime]:
        """Decode JWT token to check expiry time"""
        try:
            parts = self.jwt_token.split('.')
            if len(parts) != 3:
                return None
            
            # Decode payload (add padding if needed)
            payload = parts[1]
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding
            
            decoded = base64.urlsafe_b64decode(payload)
            payload_data = json.loads(decoded)
            
            exp_timestamp = payload_data.get('exp')
            if exp_timestamp:
                return datetime.fromtimestamp(exp_timestamp)
            
        except Exception as e:
            print(f"Could not decode token expiry: {e}")
        
        return None
    
    def _check_token_expiry(self):
        """Check and warn about token expiry"""
        expiry = self._decode_jwt_expiry()
        if expiry:
            now = datetime.now()
            time_left = expiry - now
            
            if time_left.total_seconds() < 0:
                print(f"⚠️ JWT token EXPIRED {-time_left} ago!")
                print("You need to get a fresh token from your browser.")
            elif time_left.total_seconds() < 3600:  # Less than 1 hour
                print(f"⚠️ JWT token expires in {time_left}")
                print("Consider getting a fresh token soon.")
            else:
                print(f"✅ JWT token valid for {time_left}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests"""
        if not self.jwt_token:
            return {}
        return {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    def _show_token_instructions(self):
        """Show instructions for getting a fresh token"""
        print("\n" + "="*50)
        print("🔄 HOW TO GET A FRESH JWT TOKEN:")
        print("1. Open https://testing.api.cfp.coolfarm.org in browser")
        print("2. Log in with your credentials")
        print("3. Open DevTools (F12) → Network tab")
        print("4. Clear network log and refresh page")
        print("5. Look for requests with 'Authorization: Bearer eyJ...'")
        print("6. Copy the token and update .env:")
        print("   COOL_FARM_JWT_TOKEN=your_new_token")
        print("="*50)
    
    def get_soil_data(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Fetch soil characteristics for given coordinates
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            
        Returns:
            Dictionary containing soil data or None if failed
        """
        if not self.jwt_token:
            print("❌ No JWT token configured!")
            return None
        
        # Validate coordinates
        if not (-90 <= latitude <= 90):
            print(f"❌ Invalid latitude: {latitude} (must be between -90 and 90)")
            return None
        
        if not (-180 <= longitude <= 180):
            print(f"❌ Invalid longitude: {longitude} (must be between -180 and 180)")
            return None
        
        headers = self._get_headers()
        
        # Prepare soil data request payload
        soil_request = {
            "latitude": latitude,
            "longitude": longitude
        }
        
        try:
            print(f"🌍 Fetching soil data for coordinates: {latitude}, {longitude}")
            
            response = requests.post(
                f"{self.base_url}/soil-characteristic", 
                json=soil_request,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                soil_data = response.json()
                print("✅ Successfully retrieved soil data")
                
                # Display the soil information
                if 'ipccSoilClass' in soil_data:
                    print(f"   IPCC Soil Class: {soil_data['ipccSoilClass']}")
                
                if 'wrbSoilClass' in soil_data:
                    wrb_data = soil_data['wrbSoilClass']
                    print(f"   WRB Soil Class: {wrb_data.get('wrbSoilClassName', 'Unknown')}")
                    print(f"   Probability: {wrb_data.get('probability', 'Unknown')}")
                
                return soil_data
                
            elif response.status_code == 401:
                print("❌ JWT token expired or invalid!")
                self._show_token_instructions()
                return None
                
            elif response.status_code == 400:
                print("❌ Bad request - check your coordinates")
                try:
                    error_detail = response.json()
                    print(f"Error details: {json.dumps(error_detail, indent=2)}")
                except:
                    print(f"Error: {response.text}")
                return None
                
            else:
                print(f"❌ Unexpected error: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def create_enhanced_template(self, pathway: str = "Annuals v3", 
                            latitude: float = None, 
                            longitude: float = None,
                            output_file: str = None) -> Optional[Dict[str, Any]]:
        """
        Create an enhanced template with soil data automatically populated
        
        Args:
            pathway: Assessment pathway name
            latitude: Latitude for soil data lookup
            longitude: Longitude for soil data lookup
            output_file: Optional filename to save template
            
        Returns:
            Enhanced template dictionary
        """
        print(f"🔧 Creating enhanced template for {pathway}")
        
        # Get base template
        template = self.get_default_assessment_template(pathway)
        if not template:
            return None
        
        # If coordinates provided, fetch and integrate soil data
        if latitude is not None and longitude is not None:
            print(f"🌍 Fetching soil data for coordinates...")
            soil_data = self.get_soil_data(latitude, longitude)
            
            if soil_data:
                # Update farm details with coordinates
                if 'farmDetails' not in template:
                    template['farmDetails'] = {}
                
                template['farmDetails']['latitude'] = latitude
                template['farmDetails']['longitude'] = longitude
                
                # Map soil characteristics based on API response
                soil_char_mapping = {
                    'Sandy soils': 'Low activity clay',
                    'Clay soils': 'High activity clay', 
                    'Organic soils': 'Organic soils',
                    'Other soils': 'High activity clay'  # Default fallback
                }
                
                ipcc_soil_class = soil_data.get('ipccSoilClass', 'Other soils')
                mapped_soil_char = soil_char_mapping.get(ipcc_soil_class, 'High activity clay')
                
                template['farmDetails']['soilCharacteristic'] = mapped_soil_char
                
                print(f"✅ Updated template with soil data:")
                print(f"   IPCC Soil Class: {ipcc_soil_class}")
                print(f"   Mapped to soilCharacteristic: {mapped_soil_char}")
                
                # Optionally update crop details soil type as well
                if 'inputData' in template and 'cropDetails' in template['inputData']:
                    # Map IPCC soil class to Cool Farm soil types
                    soil_type_mapping = {
                        'Sandy soils': 'Coarse',
                        'Clay soils': 'Fine',
                        'Organic soils': 'Organic',
                        'Other soils': 'Medium'  # Default
                    }
                    
                    mapped_soil_type = soil_type_mapping.get(ipcc_soil_class, 'Medium')
                    template['inputData']['cropDetails']['soilType'] = mapped_soil_type
                    print(f"   Updated cropDetails.soilType: {mapped_soil_type}")
            else:
                print("⚠️ Could not fetch soil data, using template defaults")
        
        # Save enhanced template if requested
        if output_file:
            try:
                # Create templates directory if it doesn't exist
                templates_dir = "templates"
                os.makedirs(templates_dir, exist_ok=True)
                
                # If user specifies output file, check if it includes directory
                if os.path.dirname(output_file):
                    filename = output_file
                else:
                    filename = os.path.join(templates_dir, output_file)
                
                with open(filename, 'w') as f:
                    json.dump(template, f, indent=2)
                print(f"💾 Enhanced template saved to: {filename}")
                
            except Exception as e:
                print(f"❌ Failed to save template: {e}")
        
        return template
    
    def update_template_coordinates(self, template_file: str, 
                                  latitude: float, 
                                  longitude: float,
                                  output_file: str = None) -> bool:
        """
        Update an existing template file with new coordinates and soil data
        
        Args:
            template_file: Path to existing template JSON file
            latitude: New latitude
            longitude: New longitude 
            output_file: Optional output filename (defaults to overwriting input)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load existing template
            with open(template_file, 'r') as f:
                template = json.load(f)
            
            print(f"📁 Loaded template from: {template_file}")
            
            # Fetch new soil data
            soil_data = self.get_soil_data(latitude, longitude)
            if not soil_data:
                print("❌ Could not fetch soil data")
                return False
            
            # Update template with new data
            if 'farmDetails' not in template:
                template['farmDetails'] = {}
            
            template['farmDetails']['latitude'] = latitude
            template['farmDetails']['longitude'] = longitude
            
            # Update soil characteristics
            soil_char_mapping = {
                'Sandy soils': 'Low activity clay',
                'Clay soils': 'High activity clay',
                'Organic soils': 'Organic soils',
                'Other soils': 'High activity clay'
            }
            
            ipcc_soil_class = soil_data.get('ipccSoilClass', 'Other soils')
            mapped_soil_char = soil_char_mapping.get(ipcc_soil_class, 'High activity clay')
            template['farmDetails']['soilCharacteristic'] = mapped_soil_char
            
            # Update crop soil type
            if 'inputData' in template and 'cropDetails' in template['inputData']:
                soil_type_mapping = {
                    'Sandy soils': 'Coarse',
                    'Clay soils': 'Fine', 
                    'Organic soils': 'Organic',
                    'Other soils': 'Medium'
                }
                mapped_soil_type = soil_type_mapping.get(ipcc_soil_class, 'Medium')
                template['inputData']['cropDetails']['soilType'] = mapped_soil_type
            
            # Save updated template
            output_path = output_file or template_file
            with open(output_path, 'w') as f:
                json.dump(template, f, indent=2)
            
            print(f"✅ Updated template saved to: {output_path}")
            print(f"   New coordinates: {latitude}, {longitude}")
            print(f"   Soil characteristic: {mapped_soil_char}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating template: {e}")
            return False

    def test_token(self) -> bool:
        """Test if current token works with detailed debugging"""
        if not self.jwt_token:
            print("❌ No JWT token available")
            return False
        
        headers = self._get_headers()
        
        # Test with the calculate endpoint using a minimal POST request
        print(f"🔍 Testing POST to /assessment/calculate")
        
        # Use minimal test data that should work
        minimal_test_data = {
            "pathway": "Annuals v3",
            "inputData": {
                "cropDetails": {
                    "soilType": "Fine",
                    "assessmentYear": 2024,
                    "cropType": "Alfalfa",
                    "area": {
                        "value": 1,
                        "unit": "hectares"
                    },
                    "cropYield": {
                        "value": 1,
                        "unit": "tonnes"
                    },
                    "farmGate": {
                        "value": 1,
                        "unit": "tonnes"
                    }
                }
            },
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
            "farmIdentifier": "test_farm"
        }
        try:
            response = requests.post(
                f"{self.base_url}/assessment/calculate",
                json=minimal_test_data,
                headers=headers,
                timeout=30
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Token valid - assessment endpoint working")
                return True
            elif response.status_code == 401:
                print(f"❌ Token invalid - got 401 unauthorized")
                return False
            elif response.status_code == 400:
                print(f"🤔 Token valid but bad request data - got 400")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error text: {response.text[:200]}")
                return True  # Auth worked, just bad data
            else:
                print(f"🤔 Unexpected status {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return response.status_code != 401  # If not 401, auth probably worked
                
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout on assessment endpoint")
            return False
        except Exception as e:
            print(f"❌ Error testing endpoint: {e}")
            return False
        
    def fetch_schemas(self) -> bool:
        """Fetch and save schemas for all available pathways"""
        if not self.jwt_token:
            print("❌ No JWT token configured!")
            return False
        
        pathways = ["Annuals v3", "Perennials v3", "Potatoes v3", "Paddy Rice v3"]
        
        # Create schemas directory
        os.makedirs("schemas", exist_ok=True)
        
        success_count = 0
        for pathway in pathways:
            print(f"📥 Fetching schema for {pathway}...")
            schema = self.get_pathway_schema(pathway)
            
            if schema:
                # Create filename
                safe_pathway = pathway.replace(' ', '_').replace('/', '_').lower()
                filename = f"schemas/{safe_pathway}_schema.json"
                
                # Save schema
                try:
                    with open(filename, 'w') as f:
                        json.dump(schema, f, indent=2)
                    
                    print(f"💾 Saved schema to {filename}")
                    success_count += 1
                    
                except Exception as e:
                    print(f"❌ Error saving schema for {pathway}: {e}")
            else:
                print(f"⚠️ Could not fetch schema for {pathway}")
        
        if success_count > 0:
            print(f"\n✅ Successfully downloaded {success_count}/{len(pathways)} schemas")
            print("You can now use the interactive template builder!")
            return True
        else:
            print("❌ Failed to download any schemas")
            return False    
    def get_pathways(self) -> Optional[List[str]]:
        """Get available assessment pathways"""
        # Based on the documentation, these are the known pathways
        known_pathways = [
            "Annuals v3",
            "Perennials v3", 
            "Potatoes v3",
            "Paddy Rice v3"
        ]
        
        print("Known pathways from API documentation:")
        for pathway in known_pathways:
            print(f"  - {pathway}")
        
        return known_pathways
    
    def get_pathway_schema(self, pathway: str) -> Optional[Dict[str, Any]]:
        """Get schema for a specific pathway"""
        if not self.jwt_token:
            print("❌ No JWT token configured!")
            return None
        
        headers = self._get_headers()
        try:
            # URL encode the pathway name
            pathway_encoded = pathway.replace(' ', '%20')
            response = requests.get(
                f"{self.base_url}/assessment/pathway/{pathway_encoded}/schema",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                schema = response.json()
                print(f"✅ Successfully retrieved schema for {pathway}")
                return schema
            else:
                print(f"❌ Failed to get schema for {pathway}: {response.status_code}")
                if response.status_code == 404:
                    print("   Check if pathway name is correct and exists")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def calculate_assessment(self, assessment_data: Dict[str, Any], 
                        save_result: bool = True, 
                        output_file: str = None,
                        pathway_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Calculate assessment with comprehensive error handling
        
        Args:
            assessment_data: Assessment data dictionary
            save_result: Whether to save result to file
            output_file: Custom output filename
            pathway_name: Pathway name to include in filename
            
        Returns:
            Assessment result or None if failed
        """
        if not self.jwt_token:
            print("❌ No JWT token configured!")
            self._show_token_instructions()
            return None
        
        headers = self._get_headers()
        
        try:
            print("Calculating assessment...")
            
            response = requests.post(
                f"{self.base_url}/assessment/calculate",
                json=assessment_data,
                headers=headers,
                timeout=120  # Increased timeout for complex assessments
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Assessment successful!")
                
                if save_result:
                    # Create assessments directory if it doesn't exist
                    assessments_dir = "assessments"
                    os.makedirs(assessments_dir, exist_ok=True)
                    
                    if output_file:
                        # If user specifies output file, check if it includes directory
                        if os.path.dirname(output_file):
                            filename = output_file
                        else:
                            filename = os.path.join(assessments_dir, output_file)
                    else:
                        # Extract pathway from assessment data or use provided pathway_name
                        pathway = pathway_name or assessment_data.get('pathway', 'unknown_pathway')
                        # Create safe filename from pathway name
                        safe_pathway = pathway.replace(' ', '_').replace('/', '_').lower()
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = os.path.join(assessments_dir, f"assessment_{safe_pathway}_{timestamp}.json")
                    
                    with open(filename, 'w') as f:
                        json.dump(result, f, indent=2)
                    print(f"Result saved to: {filename}")
                
                return result
                
            elif response.status_code == 401:
                print("❌ JWT token expired or invalid!")
                self._show_token_instructions()
                return None
                
            elif response.status_code == 400:
                print("❌ Bad request - check your assessment data")
                try:
                    error_detail = response.json()
                    print(f"Error details: {json.dumps(error_detail, indent=2)}")
                except:
                    print(f"Error: {response.text}")
                return None
                
            else:
                print(f"❌ Unexpected error: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return None
                
        except requests.exceptions.Timeout:
            print("❌ Request timed out - Cool Farm API might be slow")
            return None
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None

    def load_assessment_from_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load assessment data from JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load assessment from {file_path}: {e}")
            return None
        
    def _get_builtin_template(self, pathway: str) -> Optional[Dict[str, Any]]:
        """Fallback method with built-in templates"""
        
        if pathway == "Annuals v3":
            return {
                "pathway": pathway,
                "inputData": {
                    "cropDetails": {
                        "soilType": "Fine",
                        "assessmentYear": 2024,
                        "sandPercentage": 4,
                        "cropType": "Alfalfa",
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
                },
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
                "farmIdentifier": "farm_01"
            }
        else:
            print(f"❌ No built-in template available for {pathway}")
            return None
        
    def get_default_assessment_template(self, pathway: str = "Annuals v3") -> Optional[Dict[str, Any]]:
        """Get default assessment template for specified pathway from JSON files"""
        
        # Map pathway names to template filenames
        template_files = {
            "Annuals v3": "templates/annuals_v3_template.json",
            "Perennials v3": "templates/perennials_v3_template.json", 
            "Paddy Rice v3": "templates/paddy_rice_v3_template.json",
            "Potatoes v3": "templates/potatoes_v3_template.json"
        }
        
        # Check if pathway exists
        if pathway not in template_files:
            print(f"⚠️ Unknown pathway: {pathway}. Available pathways: {list(template_files.keys())}")
            print("Defaulting to Annuals v3")
            pathway = "Annuals v3"
        
        template_file = template_files[pathway]
        
        try:
            # Try to load the template from file
            with open(template_file, 'r') as f:
                template = json.load(f)
            print(f"✅ Loaded template for {pathway} from {template_file}")
            return template
            
        except FileNotFoundError:
            print(f"❌ Template file not found: {template_file}")
            print("Creating template files from built-in data...")
            
            # Create the templates directory if it doesn't exist
            os.makedirs("templates", exist_ok=True)
            
            # Fall back to built-in template and save it
            template = self._get_builtin_template(pathway)
            if template:
                with open(template_file, 'w') as f:
                    json.dump(template, f, indent=2)
                print(f"Saved template to {template_file}")
                return template
            else:
                print(f"❌ No built-in template available for {pathway}")
                return None
                
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {template_file}: {e}")
            return None
        except Exception as e:
            print(f"❌ Error loading template from {template_file}: {e}")
            return None


def main():
    """Main function with enhanced command-line interface"""
    parser = argparse.ArgumentParser(description='Enhanced Cool Farm API Assessment Tool')
    parser.add_argument('--action', 
                    choices=['test', 'pathways', 'assess', 'template', 'soil-data', 
                            'enhance-template', 'update-coords', 'fetch-schemas'], 
                    default='assess', help='Action to perform')
    parser.add_argument('--pathway', default='Annuals v3', help='Assessment pathway')
    parser.add_argument('--input-file', help='Input JSON file for assessment')
    parser.add_argument('--output-file', help='Output filename for results')
    parser.add_argument('--env-file', default='.env', help='Environment file path')
    parser.add_argument('--latitude', type=float, help='Latitude for soil data lookup')
    parser.add_argument('--longitude', type=float, help='Longitude for soil data lookup')
    
    args = parser.parse_args()
    
    print("Enhanced Cool Farm API Client")
    print("="*40)
    
    # Initialize client
    client = CoolFarmAPIClient(env_file=args.env_file)
    
    if not client.jwt_token:
        print("❌ No JWT token found - exiting")
        sys.exit(1)
    
    # Test token first (except for soil-data which might work without assessment access)
    if args.action != 'soil-data':
        if not client.test_token():
            print("❌ JWT token is invalid or expired - exiting")
            sys.exit(1)
        print("✅ JWT token is working\n")
    
    # Perform requested action
    if args.action == 'test':
        print("✅ Token test passed!" if client.test_token() else "❌ Token test failed!")
        
    elif args.action == 'fetch-schemas':
        if not client.test_token():
            print("❌ JWT token is invalid - please refresh your token")
            sys.exit(1)
        success = client.fetch_schemas()
        if success:
            print("\n🎉 Schema download complete!")
            print("You can now run: python interactive_builder.py")  
        
    elif args.action == 'pathways':
        print("Available pathways:")
        pathways = client.get_pathways()
    
    elif args.action == 'soil-data':
        if args.latitude is None or args.longitude is None:
            print("❌ --latitude and --longitude are required for soil-data action")
            print("Example: --action soil-data --latitude 51.28 --longitude 0.52")
            sys.exit(1)
        
        soil_data = client.get_soil_data(args.latitude, args.longitude)
        if soil_data:
            print("\nFull soil data response:")
            print(json.dumps(soil_data, indent=2))
    
    elif args.action == 'enhance-template':
        if args.latitude is None or args.longitude is None:
            print("❌ --latitude and --longitude are required for enhance-template action")
            sys.exit(1)
        
        output_name = args.output_file or f"enhanced_{args.pathway.replace(' ', '_').lower()}_template.json"
        
        enhanced_template = client.create_enhanced_template(
            pathway=args.pathway,
            latitude=args.latitude,
            longitude=args.longitude,
            output_file=output_name
        )
        
        if enhanced_template:
            print("\n✅ Enhanced template created successfully!")
            print("You can now edit the template file and use it for assessments.")
    
    elif args.action == 'update-coords':
        if not args.input_file:
            print("❌ --input-file is required for update-coords action")
            sys.exit(1)
        
        if args.latitude is None or args.longitude is None:
            print("❌ --latitude and --longitude are required for update-coords action")
            sys.exit(1)
        
        success = client.update_template_coordinates(
            template_file=args.input_file,
            latitude=args.latitude,
            longitude=args.longitude,
            output_file=args.output_file
        )
        
        if success:
            print("✅ Template coordinates updated successfully!")
    
    elif args.action == 'assess':
        if args.input_file:
            print(f"Running assessment from file: {args.input_file}")
            assessment_data = client.load_assessment_from_file(args.input_file)
            if not assessment_data:
                sys.exit(1)
        else:
            print(f"Running assessment with template for pathway: {args.pathway}")
            assessment_data = client.get_default_assessment_template(args.pathway)
            if not assessment_data:
                print(f"❌ Could not load template for {args.pathway}")
                sys.exit(1)
        
        result = client.calculate_assessment(
            assessment_data, 
            save_result=True, 
            output_file=args.output_file
        )
        
        if result:
            print(f"\nAssessment completed successfully!")
            if isinstance(result, dict):
                print(f"Result contains {len(result)} top-level keys")
                for key in list(result.keys())[:5]:  # Show first 5 keys
                    print(f"  - {key}")
                if len(result) > 5:
                    print(f"  ... and {len(result) - 5} more")


if __name__ == "__main__":
    main()