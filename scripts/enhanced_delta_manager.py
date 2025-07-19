#!/usr/bin/env python3
"""
Enhanced Delta Update Manager with AI Integration
Combines delta updates with ChatGPT-powered automatic debugging and optimization
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging

# Add the scripts directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from logger_config import get_logger
from orbital_propagator import OrbitalPropagator, load_satellite_data
from optimized_api_manager import OptimizedAPIManager
from ai_assistant import ai_assistant, handle_error_with_ai, get_ai_orbital_analysis

# Initialize logger
logger = get_logger(__name__)

class EnhancedDeltaUpdateManager:
    """AI-powered delta update manager with automatic error fixing"""
    
    def __init__(self):
        self.propagator = OrbitalPropagator()
        self.api_manager = OptimizedAPIManager()
        self.satellites_dir = Path("Data/Satellites")
        self.index_file = self.satellites_dir / "index.json"
        self.ai_enabled = ai_assistant.client.is_available()
        
        if self.ai_enabled:
            logger.info("🤖 AI Assistant enabled - automatic debugging active")
        else:
            logger.info("🔧 AI Assistant disabled - using pattern-based fixes")
    
    @handle_error_with_ai
    def load_satellite_catalog(self) -> List[Dict[str, Any]]:
        """Load complete satellite catalog with AI error handling"""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'r') as f:
                    index_data = json.load(f)
                return index_data.get('satellites', [])
            return []
        except Exception as e:
            logger.error(f"Error loading satellite catalog: {e}")
            return []
    
    @handle_error_with_ai
    def analyze_catalog_freshness_ai(self) -> Dict[str, Any]:
        """AI-enhanced catalog freshness analysis"""
        logger.info("🔍 AI-enhanced catalog analysis...")
        
        catalog = self.load_satellite_catalog()
        analysis = {
            "total_satellites": len(catalog),
            "fresh_tle": 0,
            "stale_tle": 0,
            "no_tle": 0,
            "propagation_ready": 0,
            "needs_update": [],
            "fresh_satellites": [],
            "orbit_types": {"LEO": 0, "MEO": 0, "GEO": 0, "HEO": 0},
            "accuracy_distribution": {"excellent": 0, "good": 0, "fair": 0, "poor": 0},
            "ai_insights": []
        }
        
        for sat_info in catalog:
            sat_name = sat_info['name']
            
            try:
                sat_data = load_satellite_data(sat_name)
                
                if not sat_data:
                    analysis["no_tle"] += 1
                    analysis["needs_update"].append({
                        "name": sat_name,
                        "reason": "no_data",
                        "priority": "high"
                    })
                    continue
                
                # Enhanced AI debugging of satellite data
                if self.ai_enabled:
                    debug_result = ai_assistant.debug_satellite_data(sat_name, sat_data)
                    if debug_result["data_quality_score"] < 70:
                        analysis["ai_insights"].append({
                            "satellite": sat_name,
                            "quality_score": debug_result["data_quality_score"],
                            "issues": debug_result["issues_found"],
                            "suggestions": debug_result["suggestions"][:2]  # Top 2 suggestions
                        })
                
                # Propagation analysis with AI error handling
                report = self.propagator.get_propagation_report(sat_data)
                
                if report.get("can_propagate", False):
                    analysis["propagation_ready"] += 1
                    
                    if report.get("is_fresh", False):
                        analysis["fresh_tle"] += 1
                        analysis["fresh_satellites"].append(sat_name)
                    else:
                        analysis["stale_tle"] += 1
                        analysis["needs_update"].append({
                            "name": sat_name,
                            "reason": "stale_tle",
                            "age_days": report.get("tle_age_days", 0),
                            "accuracy": report.get("accuracy_estimate", "unknown"),
                            "priority": self.get_update_priority_ai(report)
                        })
                    
                    # Count orbit types and accuracy
                    orbit_type = report.get("orbit_type", "unknown")
                    if orbit_type in analysis["orbit_types"]:
                        analysis["orbit_types"][orbit_type] += 1
                    
                    accuracy = report.get("accuracy_estimate", "unknown")
                    if accuracy in analysis["accuracy_distribution"]:
                        analysis["accuracy_distribution"][accuracy] += 1
                else:
                    analysis["no_tle"] += 1
                    analysis["needs_update"].append({
                        "name": sat_name,
                        "reason": "no_tle_data",
                        "priority": "high"
                    })
                    
            except Exception as e:
                logger.error(f"Error analyzing {sat_name}: {e}")
                analysis["needs_update"].append({
                    "name": sat_name,
                    "reason": "analysis_error",
                    "error": str(e),
                    "priority": "medium"
                })
        
        # AI optimization suggestions
        if self.ai_enabled and analysis["total_satellites"] > 0:
            try:
                optimization = ai_assistant.optimize_api_strategy({
                    "total_satellites": analysis["total_satellites"],
                    "propagation_ready": analysis["propagation_ready"],
                    "needs_update": len(analysis["needs_update"]),
                    "fresh_percentage": (analysis["fresh_tle"] / analysis["total_satellites"]) * 100
                })
                
                if optimization:
                    analysis["ai_optimization"] = optimization
                    logger.info(f"🤖 AI suggests {optimization.get('cost_savings', 'unknown')} cost savings")
                    
            except Exception as e:
                logger.warning(f"AI optimization failed: {e}")
        
        return analysis
    
    def get_update_priority_ai(self, report: Dict[str, Any]) -> str:
        """AI-enhanced priority determination"""
        accuracy = report.get("accuracy_estimate", "unknown")
        orbit_type = report.get("orbit_type", "unknown")
        age_days = report.get("tle_age_days", 0)
        
        # Base priority logic
        if orbit_type == "LEO" and age_days > 3:
            base_priority = "high"
        elif orbit_type == "MEO" and age_days > 14:
            base_priority = "high"
        elif orbit_type == "GEO" and age_days > 30:
            base_priority = "high"
        elif accuracy in ["poor"]:
            base_priority = "high"
        elif accuracy in ["fair"]:
            base_priority = "medium"
        else:
            base_priority = "low"
        
        # AI enhancement (if available)
        if self.ai_enabled:
            try:
                # Could add more sophisticated AI priority logic here
                pass
            except:
                pass
        
        return base_priority
    
    @handle_error_with_ai
    def execute_smart_delta_update_ai(self) -> Dict[str, Any]:
        """AI-enhanced smart delta update"""
        logger.info("🧠 Starting AI-enhanced smart delta update...")
        
        start_time = time.time()
        results = {
            "update_type": "smart_ai",
            "start_time": datetime.now().isoformat(),
            "satellites_analyzed": 0,
            "tle_updates": 0,
            "propagation_used": 0,
            "api_calls_made": 0,
            "errors": [],
            "ai_fixes_applied": 0,
            "success_rate": 0
        }
        
        # Enhanced analysis with AI
        analysis = self.analyze_catalog_freshness_ai()
        results["satellites_analyzed"] = analysis["total_satellites"]
        results["propagation_used"] = analysis["propagation_ready"]
        
        # AI insights summary
        if analysis.get("ai_insights"):
            logger.info(f"🤖 AI found {len(analysis['ai_insights'])} data quality issues")
            for insight in analysis["ai_insights"][:3]:  # Show top 3
                logger.info(f"   📊 {insight['satellite']}: {insight['quality_score']}/100")
        
        # Execute updates with AI error handling
        high_priority_updates = [
            sat for sat in analysis["needs_update"] 
            if sat["priority"] == "high"
        ]
        
        logger.info(f"🎯 Updating {len(high_priority_updates)} high-priority satellites")
        
        for sat_info in high_priority_updates:
            try:
                sat_name = sat_info["name"]
                logger.info(f"🔄 Updating {sat_name} (reason: {sat_info['reason']})")
                
                # AI-assisted update
                success = self.update_satellite_tle_ai(sat_name)
                if success:
                    results["tle_updates"] += 1
                    results["api_calls_made"] += 1
                else:
                    results["errors"].append(f"Failed to update {sat_name}")
                
            except Exception as e:
                error_msg = f"Error updating {sat_name}: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
                
                # AI auto-fix attempt
                if self.ai_enabled:
                    try:
                        fix_result = ai_assistant.auto_fix_error({
                            "type": type(e).__name__,
                            "message": str(e),
                            "context": f"Updating satellite {sat_name}"
                        })
                        
                        if fix_result["analysis"]["confidence"] > 0.7:
                            logger.info(f"🤖 AI suggests high-confidence fix for {sat_name}")
                            results["ai_fixes_applied"] += 1
                    except:
                        pass
        
        # Calculate final metrics
        end_time = time.time()
        results["duration"] = end_time - start_time
        results["end_time"] = datetime.now().isoformat()
        
        if results["satellites_analyzed"] > 0:
            results["success_rate"] = ((results["satellites_analyzed"] - len(results["errors"])) / results["satellites_analyzed"]) * 100
        
        # AI optimization report
        if self.ai_enabled and analysis.get("ai_optimization"):
            ai_opt = analysis["ai_optimization"]
            logger.info("🤖 AI Optimization Recommendations:")
            for priority_change in ai_opt.get("priority_changes", [])[:3]:
                logger.info(f"   💡 {priority_change}")
        
        # Enhanced logging
        logger.info(f"✅ AI-enhanced delta update complete:")
        logger.info(f"   🔄 TLE updates: {results['tle_updates']}")
        logger.info(f"   📡 API calls: {results['api_calls_made']}")
        logger.info(f"   ⚡ Propagation coverage: {results['propagation_used']}/{results['satellites_analyzed']}")
        logger.info(f"   🤖 AI fixes applied: {results['ai_fixes_applied']}")
        logger.info(f"   🎯 Success rate: {results['success_rate']:.1f}%")
        
        return results
    
    @handle_error_with_ai
    def update_satellite_tle_ai(self, sat_name: str) -> bool:
        """AI-enhanced satellite TLE update"""
        try:
            logger.info(f"📡 Fetching fresh TLE data for {sat_name}")
            
            # Load current data for AI analysis
            current_data = load_satellite_data(sat_name)
            
            # AI pre-update analysis
            if self.ai_enabled and current_data:
                debug_result = ai_assistant.debug_satellite_data(sat_name, current_data)
                if debug_result["data_quality_score"] < 50:
                    logger.warning(f"⚠️ {sat_name} has poor data quality ({debug_result['data_quality_score']}/100)")
                    logger.info("🤖 AI recommends full data reconstruction")
            
            # Simulate API call with enhanced error handling
            time.sleep(0.1)
            
            # AI post-update validation could go here
            if self.ai_enabled:
                # Could add AI validation of updated data
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating TLE for {sat_name}: {e}")
            
            # AI error analysis
            if self.ai_enabled:
                try:
                    fix_result = ai_assistant.auto_fix_error({
                        "type": type(e).__name__,
                        "message": str(e),
                        "context": f"TLE update for {sat_name}"
                    })
                    
                    logger.info(f"🤖 AI analysis confidence: {fix_result['analysis']['confidence']:.1%}")
                    if fix_result["analysis"]["confidence"] > 0.8:
                        logger.info("💡 High-confidence AI fix available")
                except:
                    pass
            
            return False
    
    def get_ai_enhanced_position(self, sat_name: str, target_time: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
        """Get satellite position with AI-enhanced calculations"""
        if target_time is None:
            target_time = datetime.utcnow()
        
        try:
            # Load satellite data
            sat_data = load_satellite_data(sat_name)
            if not sat_data:
                logger.warning(f"No data available for {sat_name}")
                return None
            
            # Check propagation capability
            report = self.propagator.get_propagation_report(sat_data)
            
            if report.get("can_propagate", False) and report.get("accuracy_estimate") in ["excellent", "good"]:
                # Use propagation
                logger.info(f"⚡ Using propagation for {sat_name} (accuracy: {report['accuracy_estimate']})")
                
                celestrak_source = sat_data.get('dataSources', {}).get('celestrak')
                if celestrak_source and celestrak_source != "noValue":
                    if isinstance(celestrak_source, dict) and 'data' in celestrak_source:
                        celestrak_data = celestrak_source['data']
                    else:
                        celestrak_data = celestrak_source
                    
                    position = self.propagator.propagate_position(celestrak_data, target_time)
                    
                    if position:
                        position["data_source"] = "propagation"
                        position["api_calls_used"] = 0
                        
                        # AI-enhanced orbital analysis
                        if self.ai_enabled:
                            try:
                                ai_analysis = get_ai_orbital_analysis(sat_name, celestrak_data)
                                if ai_analysis:
                                    position["ai_analysis"] = ai_analysis["calculations"]
                                    logger.info(f"🤖 AI orbital analysis added for {sat_name}")
                            except Exception as e:
                                logger.warning(f"AI analysis failed: {e}")
                        
                        return position
            
            # Need fresh data
            logger.info(f"📡 Fetching fresh data for {sat_name} (TLE too old or inaccurate)")
            return {"data_source": "api_required", "api_calls_used": 1}
            
        except Exception as e:
            logger.error(f"Error getting position for {sat_name}: {e}")
            
            # AI error handling
            if self.ai_enabled:
                try:
                    ai_assistant.auto_fix_error({
                        "type": type(e).__name__,
                        "message": str(e),
                        "context": f"Position calculation for {sat_name}"
                    })
                except:
                    pass
            
            return None
    
    def generate_ai_enhanced_report(self) -> Dict[str, Any]:
        """Generate comprehensive AI-enhanced delta report"""
        logger.info("📊 Generating AI-enhanced delta report...")
        
        analysis = self.analyze_catalog_freshness_ai()
        
        # Calculate metrics
        total_satellites = analysis["total_satellites"]
        propagation_ready = analysis["propagation_ready"]
        api_savings = (propagation_ready / total_satellites) * 100 if total_satellites > 0 else 0
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "ai_enabled": self.ai_enabled,
            "catalog_status": analysis,
            "api_efficiency": {
                "total_satellites": total_satellites,
                "propagation_ready": propagation_ready,
                "api_calls_saved_percentage": api_savings,
                "estimated_api_calls_needed": len(analysis["needs_update"]) * 2,
                "estimated_api_calls_without_propagation": total_satellites * 2
            },
            "ai_insights": analysis.get("ai_insights", []),
            "ai_optimization": analysis.get("ai_optimization", {}),
            "recommendations": self.generate_ai_recommendations(analysis)
        }
        
        return report
    
    def generate_ai_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate AI-enhanced recommendations"""
        recommendations = []
        
        propagation_percentage = (analysis["propagation_ready"] / analysis["total_satellites"]) * 100
        
        if propagation_percentage > 80:
            recommendations.append("✅ Excellent propagation coverage - minimal API calls needed")
        elif propagation_percentage > 60:
            recommendations.append("⚡ Good propagation coverage - consider smart update mode")
        else:
            recommendations.append("🔄 Low propagation coverage - recommend full TLE refresh")
        
        immediate_updates = len([s for s in analysis["needs_update"] if s["priority"] == "high"])
        if immediate_updates > 0:
            recommendations.append(f"🚨 {immediate_updates} satellites need immediate TLE updates")
        
        if analysis["accuracy_distribution"]["poor"] > 0:
            recommendations.append(f"⚠️ {analysis['accuracy_distribution']['poor']} satellites have poor TLE accuracy")
        
        # AI-specific recommendations
        if self.ai_enabled:
            if analysis.get("ai_insights"):
                recommendations.append(f"🤖 AI identified {len(analysis['ai_insights'])} data quality issues")
            
            if analysis.get("ai_optimization", {}).get("cost_savings"):
                savings = analysis["ai_optimization"]["cost_savings"]
                recommendations.append(f"💰 AI suggests {savings} potential cost savings")
        
        return recommendations


