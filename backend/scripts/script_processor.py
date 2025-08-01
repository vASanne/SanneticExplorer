#!/usr/bin/env python3
"""
Script Processor for Worker Container
Monitors Redis queue and executes triggered scripts
"""

import os
import sys
import json
import time
import logging
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Add the parent directory to the path so we can import our models
sys.path.append(str(Path(__file__).parent.parent.parent))

import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import UpdateLog, Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ScriptProcessor:
    def __init__(self):
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/sannetic_explorer")
        
        # Initialize Redis connection
        self.redis_client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            db=0,
            decode_responses=True
        )
        
        # Initialize database connection
        self.engine = create_engine(self.db_url)
        self.Session = sessionmaker(bind=self.engine)
        
        # Script mapping
        self.script_paths = {
            # "update_critical.py": "/app/scripts/update_critical.py",  # Removed - script deleted
            # "update_data_optimized.py": "/app/scripts/update_data_optimized.py",  # Removed - script deleted
            # "enhanced_delta_manager.py": "/app/scripts/enhanced_delta_manager.py",  # Removed - script deleted
            # "ai_health_check.py": "/app/scripts/ai_health_check.py",  # Removed - script deleted
            "sync.py": "/app/backend/scripts/sync.py"
        }
    
    def log_script_start(self, script_name: str, job_id: str) -> None:
        """Log script start to database"""
        try:
            session = self.Session()
            log_entry = UpdateLog(
                timestamp=datetime.now(),
                script_name=script_name,
                status="info",
                message=f"Script {script_name} started via API trigger (job_id: {job_id})",
                duration_sec=None,
                log_level="INFO",
                source_file="api_trigger"
            )
            session.add(log_entry)
            session.commit()
            session.close()
            logger.info(f"Logged script start: {script_name}")
        except Exception as e:
            logger.error(f"Failed to log script start: {e}")
    
    def log_script_end(self, script_name: str, job_id: str, success: bool, duration: float, message: str = None) -> None:
        """Log script completion to database"""
        try:
            session = self.Session()
            status = "success" if success else "error"
            log_message = f"Script {script_name} completed via API trigger (job_id: {job_id})"
            if message:
                log_message += f" - {message}"
            
            log_entry = UpdateLog(
                timestamp=datetime.now(),
                script_name=script_name,
                status=status,
                message=log_message,
                duration_sec=duration,
                log_level="INFO" if success else "ERROR",
                source_file="api_trigger"
            )
            session.add(log_entry)
            session.commit()
            session.close()
            logger.info(f"Logged script end: {script_name} - {status}")
        except Exception as e:
            logger.error(f"Failed to log script end: {e}")
    
    def execute_script(self, script_name: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a script with given parameters"""
        start_time = datetime.now()
        job_id = f"script_{script_name}_{int(start_time.timestamp())}"
        
        # Log script start
        self.log_script_start(script_name, job_id)
        
        try:
            # Get script path
            script_path = self.script_paths.get(script_name)
            if not script_path or not os.path.exists(script_path):
                raise FileNotFoundError(f"Script not found: {script_name}")
            
            # Build command
            cmd = ["python", script_path]
            
            # Add parameters if provided
            if parameters:
                for key, value in parameters.items():
                    if isinstance(value, bool):
                        if value:
                            cmd.append(f"--{key}")
                    else:
                        cmd.extend([f"--{key}", str(value)])
            
            logger.info(f"Executing command: {' '.join(cmd)}")
            
            # Execute script
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd="/app",
                timeout=3600  # 1 hour timeout
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Check if script succeeded
            success = result.returncode == 0
            message = result.stdout.strip() if success else result.stderr.strip()
            
            # Log script completion
            self.log_script_end(script_name, job_id, success, duration, message)
            
            return {
                "job_id": job_id,
                "script_name": script_name,
                "success": success,
                "duration_sec": duration,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "message": message
            }
            
        except subprocess.TimeoutExpired:
            duration = (datetime.now() - start_time).total_seconds()
            self.log_script_end(script_name, job_id, False, duration, "Script timed out after 1 hour")
            return {
                "job_id": job_id,
                "script_name": script_name,
                "success": False,
                "duration_sec": duration,
                "return_code": -1,
                "stdout": "",
                "stderr": "Script timed out after 1 hour",
                "message": "Script timed out after 1 hour"
            }
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_msg = f"Failed to execute script: {str(e)}"
            self.log_script_end(script_name, job_id, False, duration, error_msg)
            return {
                "job_id": job_id,
                "script_name": script_name,
                "success": False,
                "duration_sec": duration,
                "return_code": -1,
                "stdout": "",
                "stderr": error_msg,
                "message": error_msg
            }
    
    def process_queue(self):
        """Process jobs from Redis queue"""
        logger.info("Starting script processor...")
        
        while True:
            try:
                # Wait for job from queue (blocking)
                job_data = self.redis_client.brpop("script_queue", timeout=1)
                
                if job_data:
                    # Parse job data
                    queue_name, job_json = job_data
                    job = json.loads(job_json)
                    
                    script_name = job.get("script_name")
                    parameters = job.get("parameters", {})
                    
                    logger.info(f"Processing job: {script_name} with parameters: {parameters}")
                    
                    # Execute script
                    result = self.execute_script(script_name, parameters)
                    
                    if result["success"]:
                        logger.info(f"Script {script_name} completed successfully in {result['duration_sec']:.2f}s")
                    else:
                        logger.error(f"Script {script_name} failed: {result['message']}")
                
                time.sleep(0.1)  # Small delay to prevent busy waiting
                
            except KeyboardInterrupt:
                logger.info("Script processor stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in script processor: {e}")
                time.sleep(5)  # Wait before retrying

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process script execution queue')
    parser.add_argument('--test', help='Test script execution')
    parser.add_argument('--parameters', help='Script parameters as JSON')
    
    args = parser.parse_args()
    
    processor = ScriptProcessor()
    
    if args.test:
        # Test mode - execute a single script
        parameters = {}
        if args.parameters:
            try:
                parameters = json.loads(args.parameters)
            except json.JSONDecodeError:
                logger.error("Invalid JSON parameters")
                return
        
        result = processor.execute_script(args.test, parameters)
        print(json.dumps(result, indent=2, default=str))
    else:
        # Normal mode - process queue
        processor.process_queue()

if __name__ == "__main__":
    main() 