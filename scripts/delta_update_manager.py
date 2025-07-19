#!/usr/bin/env python3
"""
Delta Update Manager for Sannetic Explorer
Intelligently manages TLE updates vs orbital propagation
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging

from logger_config import get_logger
from orbital_propagator import OrbitalPropagator, load_satellite_data
from optimized_api_manager import OptimizedAPIManager

# Initialize logger
logger = get_logger(__name__)

class DeltaUpdateManager:
    """Manages intelligent delta updates with orbital propagation"""
    
    def __init__(self):
        self.propagator = OrbitalPropagator()
        self.api_manager = OptimizedAPIManager()
        self.satellites_dir = Path("Data/Satellites")
        self.index_file = self.satellites_dir / "index.json"
        
    def load_satellite_catalog(self) -> List[Dict[str, Any]]:
        """Load complete satellite catalog"""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'r') as f:
                    index_data = json.load(f)
                return index_data.get('satellites', [])
            return []
        except Exception as e:
            logger.error(f"Error loading satellite catalog: {e}")
            return []
    
    def analyze_catalog_freshness(self) -> Dict[str, Any]:
        """Analyze TLE freshness across entire catalog"""
        logger.info("🔍 Analyzing catalog TLE freshness...")
        
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
            "accuracy_distribution": {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
        }
        
        for sat_info in catalog:
            sat_name = sat_info['name']
            sat_data = load_satellite_data(sat_name)
            
            if not sat_data:
                analysis["no_tle"] += 1
                analysis["needs_update"].append({
                    "name": sat_name,
                    "reason": "no_data",
                    "priority": "high"
                })
                continue
            
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
                        "priority": self.get_update_priority(report)
                    })
                
                # Count orbit types
                orbit_type = report.get("orbit_type", "unknown")
                if orbit_type in analysis["orbit_types"]:
                    analysis["orbit_types"][orbit_type] += 1
                
                # Count accuracy distribution
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
        
        return analysis
    
    def get_update_priority(self, report: Dict[str, Any]) -> str:
        """Determine update priority based on propagation report"""
        accuracy = report.get("accuracy_estimate", "unknown")
        orbit_type = report.get("orbit_type", "unknown")
        age_days = report.get("tle_age_days", 0)
        
        # Critical satellites always high priority
        if orbit_type == "LEO" and age_days > 3:
            return "high"
        elif orbit_type == "MEO" and age_days > 14:
            return "high"
        elif orbit_type == "GEO" and age_days > 30:
            return "high"
        elif accuracy in ["poor"]:
            return "high"
        elif accuracy in ["fair"]:
            return "medium"
        else:
            return "low"
    
    def create_update_plan(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create intelligent update plan based on analysis"""
        logger.info("📋 Creating delta update plan...")
        
        needs_update = analysis["needs_update"]
        
        # Prioritize updates
        high_priority = [sat for sat in needs_update if sat["priority"] == "high"]
        medium_priority = [sat for sat in needs_update if sat["priority"] == "medium"]
        low_priority = [sat for sat in needs_update if sat["priority"] == "low"]
        
        # Calculate API call estimates
        high_api_calls = len(high_priority) * 2  # Celestrak + Space-Track
        medium_api_calls = len(medium_priority) * 1  # Celestrak only
        low_api_calls = len(low_priority) * 1  # Celestrak only
        
        plan = {
            "total_satellites": analysis["total_satellites"],
            "propagation_ready": analysis["propagation_ready"],
            "immediate_updates": high_priority,
            "scheduled_updates": medium_priority,
            "deferred_updates": low_priority,
            "api_calls_estimate": {
                "immediate": high_api_calls,
                "scheduled": medium_api_calls,
                "deferred": low_api_calls,
                "total": high_api_calls + medium_api_calls + low_api_calls
            },
            "propagation_coverage": {
                "can_propagate": analysis["propagation_ready"],
                "percentage": (analysis["propagation_ready"] / analysis["total_satellites"]) * 100 if analysis["total_satellites"] > 0 else 0
            }
        }
        
        return plan
    
    def execute_delta_update(self, update_type: str = "smart") -> Dict[str, Any]:
        """Execute delta update based on type"""
        logger.info(f"🚀 Starting delta update: {update_type}")
        
        start_time = time.time()
        results = {
            "update_type": update_type,
            "start_time": datetime.now().isoformat(),
            "satellites_analyzed": 0,
            "tle_updates": 0,
            "propagation_used": 0,
            "api_calls_made": 0,
            "errors": [],
            "success_rate": 0
        }
        
        # Analyze current state
        analysis = self.analyze_catalog_freshness()
        plan = self.create_update_plan(analysis)
        
        logger.info(f"📊 Analysis complete: {analysis['propagation_ready']}/{analysis['total_satellites']} satellites ready for propagation")
        
        results["satellites_analyzed"] = analysis["total_satellites"]
        results["propagation_used"] = analysis["propagation_ready"]
        
        # Execute based on update type
        if update_type == "smart":
            results.update(self.execute_smart_update(plan))
        elif update_type == "critical":
            results.update(self.execute_critical_update(plan))
        elif update_type == "full":
            results.update(self.execute_full_update(plan))
        elif update_type == "discovery":
            results.update(self.execute_discovery_update())
        
        # Calculate final metrics
        end_time = time.time()
        results["duration"] = end_time - start_time
        results["end_time"] = datetime.now().isoformat()
        
        if results["satellites_analyzed"] > 0:
            results["success_rate"] = ((results["satellites_analyzed"] - len(results["errors"])) / results["satellites_analyzed"]) * 100
        
        # Log summary
        logger.info(f"✅ Delta update complete: {results['tle_updates']} updates, {results['api_calls_made']} API calls")
        logger.info(f"⚡ Propagation coverage: {results['propagation_used']}/{results['satellites_analyzed']} satellites")
        logger.info(f"🎯 Success rate: {results['success_rate']:.1f}%")
        
        return results
    
    def execute_smart_update(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute smart update - only update what's necessary"""
        logger.info("🧠 Executing smart delta update...")
        
        results = {"tle_updates": 0, "api_calls_made": 0, "errors": []}
        
        # Update only high priority satellites
        immediate_updates = plan["immediate_updates"]
        
        logger.info(f"🎯 Updating {len(immediate_updates)} high-priority satellites")
        
        for sat_info in immediate_updates:
            try:
                sat_name = sat_info["name"]
                logger.info(f"🔄 Updating {sat_name} (reason: {sat_info['reason']})")
                
                # Update TLE data
                success = self.update_satellite_tle(sat_name)
                if success:
                    results["tle_updates"] += 1
                    results["api_calls_made"] += 1  # Estimate
                else:
                    results["errors"].append(f"Failed to update {sat_name}")
                
            except Exception as e:
                logger.error(f"Error updating {sat_name}: {e}")
                results["errors"].append(f"Error updating {sat_name}: {str(e)}")
        
        return results
    
    def execute_critical_update(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute critical update - update mission-critical satellites"""
        logger.info("🚨 Executing critical delta update...")
        
        critical_satellites = [
            "International Space Station",
            "Hubble",
            "Starlink",
            "GPS",
            "Aqua/Terra"
        ]
        
        results = {"tle_updates": 0, "api_calls_made": 0, "errors": []}
        
        for sat_name in critical_satellites:
            try:
                logger.info(f"🔄 Updating critical satellite: {sat_name}")
                
                success = self.update_satellite_tle(sat_name)
                if success:
                    results["tle_updates"] += 1
                    results["api_calls_made"] += 1
                else:
                    results["errors"].append(f"Failed to update {sat_name}")
                
            except Exception as e:
                logger.error(f"Error updating {sat_name}: {e}")
                results["errors"].append(f"Error updating {sat_name}: {str(e)}")
        
        return results
    
    def execute_full_update(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute full update - update all satellites"""
        logger.info("🌍 Executing full delta update...")
        
        results = {"tle_updates": 0, "api_calls_made": 0, "errors": []}
        
        all_updates = plan["immediate_updates"] + plan["scheduled_updates"] + plan["deferred_updates"]
        
        logger.info(f"🔄 Updating {len(all_updates)} satellites")
        
        for sat_info in all_updates:
            try:
                sat_name = sat_info["name"]
                logger.info(f"🔄 Updating {sat_name}")
                
                success = self.update_satellite_tle(sat_name)
                if success:
                    results["tle_updates"] += 1
                    results["api_calls_made"] += 1
                else:
                    results["errors"].append(f"Failed to update {sat_name}")
                
            except Exception as e:
                logger.error(f"Error updating {sat_name}: {e}")
                results["errors"].append(f"Error updating {sat_name}: {str(e)}")
        
        return results
    
    def execute_discovery_update(self) -> Dict[str, Any]:
        """Execute discovery update - find new satellites"""
        logger.info("🔍 Executing discovery update...")
        
        results = {"tle_updates": 0, "api_calls_made": 0, "errors": [], "new_discoveries": []}
        
        # This would implement new satellite discovery
        # For now, return placeholder results
        logger.info("🆕 Discovery update not yet implemented")
        
        return results
    
    def update_satellite_tle(self, sat_name: str) -> bool:
        """Update TLE data for specific satellite"""
        try:
            # This would call the API manager to update TLE data
            # For now, simulate success
            logger.info(f"📡 Fetching fresh TLE data for {sat_name}")
            
            # Simulate API call delay
            time.sleep(0.1)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating TLE for {sat_name}: {e}")
            return False
    
    def get_real_time_position(self, sat_name: str, target_time: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
        """Get real-time position using propagation or fresh data"""
        if target_time is None:
            target_time = datetime.utcnow()
        
        try:
            # Load satellite data
            sat_data = load_satellite_data(sat_name)
            if not sat_data:
                logger.warning(f"No data available for {sat_name}")
                return None
            
            # Check if we can use propagation
            report = self.propagator.get_propagation_report(sat_data)
            
            if report.get("can_propagate", False) and report.get("accuracy_estimate") in ["excellent", "good"]:
                # Use propagation - no API call needed
                logger.info(f"⚡ Using propagation for {sat_name} (accuracy: {report['accuracy_estimate']})")
                
                celestrak_data = sat_data.get('dataSources', {}).get('celestrak')
                position = self.propagator.propagate_position(celestrak_data, target_time)
                
                if position:
                    position["data_source"] = "propagation"
                    position["api_calls_used"] = 0
                    return position
            
            # Need fresh data - use API
            logger.info(f"📡 Fetching fresh data for {sat_name} (TLE too old or inaccurate)")
            
            # This would fetch fresh data via API
            # For now, return None to indicate API call needed
            return {"data_source": "api_required", "api_calls_used": 1}
            
        except Exception as e:
            logger.error(f"Error getting position for {sat_name}: {e}")
            return None
    
    def generate_delta_report(self) -> Dict[str, Any]:
        """Generate comprehensive delta update report"""
        logger.info("📊 Generating delta update report...")
        
        analysis = self.analyze_catalog_freshness()
        plan = self.create_update_plan(analysis)
        
        # Calculate API savings
        total_satellites = analysis["total_satellites"]
        propagation_ready = analysis["propagation_ready"]
        api_savings = (propagation_ready / total_satellites) * 100 if total_satellites > 0 else 0
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "catalog_status": analysis,
            "update_plan": plan,
            "api_efficiency": {
                "total_satellites": total_satellites,
                "propagation_ready": propagation_ready,
                "api_calls_saved_percentage": api_savings,
                "estimated_api_calls_needed": plan["api_calls_estimate"]["total"],
                "estimated_api_calls_without_propagation": total_satellites * 2
            },
            "recommendations": self.generate_recommendations(analysis, plan)
        }
        
        return report
    
    def generate_recommendations(self, analysis: Dict[str, Any], plan: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        propagation_percentage = (analysis["propagation_ready"] / analysis["total_satellites"]) * 100
        
        if propagation_percentage > 80:
            recommendations.append("✅ Excellent propagation coverage - minimal API calls needed")
        elif propagation_percentage > 60:
            recommendations.append("⚡ Good propagation coverage - consider smart update mode")
        else:
            recommendations.append("🔄 Low propagation coverage - recommend full TLE refresh")
        
        immediate_updates = len(plan["immediate_updates"])
        if immediate_updates > 0:
            recommendations.append(f"🚨 {immediate_updates} satellites need immediate TLE updates")
        
        if analysis["accuracy_distribution"]["poor"] > 0:
            recommendations.append(f"⚠️ {analysis['accuracy_distribution']['poor']} satellites have poor TLE accuracy")
        
        return recommendations


def main():
    """Test delta update manager"""
    logger.info("🛰️ Testing Delta Update Manager")
    
    manager = DeltaUpdateManager()
    
    # Generate comprehensive report
    report = manager.generate_delta_report()
    
    logger.info("📊 Delta Update Report:")
    logger.info(f"   Total satellites: {report['catalog_status']['total_satellites']}")
    logger.info(f"   Propagation ready: {report['catalog_status']['propagation_ready']}")
    logger.info(f"   API savings: {report['api_efficiency']['api_calls_saved_percentage']:.1f}%")
    logger.info(f"   Estimated API calls needed: {report['api_efficiency']['estimated_api_calls_needed']}")
    
    logger.info("💡 Recommendations:")
    for rec in report["recommendations"]:
        logger.info(f"   {rec}")
    
    # Test smart update
    logger.info("\n🧠 Testing smart delta update...")
    results = manager.execute_delta_update("smart")
    
    logger.info(f"✅ Smart update results:")
    logger.info(f"   TLE updates: {results['tle_updates']}")
    logger.info(f"   API calls: {results['api_calls_made']}")
    logger.info(f"   Success rate: {results['success_rate']:.1f}%")


if __name__ == "__main__":
    main() 