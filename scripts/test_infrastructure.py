#!/usr/bin/env python3
"""
Infrastructure Testing Script for Sannetic Explorer
Tests Docker containers, database connectivity, API endpoints, and system health
"""

import requests
import psycopg2
import redis
import time
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class InfrastructureTester:
    def __init__(self):
        self.test_results = []
        self.db_port = int(os.getenv("HOST_TEST_POSTGRES_PORT", "15433"))
        self.redis_port = int(os.getenv("HOST_TEST_REDIS_PORT", "16380"))
        self.backend_port = int(os.getenv("HOST_TEST_BACKEND_PORT", "13801"))
        self.frontend_port = int(os.getenv("HOST_TEST_FRONTEND_PORT", "13301"))
        self.base_url = os.getenv("PUBLIC_TEST_API_URL", f"http://localhost:{self.backend_port}")
        self.frontend_url = os.getenv("TEST_FRONTEND_URL", f"http://localhost:{self.frontend_port}")
        self.db_config = {
            'host': 'localhost',
            'port': self.db_port,
            'database': 'sannetic_explorer_test',
            'user': 'postgres',
            'password': 'postgres'
        }
        self.redis_config = {
            'host': 'localhost',
            'port': self.redis_port,
            'db': 0
        }

    def log_test(self, test_name: str, success: bool, message: str = "", details: Any = None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   Details: {details}")

    def test_docker_containers(self) -> bool:
        """Test if Docker containers are running"""
        print("\n🐳 Testing Docker Containers...")
        
        try:
            # Test if containers are accessible via their ports
            containers = [
                ('test-db', self.db_port),
                ('test-redis', self.redis_port),
                ('test-backend', self.backend_port),
                ('test-frontend', self.frontend_port)
            ]
            
            all_running = True
            for container_name, port in containers:
                try:
                    if port == self.db_port:  # PostgreSQL
                        conn = psycopg2.connect(**self.db_config)
                        conn.close()
                        self.log_test(f"Container {container_name}", True, f"PostgreSQL accessible on port {port}")
                    elif port == self.redis_port:  # Redis
                        r = redis.Redis(**self.redis_config)
                        r.ping()
                        self.log_test(f"Container {container_name}", True, f"Redis accessible on port {port}")
                    else:  # HTTP services
                        response = requests.get(f"http://localhost:{port}", timeout=5)
                        self.log_test(f"Container {container_name}", True, f"HTTP service accessible on port {port}")
                except Exception as e:
                    self.log_test(f"Container {container_name}", False, f"Not accessible on port {port}", str(e))
                    all_running = False
            
            return all_running
        except Exception as e:
            self.log_test("Docker Containers", False, "Failed to test containers", str(e))
            return False

    def test_database_connectivity(self) -> bool:
        """Test database connectivity and basic operations"""
        print("\n🗄️ Testing Database Connectivity...")
        
        try:
            # Test connection
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            self.log_test("Database Connection", True, "Successfully connected to PostgreSQL", version)
            
            # Test if tables exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = [row[0] for row in cursor.fetchall()]
            self.log_test("Database Tables", True, f"Found {len(tables)} tables", tables)
            
            # Test if celestial_bodies table has data
            cursor.execute("SELECT COUNT(*) FROM celestial_bodies;")
            count = cursor.fetchone()[0]
            self.log_test("Data Availability", True, f"Found {count} celestial bodies")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            self.log_test("Database Connectivity", False, "Failed to connect to database", str(e))
            return False

    def test_redis_connectivity(self) -> bool:
        """Test Redis connectivity and basic operations"""
        print("\n🔴 Testing Redis Connectivity...")
        
        try:
            r = redis.Redis(**self.redis_config)
            
            # Test ping
            response = r.ping()
            self.log_test("Redis Ping", True, "Redis server is responding")
            
            # Test basic operations
            r.set("test_key", "test_value")
            value = r.get("test_key")
            r.delete("test_key")
            
            if value == b"test_value":
                self.log_test("Redis Operations", True, "Basic Redis operations working")
            else:
                self.log_test("Redis Operations", False, "Basic Redis operations failed")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Redis Connectivity", False, "Failed to connect to Redis", str(e))
            return False

    def test_api_endpoints(self) -> bool:
        """Test API endpoints"""
        print("\n🌐 Testing API Endpoints...")
        
        endpoints = [
            ("/health", "Health Check"),
            ("/stats", "System Statistics"),
            ("/bodies", "Celestial Bodies"),
            ("/bodies/planets", "Planets"),
            ("/bodies/moons", "Moons"),
            ("/bodies/stars", "Stars"),
            ("/updates/status", "Update Status"),
            ("/updates/latest", "Latest Updates")
        ]
        
        all_endpoints_working = True
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    self.log_test(f"API {name}", True, f"Endpoint {endpoint} responding")
                else:
                    self.log_test(f"API {name}", False, f"Endpoint {endpoint} returned {response.status_code}")
                    all_endpoints_working = False
            except Exception as e:
                self.log_test(f"API {name}", False, f"Endpoint {endpoint} failed", str(e))
                all_endpoints_working = False
        
        return all_endpoints_working

    def test_frontend_accessibility(self) -> bool:
        """Test frontend accessibility"""
        print("\n🎨 Testing Frontend Accessibility...")
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                self.log_test("Frontend", True, "Frontend is accessible")
                return True
            else:
                self.log_test("Frontend", False, f"Frontend returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend", False, "Frontend not accessible", str(e))
            return False

    def test_system_performance(self) -> bool:
        """Test system performance metrics"""
        print("\n⚡ Testing System Performance...")
        
        try:
            # Test API response time
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response_time = time.time() - start_time
            
            if response_time < 1.0:
                self.log_test("API Response Time", True, f"Response time: {response_time:.3f}s")
            else:
                self.log_test("API Response Time", False, f"Slow response time: {response_time:.3f}s")
            
            # Test database query performance
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            start_time = time.time()
            cursor.execute("SELECT COUNT(*) FROM celestial_bodies;")
            query_time = time.time() - start_time
            
            if query_time < 0.1:
                self.log_test("Database Query Time", True, f"Query time: {query_time:.3f}s")
            else:
                self.log_test("Database Query Time", False, f"Slow query time: {query_time:.3f}s")
            
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            self.log_test("System Performance", False, "Failed to test performance", str(e))
            return False

    def test_data_integrity(self) -> bool:
        """Test data integrity and consistency"""
        print("\n🔍 Testing Data Integrity...")
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Test data consistency
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_bodies,
                    COUNT(CASE WHEN name IS NOT NULL THEN 1 END) as bodies_with_names,
                    COUNT(CASE WHEN type IS NOT NULL THEN 1 END) as bodies_with_types
                FROM celestial_bodies;
            """)
            result = cursor.fetchone()
            
            total, with_names, with_types = result
            
            if total > 0 and with_names == total and with_types == total:
                self.log_test("Data Consistency", True, f"All {total} bodies have names and types")
            else:
                self.log_test("Data Consistency", False, f"Inconsistent data: {total} total, {with_names} with names, {with_types} with types")
            
            # Test referential integrity
            cursor.execute("""
                SELECT COUNT(*) 
                FROM celestial_bodies cb1
                LEFT JOIN celestial_bodies cb2 ON cb1.parent_id = cb2.id
                WHERE cb1.parent_id IS NOT NULL AND cb2.id IS NULL;
            """)
            orphan_count = cursor.fetchone()[0]
            
            if orphan_count == 0:
                self.log_test("Referential Integrity", True, "No orphaned records found")
            else:
                self.log_test("Referential Integrity", False, f"Found {orphan_count} orphaned records")
            
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            self.log_test("Data Integrity", False, "Failed to test data integrity", str(e))
            return False

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                'timestamp': datetime.now().isoformat()
            },
            'results': self.test_results,
            'recommendations': []
        }
        
        # Generate recommendations based on failures
        if failed_tests > 0:
            report['recommendations'].append("Review failed tests and fix issues")
        
        if any('performance' in result['test'].lower() and not result['success'] for result in self.test_results):
            report['recommendations'].append("Optimize system performance")
        
        if any('database' in result['test'].lower() and not result['success'] for result in self.test_results):
            report['recommendations'].append("Check database configuration and connectivity")
        
        return report

    def run_all_tests(self) -> bool:
        """Run all infrastructure tests"""
        print("🚀 Starting Sannetic Explorer Infrastructure Tests")
        print("=" * 60)
        
        tests = [
            self.test_docker_containers,
            self.test_database_connectivity,
            self.test_redis_connectivity,
            self.test_api_endpoints,
            self.test_frontend_accessibility,
            self.test_system_performance,
            self.test_data_integrity
        ]
        
        all_passed = True
        for test in tests:
            try:
                if not test():
                    all_passed = False
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {e}")
                all_passed = False
        
        # Generate and display report
        report = self.generate_report()
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Passed: {report['summary']['passed']}")
        print(f"Failed: {report['summary']['failed']}")
        print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        
        if report['recommendations']:
            print("\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
        
        # Save report to file
        with open('infrastructure_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: infrastructure_test_report.json")
        
        return all_passed

def main():
    """Main function"""
    tester = InfrastructureTester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 