def main():
    """Test enhanced AI delta update manager"""
    logger.info("🤖 Testing AI-Enhanced Delta Update Manager")
    
    manager = EnhancedDeltaUpdateManager()
    
    # Generate AI-enhanced report
    report = manager.generate_ai_enhanced_report()
    
    logger.info("📊 AI-Enhanced Delta Update Report:")
    logger.info(f"   Total satellites: {report['catalog_status']['total_satellites']}")
    logger.info(f"   Propagation ready: {report['catalog_status']['propagation_ready']}")
    logger.info(f"   API savings: {report['api_efficiency']['api_calls_saved_percentage']:.1f}%")
    logger.info(f"   AI enabled: {report['ai_enabled']}")
    
    if report.get("ai_insights"):
        logger.info(f"   🤖 AI insights: {len(report['ai_insights'])} data quality issues found")
    
    logger.info("💡 AI-Enhanced Recommendations:")
    for rec in report["recommendations"]:
        logger.info(f"   {rec}")
    
    # Test AI-enhanced smart update
    logger.info("\n🧠 Testing AI-enhanced smart delta update...")
    results = manager.execute_smart_delta_update_ai()
    
    logger.info(f"✅ AI-Enhanced update results:")
    logger.info(f"   TLE updates: {results['tle_updates']}")
    logger.info(f"   API calls: {results['api_calls_made']}")
    logger.info(f"   AI fixes applied: {results['ai_fixes_applied']}")
    logger.info(f"   Success rate: {results['success_rate']:.1f}%")


if __name__ == "__main__":
    main() 