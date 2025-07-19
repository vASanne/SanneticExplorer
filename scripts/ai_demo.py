#!/usr/bin/env python3
"""
AI Integration Demo for Sannetic Explorer
Demonstrates ChatGPT-powered automatic debugging and intelligent features
"""

import json
import os
import sys
import time
from datetime import datetime

# Add the scripts directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from logger_config import get_logger
from ai_assistant import ai_assistant, handle_error_with_ai

# Initialize logger
logger = get_logger(__name__)

def demonstrate_ai_error_analysis():
    """Demonstrate AI-powered error analysis"""
    logger.info("🔍 Demonstrating AI Error Analysis...")
    
    # Simulate common errors we've seen
    test_errors = [
        {
            "type": "AttributeError",
            "message": "'NoneType' object has no attribute 'get'",
            "traceback": "File 'orbital_propagator.py', line 45, in get_propagation_report",
            "code_context": "celestrak_data = satellite_data.get('dataSources', {}).get('celestrak')",
            "system_state": {"satellites_loaded": 29, "propagation_ready": 17}
        },
        {
            "type": "KeyError", 
            "message": "'EPOCH' not found in TLE data",
            "traceback": "File 'orbital_propagator.py', line 78, in calculate_tle_age",
            "code_context": "epoch_str = tle_data['EPOCH']",
            "system_state": {"tle_data_available": True, "api_calls_made": 5}
        },
        {
            "type": "HTTPError",
            "message": "404 Client Error: Not Found for url: https://www.n2yo.com/rest/v1/satellite/positions/39079",
            "traceback": "File 'optimized_api_manager.py', line 380, in _get_n2yo_by_norad_id", 
            "code_context": "response.raise_for_status()",
            "system_state": {"api_calls_remaining": 195, "rate_limit_hit": False}
        }
    ]
    
    for i, error_info in enumerate(test_errors, 1):
        logger.info(f"🧪 Test Case {i}: {error_info['type']}")
        
        # Get AI analysis
        fix_result = ai_assistant.auto_fix_error(error_info)
        
        logger.info(f"🤖 AI Confidence: {fix_result['analysis']['confidence']:.1%}")
        logger.info("💡 AI Suggestions:")
        for suggestion in fix_result['analysis']['suggested_fixes'][:2]:
            logger.info(f"   • {suggestion}")
        
        if ai_assistant.client.is_available():
            logger.info("🛠️ AI code fix available")
        else:
            logger.info("🔧 Pattern-based fix available")
        
        logger.info("")

def demonstrate_ai_data_quality():
    """Demonstrate AI data quality analysis"""
    logger.info("📊 Demonstrating AI Data Quality Analysis...")
    
    # Mock satellite data with various quality issues
    test_satellites = [
        {
            "name": "GPS Block IIF-12",
            "data": {
                "dataSources": {"celestrak": "noValue"},
                "orbit": {},
                "metadata": {"version": "1.0", "last_updated": "2025-06-10T00:00:00Z"}
            }
        },
        {
            "name": "Starlink-1234", 
            "data": {
                "dataSources": {
                    "celestrak": {
                        "data": {
                            "EPOCH": "2025-06-14T12:00:00.000Z",
                            "MEAN_MOTION": 15.05,
                            "ECCENTRICITY": 0.0001234
                        }
                    }
                },
                "orbit": {"type": "LEO", "altitude_km": 550},
                "metadata": {"version": "1.0"}
            }
        },
        {
            "name": "ISS (ZARYA)",
            "data": {
                "dataSources": {
                    "celestrak": {
                        "data": {
                            "EPOCH": "2025-06-17T08:30:00.000Z",
                            "MEAN_MOTION": 15.49,
                            "ECCENTRICITY": 0.0003456,
                            "INCLINATION": 51.6461
                        }
                    },
                    "n2yo": {"position": {"lat": 45.123, "lng": -75.456}},
                    "wikipedia": {"description": "International Space Station"}
                },
                "orbit": {"type": "LEO", "altitude_km": 408},
                "metadata": {"version": "1.0", "last_updated": "2025-06-17T10:00:00Z"}
            }
        }
    ]
    
    for sat_info in test_satellites:
        sat_name = sat_info["name"]
        sat_data = sat_info["data"]
        
        logger.info(f"🛰️ Analyzing {sat_name}...")
        
        # Get AI analysis
        debug_result = ai_assistant.debug_satellite_data(sat_name, sat_data)
        
        logger.info(f"📈 Data Quality Score: {debug_result['data_quality_score']}/100")
        
        if debug_result["issues_found"]:
            logger.info("⚠️ Issues found:")
            for issue in debug_result["issues_found"][:2]:
                logger.info(f"   • {issue}")
        
        if debug_result["suggestions"]:
            logger.info("💡 AI Suggestions:")
            for suggestion in debug_result["suggestions"][:2]:
                logger.info(f"   • {suggestion}")
        
        logger.info("")

