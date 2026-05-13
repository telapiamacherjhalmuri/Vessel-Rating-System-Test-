"""
API Usage Examples - Vessel Rating System REST API
Run the API server first: python api_server.py
Then run this script: python api_examples.py
"""

import requests
import json
import time

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# ==================== Colors for Output ====================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.END}\n")

def print_section(text):
    print(f"{Colors.CYAN}{text}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

# ==================== Example 1: Health Check ====================

def example_1_health_check():
    """Check API health status"""
    print_header("Example 1: Health Check")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        data = response.json()
        
        print(json.dumps(data, indent=2))
        print_success("API is healthy and operational")
        
    except Exception as e:
        print_error(f"Failed to check health: {str(e)}")

# ==================== Example 2: Single Vessel Analysis ====================

def example_2_single_analysis():
    """Analyze a single vessel"""
    print_header("Example 2: Single Vessel Analysis")
    
    vessel_data = {
        "vessel_name": "Ever Given",
        "imo_number": "9860910"
    }
    
    print_section(f"📍 Analyzing vessel: {vessel_data['vessel_name']} (IMO: {vessel_data['imo_number']})")
    
    try:
        response = requests.post(f"{API_BASE_URL}/analyze", json=vessel_data)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n{Colors.BOLD}ANALYSIS RESULTS:{Colors.END}")
            print(f"  Vessel Name: {data['vessel_name']}")
            print(f"  IMO Number: {data['imo_number']}")
            print(f"  Analysis Date: {data['analysis_date']}")
            print(f"  {Colors.YELLOW}Final Rating: {data['final_rating']}/9{Colors.END}")
            print(f"  {Colors.YELLOW}Band Rating: {data['band_rating']}{Colors.END}")
            print(f"  {Colors.YELLOW}Risk Level: {data['risk_level']}{Colors.END}")
            print(f"  Processing Time: {data['processing_time_seconds']}s")
            
            print(f"\n{Colors.BOLD}MODULE SCORES:{Colors.END}")
            for module in data['module_scores']:
                print(f"  • {module['module_name']}: {module['score']}/10 (Weight: {module['weight']}%)")
            
            if data['critical_alerts']:
                print(f"\n{Colors.RED}{Colors.BOLD}CRITICAL ALERTS:{Colors.END}")
                for alert in data['critical_alerts']:
                    print(f"  ⚠️  {alert}")
            
            print(f"\n{Colors.BOLD}RECOMMENDATION:{Colors.END}")
            print(f"  {data['recommendation']}")
            
            print_success("Analysis completed successfully")
        else:
            print_error(f"API returned status {response.status_code}: {response.text}")
    
    except Exception as e:
        print_error(f"Analysis failed: {str(e)}")

# ==================== Example 3: Batch Analysis ====================

def example_3_batch_analysis():
    """Analyze multiple vessels at once"""
    print_header("Example 3: Batch Analysis (Multiple Vessels)")
    
    vessels_data = {
        "vessels": [
            {"vessel_name": "Ever Given", "imo_number": "9860910"},
            {"vessel_name": "MSC Zoe", "imo_number": "7904881"},
            {"vessel_name": "OOCL Hong Kong", "imo_number": "9711519"}
        ]
    }
    
    print_section(f"📍 Analyzing {len(vessels_data['vessels'])} vessels")
    
    try:
        response = requests.post(f"{API_BASE_URL}/batch-analyze", json=vessels_data)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n{Colors.BOLD}BATCH ANALYSIS SUMMARY:{Colors.END}")
            print(f"  Total Vessels: {data['total_vessels']}")
            print(f"  Successful: {Colors.GREEN}{data['successful']}{Colors.END}")
            print(f"  Failed: {Colors.RED if data['failed'] > 0 else Colors.GREEN}{data['failed']}{Colors.END}")
            print(f"  Processing Time: {data['processing_time_seconds']}s")
            
            print(f"\n{Colors.BOLD}SUMMARY STATISTICS:{Colors.END}")
            summary = data['summary']
            print(f"  Average Rating: {summary['average_rating']}/9")
            print(f"  {Colors.RED}Critical Risk: {summary['high_risk_count']}{Colors.END}")
            print(f"  {Colors.YELLOW}High Risk: {summary['medium_risk_count']}{Colors.END}")
            print(f"  {Colors.GREEN}Low Risk: {summary['low_risk_count']}{Colors.END}")
            
            print(f"\n{Colors.BOLD}INDIVIDUAL RESULTS:{Colors.END}")
            for result in data['results']:
                print(f"  • {result['vessel_name']} (IMO: {result['imo_number']})")
                print(f"    Rating: {result['final_rating']}/9 | Risk: {result['risk_level']}")
            
            print_success("Batch analysis completed successfully")
        else:
            print_error(f"API returned status {response.status_code}: {response.text}")
    
    except Exception as e:
        print_error(f"Batch analysis failed: {str(e)}")

# ==================== Example 4: Get Modules Info ====================

def example_4_modules_info():
    """Get information about all scoring modules"""
    print_header("Example 4: Scoring Modules Information")
    
    try:
        response = requests.get(f"{API_BASE_URL}/modules")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"{Colors.BOLD}AVAILABLE MODULES:{Colors.END}")
            for module in data['modules']:
                print(f"\n  {module['id']}. {module['name']} ({module['weight']}% weight)")
                print(f"     Description: {module['description']}")
                print(f"     Factors: {', '.join(module['factors'])}")
            
            print(f"\n{Colors.BOLD}RATING SCALE:{Colors.END}")
            scale = data['rating_scale']
            print(f"  Type: {scale['type']}")
            print(f"  Range: {scale['min']} - {scale['max']}")
            for risk in scale['risk_levels']:
                print(f"    • {risk}")
            
            print_success("Module information retrieved successfully")
        else:
            print_error(f"API returned status {response.status_code}")
    
    except Exception as e:
        print_error(f"Failed to retrieve module information: {str(e)}")

