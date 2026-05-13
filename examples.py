"""
Example Usage Scripts for Vessel Rating System

Demonstrates programmatic usage of the system without the web UI.
"""

from api_integration import get_api_integration
from scoring_engine import get_scoring_engine
from utils import (
    print_console_report, 
    save_report_to_file, 
    export_summary_csv,
    format_json_report
)
import json


def example_1_simple_analysis():
    """Example 1: Simple vessel analysis and display"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Simple Vessel Analysis")
    print("="*70 + "\n")
    
    # Initialize
    api = get_api_integration()
    engine = get_scoring_engine()
    
    # Fetch data
    vessel_data = api.fetch_all_vessel_data("Meghna Pearl", "9894765")
    
    # Generate report
    report = engine.generate_report("Meghna Pearl", "9894765", vessel_data)
    
    # Display
    print_console_report(report)
    
    return report


def example_2_batch_analysis():
    """Example 2: Analyze multiple vessels"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Batch Vessel Analysis")
    print("="*70 + "\n")
    
    vessels = [
        ("Meghna Pearl", "9894765"),
        ("Global Leader", "9876543"),
        ("Test Vessel 1", "1234567"),
    ]
    
    api = get_api_integration()
    engine = get_scoring_engine()
    
    reports = []
    
    for vessel_name, imo in vessels:
        print(f"Analyzing {vessel_name} (IMO: {imo})...")
        
        vessel_data = api.fetch_all_vessel_data(vessel_name, imo)
        report = engine.generate_report(vessel_name, imo, vessel_data)
        reports.append(report)
        
        # Quick summary
        band = report["scoring"]["final_band"]
        classification = report["scoring"]["classification"]
        print(f"  ✓ Band: {band:.1f}/9.0 - {classification.upper()}\n")
    
    # Print comparison
    print("\n" + "-"*70)
    print("COMPARISON SUMMARY")
    print("-"*70)
    for report in reports:
        name = report["vessel_info"]["vessel_name"]
        band = report["scoring"]["final_band"]
        emoji = report["scoring"]["emoji_indicator"]
        risk = report["scoring"]["risk_level"]
        print(f"{emoji} {name:20} Band: {band:.1f}/9.0 - {risk}")
    
    return reports


def example_3_export_reports():
    """Example 3: Generate and export reports"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Export Reports (JSON and CSV)")
    print("="*70 + "\n")
    
    api = get_api_integration()
    engine = get_scoring_engine()
    
    vessel_data = api.fetch_all_vessel_data("Meghna Pearl", "9894765")
    report = engine.generate_report("Meghna Pearl", "9894765", vessel_data)
    
    # Save JSON
    json_file = save_report_to_file(report)
    print(f"✓ JSON report saved: {json_file}")
    
    # Save CSV
    csv_file = export_summary_csv(report)
    print(f"✓ CSV summary saved: {csv_file}")
    
    return json_file, csv_file


def example_4_risk_analysis():
    """Example 4: Detailed risk analysis"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Detailed Risk Analysis")
    print("="*70 + "\n")
    
    api = get_api_integration()
    engine = get_scoring_engine()
    
    vessel_data = api.fetch_all_vessel_data("Meghna Pearl", "9894765")
    report = engine.generate_report("Meghna Pearl", "9894765", vessel_data)
    
    print("DETAILED RISK ASSESSMENT\n")
    
    # Module analysis
    print("Module Scores & Contributions:")
    print("-" * 70)
    for module in report["module_breakdown"]:
        print(f"{module['emoji']} {module['module']}")
        print(f"   Score: {module['score']:.1f}/100")
        print(f"   Band:  {module['band']:.1f}/9.0")
        print(f"   Weight: {module['weight_percent']}%")
        print(f"   Contribution: {module['weighted_contribution']:.2f}")
        print()
    
    # Alerts
    print("\nRisk Alerts:")
    print("-" * 70)
    alerts = report["alerts"]
    if alerts:
        for alert in alerts:
            print(f"{alert['emoji']} [{alert['severity']}] {alert['message']}")
    else:
        print("✅ No critical alerts")
    
    # Override status
    print("\nCritical Override Status:")
    print("-" * 70)
    if report["scoring"]["override_applied"]:
        print(f"⚠️  Override Applied: {report['scoring']['override_reason']}")
        print(f"   Final Band: {report['scoring']['final_band']:.1f}/9.0")
    else:
        print("✅ No overrides applied - normal scoring used")
    
    return report