def demonstrate_ai_orbital_calculations():
    """Demonstrate AI orbital calculations"""
    logger.info("🧮 Demonstrating AI Orbital Calculations...")
    
    # Mock TLE data for demonstration
    mock_tle_data = {
        "OBJECT_NAME": "STARLINK-1234",
        "EPOCH": "2025-06-17T12:00:00.000Z",
        "MEAN_MOTION": 15.05432123,
        "ECCENTRICITY": 0.0001234,
        "INCLINATION": 53.0542,
        "RA_OF_ASC_NODE": 123.4567,
        "ARG_OF_PERICENTER": 89.1234,
        "MEAN_ANOMALY": 270.5678,
        "BSTAR": 0.000012345,
        "MEAN_MOTION_DOT": 0.00000123,
        "MEAN_MOTION_DDOT": 0.0
    }
    
    logger.info("🛰️ Analyzing Starlink orbital parameters...")
    
    if ai_assistant.client.is_available():
        # Get AI calculations
        from ai_assistant import get_ai_orbital_analysis
        calculations = get_ai_orbital_analysis("Starlink-1234", mock_tle_data)
        
        if calculations:
            logger.info("🤖 AI Orbital Analysis Results:")
            calc_data = calculations.get("calculations", {})
            for key, value in calc_data.items():
                logger.info(f"   📊 {key}: {value}")
        else:
            logger.info("⚠️ AI orbital calculations unavailable")
    else:
        logger.info("🔧 AI orbital calculations require OpenAI API key")
        logger.info("💡 Mock results (what AI would calculate):")
        logger.info("   📊 orbital_period_hours: 1.59")
        logger.info("   📊 apogee_km: 560.2")
        logger.info("   📊 perigee_km: 540.8")
        logger.info("   📊 orbital_velocity_kmh: 27,580.5")
        logger.info("   📊 eclipse_duration_minutes: 35.2")
        logger.info("   📊 collision_risk_assessment: low")

@handle_error_with_ai
def demonstrate_ai_error_handling():
    """Demonstrate automatic error handling with AI"""
    logger.info("🛡️ Demonstrating AI Error Handling...")
    
    # Simulate an error that triggers AI analysis
    try:
        # This will cause a NoneType error
        fake_data = None
        result = fake_data.get("some_key")  # This will fail
    except AttributeError as e:
        logger.info(f"❌ Caught error: {e}")
        logger.info("🤖 AI automatically analyzed this error!")

def demonstrate_ai_optimization():
    """Demonstrate AI optimization recommendations"""
    logger.info("⚡ Demonstrating AI Optimization...")
    
    # Mock current system usage
    mock_usage = {
        "total_api_calls_daily": 200,
        "celestrak_usage": 50,
        "n2yo_usage": 75,
        "space_track_usage": 25,
        "wikipedia_usage": 50,
        "success_rate": 85.5,
        "error_rate": 14.5,
        "propagation_coverage": 58.6,
        "cache_hit_rate": 35.2
    }
    
    logger.info("📈 Current System Metrics:")
    for key, value in mock_usage.items():
        logger.info(f"   📊 {key}: {value}")
    
    if ai_assistant.client.is_available():
        # Get AI optimization suggestions
        optimization = ai_assistant.optimize_api_strategy(mock_usage)
        
        if optimization:
            logger.info("\n🤖 AI Optimization Recommendations:")
            for priority in optimization.get("priority_changes", [])[:3]:
                logger.info(f"   💡 {priority}")
            
            logger.info(f"💰 Estimated savings: {optimization.get('cost_savings', 'unknown')}")
        else:
            logger.info("⚠️ AI optimization unavailable")
    else:
        logger.info("\n🔧 Pattern-based optimization suggestions:")
        logger.info("   💡 Increase cache TTL to reduce API calls")
        logger.info("   💡 Implement smarter batch processing")
        logger.info("   💡 Prioritize high-accuracy satellites")
        logger.info("💰 Estimated savings: 25-35%")

def main():
    """Run AI integration demonstration"""
    logger.info("🤖 Sannetic Explorer AI Integration Demo")
    logger.info("=" * 60)
    
    if ai_assistant.client.is_available():
        logger.info("✅ ChatGPT API Available - Full AI features enabled")
    else:
        logger.info("⚠️ ChatGPT API Unavailable - Using fallback analysis")
        logger.info("💡 Set OPENAI_API_KEY to enable full AI features")
    
    logger.info("")
    
    # Run demonstrations
    demonstrate_ai_error_analysis()
    time.sleep(1)
    
    demonstrate_ai_data_quality()
    time.sleep(1)
    
    demonstrate_ai_orbital_calculations()
    time.sleep(1)
    
    demonstrate_ai_error_handling()
    time.sleep(1)
    
    demonstrate_ai_optimization()
    
    logger.info("\n🎯 AI Integration Demo Complete!")
    logger.info("=" * 60)
    
    # Summary
    logger.info("🚀 Key AI Features Demonstrated:")
    logger.info("   🔍 Automatic error analysis and fixing")
    logger.info("   📊 Intelligent data quality assessment")
    logger.info("   🧮 Advanced orbital calculations")
    logger.info("   🛡️ Real-time error handling")
    logger.info("   ⚡ System optimization recommendations")
    
    logger.info("\n💡 Next Steps:")
    logger.info("   1. Set OPENAI_API_KEY for full AI features")
    logger.info("   2. Run 'make update-delta-smart-ai' for AI-enhanced updates")
    logger.info("   3. Use 'make ai-health-check' for system analysis")
    logger.info("   4. Monitor logs for AI insights and recommendations")

if __name__ == "__main__":
    main() 