# ==================== Example 5: Get Statistics ====================

def example_5_statistics():
    """Get system statistics"""
    print_header("Example 5: System Statistics")
    
    try:
        response = requests.get(f"{API_BASE_URL}/stats")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"{Colors.BOLD}SYSTEM STATISTICS:{Colors.END}")
            print(f"  Total Vessels Analyzed: {data['total_vessels_analyzed']}")
            print(f"  Total Analyses: {data['total_analyses']}")
            print(f"  Average Rating: {data['average_rating']}/9")
            
            print(f"\n{Colors.BOLD}RISK DISTRIBUTION:{Colors.END}")
            dist = data['risk_distribution']
            print(f"  {Colors.RED}Critical: {dist['critical']}{Colors.END}")
            print(f"  {Colors.YELLOW}High: {dist['high']}{Colors.END}")
            print(f"  {Colors.YELLOW}Medium: {dist['medium']}{Colors.END}")
            print(f"  {Colors.GREEN}Low: {dist['low']}{Colors.END}")
            print(f"  {Colors.GREEN}Minimal: {dist['minimal']}{Colors.END}")
            
            if data['last_analysis']:
                print(f"\n  Last Analysis: {data['last_analysis']}")
            
            print_success("Statistics retrieved successfully")
        else:
            print_error(f"API returned status {response.status_code}")
    
    except Exception as e:
        print_error(f"Failed to retrieve statistics: {str(e)}")

# ==================== Example 6: Vessel History ====================

def example_6_vessel_history():
    """Get analysis history for a specific vessel"""
    print_header("Example 6: Vessel Analysis History")
    
    imo_number = "9860910"
    print_section(f"📍 Getting history for vessel IMO: {imo_number}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/history/{imo_number}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n{Colors.BOLD}VESSEL INFORMATION:{Colors.END}")
            print(f"  Name: {data['vessel_name']}")
            print(f"  IMO: {data['imo_number']}")
            print(f"  Total Analyses: {data['total_analyses']}")
            print(f"  Latest Rating: {data['latest_rating']}/9")
            print(f"  Latest Analysis: {data['latest_analysis_date']}")
            
            if data['ratings_history']:
                print(f"\n{Colors.BOLD}RATING HISTORY:{Colors.END}")
                for entry in data['ratings_history'][-5:]:  # Show last 5
                    print(f"  • {entry['date']}: {entry['rating']}/9 (Band: {entry['band']}, Risk: {entry['risk_level']})")
            
            print_success("History retrieved successfully")
        elif response.status_code == 404:
            print_error("Vessel not found in history")
        else:
            print_error(f"API returned status {response.status_code}")
    
    except Exception as e:
        print_error(f"Failed to retrieve history: {str(e)}")

# ==================== Example 7: Error Handling ====================

def example_7_error_handling():
    """Demonstrate error handling"""
    print_header("Example 7: Error Handling")
    
    print_section("Testing invalid input (missing IMO):")
    
    vessel_data = {
        "vessel_name": "Test Vessel"
        # Missing imo_number - will cause validation error
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/analyze", json=vessel_data)
        
        if response.status_code != 200:
            error_data = response.json()
            print_error(f"Status: {response.status_code}")
            print(json.dumps(error_data, indent=2))
        else:
            print_success("Request succeeded")
    
    except Exception as e:
        print_error(f"Request failed: {str(e)}")

# ==================== Run All Examples ====================

def run_all_examples():
    """Run all example functions"""
    print("\n" + "="*60)
    print(f"{Colors.BOLD}{Colors.CYAN}🚢 VESSEL RATING SYSTEM - API EXAMPLES{Colors.END}")
    print("="*60)
    
    print(f"\n{Colors.YELLOW}Make sure the API server is running: python api_server.py{Colors.END}")
    print(f"{Colors.YELLOW}Then access the interactive docs at: http://localhost:8000/docs{Colors.END}\n")
    
    time.sleep(2)
    
    examples = [
        ("1", "Health Check", example_1_health_check),
        ("2", "Single Vessel Analysis", example_2_single_analysis),
        ("3", "Batch Analysis", example_3_batch_analysis),
        ("4", "Modules Information", example_4_modules_info),
        ("5", "System Statistics", example_5_statistics),
        ("6", "Vessel History", example_6_vessel_history),
        ("7", "Error Handling", example_7_error_handling),
    ]
    
    while True:
        print(f"\n{Colors.BOLD}{Colors.CYAN}Select an example to run:{Colors.END}")
        for num, name, _ in examples:
            print(f"  {num}. {name}")
        print("  0. Run all examples")
        print("  q. Quit")
        
        choice = input(f"\n{Colors.BOLD}Enter your choice: {Colors.END}").strip().lower()
        
        if choice == 'q':
            print(f"\n{Colors.GREEN}✓ Thank you for using the API examples!{Colors.END}\n")
            break
        elif choice == '0':
            for _, _, func in examples:
                try:
                    func()
                    time.sleep(1)
                except Exception as e:
                    print_error(f"Example failed: {str(e)}")
        else:
            for num, _, func in examples:
                if choice == num:
                    try:
                        func()
                    except Exception as e:
                        print_error(f"Example failed: {str(e)}")
                    break

if __name__ == "__main__":
    run_all_examples()