def example_5_vessel_comparison():
    """Example 5: Compare two vessels"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Vessel Comparison")
    print("="*70 + "\n")
    
    vessel1 = ("Meghna Pearl", "9894765")
    vessel2 = ("Global Leader", "9876543")
    
    api = get_api_integration()
    engine = get_scoring_engine()
    
    # Analyze both
    data1 = api.fetch_all_vessel_data(vessel1[0], vessel1[1])
    report1 = engine.generate_report(vessel1[0], vessel1[1], data1)
    
    data2 = api.fetch_all_vessel_data(vessel2[0], vessel2[1])
    report2 = engine.generate_report(vessel2[0], vessel2[1], data2)
    
    # Compare
    print("VESSEL COMPARISON")
    print("-" * 70)
    print(f"{'Metric':<30} {'Vessel 1':<20} {'Vessel 2':<20}")
    print("-" * 70)
    
    print(f"{'Vessel Name':<30} {vessel1[0]:<20} {vessel2[0]:<20}")
    print(f"{'IMO Number':<30} {vessel1[1]:<20} {vessel2[1]:<20}")
    print(f"{'Final Score':<30} {report1['scoring']['final_score']:<20.1f} {report2['scoring']['final_score']:<20.1f}")
    print(f"{'Band Rating':<30} {report1['scoring']['final_band']:<20.1f} {report2['scoring']['final_band']:<20.1f}")
    print(f"{'Classification':<30} {report1['scoring']['classification']:<20} {report2['scoring']['classification']:<20}")
    print(f"{'Risk Level':<30} {report1['scoring']['risk_level']:<20} {report2['scoring']['risk_level']:<20}")
    
    print("\n" + "-" * 70)
    print("Module Score Comparison:")
    print("-" * 70)
    
    for i, (mod1, mod2) in enumerate(zip(report1["module_breakdown"], report2["module_breakdown"])):
        print(f"\n{mod1['module']}:")
        print(f"  Vessel 1: {mod1['score']:.1f}/100 (Band: {mod1['band']:.1f})")
        print(f"  Vessel 2: {mod2['score']:.1f}/100 (Band: {mod2['band']:.1f})")
        difference = mod1['score'] - mod2['score']
        if difference > 0:
            print(f"  Δ: +{difference:.1f} (Vessel 2 lower risk)")
        elif difference < 0:
            print(f"  Δ: {difference:.1f} (Vessel 1 lower risk)")
        else:
            print(f"  Δ: Same")
    
    return report1, report2


def example_6_json_output():
    """Example 6: Working with JSON output"""
    print("\n" + "="*70)
    print("EXAMPLE 6: JSON Output Handling")
    print("="*70 + "\n")
    
    api = get_api_integration()
    engine = get_scoring_engine()
    
    vessel_data = api.fetch_all_vessel_data("Meghna Pearl", "9894765")
    report = engine.generate_report("Meghna Pearl", "9894765", vessel_data)
    
    # Pretty JSON
    json_str = format_json_report(report)
    
    # Print (truncated for demo)
    print("Report JSON Structure (partial):")
    print("-" * 70)
    json_obj = json.loads(json_str)
    print(json.dumps({
        "vessel_info": json_obj["vessel_info"],
        "scoring": json_obj["scoring"],
        "alerts_count": len(json_obj["alerts"]),
        "modules_count": len(json_obj["module_breakdown"])
    }, indent=2))
    
    return report


def run_all_examples():
    """Run all examples"""
    print("\n" + "="*70)
    print("VESSEL RATING SYSTEM - USAGE EXAMPLES")
    print("="*70)
    
    try:
        example_1_simple_analysis()
        example_2_batch_analysis()
        example_3_export_reports()
        example_4_risk_analysis()
        example_5_vessel_comparison()
        example_6_json_output()
        
        print("\n" + "="*70)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        if example_num == "1":
            example_1_simple_analysis()
        elif example_num == "2":
            example_2_batch_analysis()
        elif example_num == "3":
            example_3_export_reports()
        elif example_num == "4":
            example_4_risk_analysis()
        elif example_num == "5":
            example_5_vessel_comparison()
        elif example_num == "6":
            example_6_json_output()
        else:
            print(f"Unknown example: {example_num}")
            print("Usage: python examples.py [1-6]")
    else:
        run_all_examples()
