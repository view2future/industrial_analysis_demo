#!/usr/bin/env python3
"""
Integration Test for Regional Industrial Dashboard Application

This test performs end-to-end testing of the main application features:
1. File upload and processing
2. Text analysis
3. Dashboard generation
4. API endpoints
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import application modules
from scripts.industry_analysis import app
from src.analysis.text_processor import TextProcessor
from src.visualization.dashboard_generator import DashboardGenerator


class IntegrationTests(unittest.TestCase):
    """Integration tests for the regional industrial dashboard."""

    def setUp(self):
        """Set up test environment."""
        self.app = app.test_client()
        self.app.testing = True
        
        # Sample test content
        self.sample_text = """
        区域产业发展分析报告
        
        产业概述：
        人工智能产业是当前最具发展潜力的战略性新兴产业之一。近年来，随着大数据、云计算等技术的快速发展，
        人工智能在各个领域的应用不断深化，形成了良好的发展态势。
        
        政策环境：
        国家出台了一系列支持人工智能发展的政策措施，包括《新一代人工智能发展规划》等重要文件，
        为产业发展提供了强有力的政策保障。
        
        市场规模：
        据统计，2025年中国人工智能市场规模达到5000亿元人民币，预计未来五年年均增长率将保持在25%以上。
        """

    def test_complete_workflow_txt(self):
        """Test complete workflow with TXT file."""
        print("\n🔄 Testing complete workflow with TXT file...")
        
        # Step 1: Test file processing
        processor = TextProcessor()
        
        # Create a temporary TXT file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(self.sample_text)
            temp_file_path = f.name
        
        try:
            # Process the file
            analysis_result = processor.analyze_file(temp_file_path)
            self.assertIsNotNone(analysis_result, "File processing should return result")
            self.assertIn('categories', analysis_result, "Result should contain categories")
            
            # Step 2: Test dashboard generation
            generator = DashboardGenerator()
            dashboard_data = generator.generate_dashboard_data(analysis_result)
            self.assertIsNotNone(dashboard_data, "Dashboard generation should return data")
            self.assertIn('title', dashboard_data, "Dashboard should have title")
            self.assertIn('summary', dashboard_data, "Dashboard should have summary")
            self.assertIn('charts', dashboard_data, "Dashboard should have charts")
            
            # Step 3: Test that categories were properly processed
            categories = analysis_result['categories']
            found_categories = [cat for cat in categories if categories[cat]['content']]
            self.assertGreater(len(found_categories), 0, "Should find content in at least one category")
            
            print("✅ Complete TXT workflow test passed")
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)

    def test_api_endpoints(self):
        """Test main API endpoints."""
        print("\n🔌 Testing main API endpoints...")
        
        # Test home page
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200, "Home page should be accessible")
        
        # Test upload page
        response = self.app.get('/upload')
        self.assertEqual(response.status_code, 200, "Upload page should be accessible")
        
        # Test settings page
        response = self.app.get('/settings')
        self.assertEqual(response.status_code, 200, "Settings page should be accessible")
        
        # Test config API
        response = self.app.get('/api/config')
        self.assertEqual(response.status_code, 200, "Config API should be accessible")
        self.assertIn('application/json', response.content_type, "Config API should return JSON")
        
        print("✅ API endpoints test passed")

    def test_file_type_handling(self):
        """Test handling of different file types."""
        print("\n📁 Testing file type handling...")
        
        processor = TextProcessor()
        
        # Test TXT file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(self.sample_text)
            txt_file_path = f.name
        
        # Test MD file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(self.sample_text)
            md_file_path = f.name
        
        # Test JSON file
        json_content = {"content": self.sample_text, "title": "测试报告"}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(json_content, f, ensure_ascii=False, indent=2)
            json_file_path = f.name
        
        try:
            # Process TXT file
            txt_result = processor.analyze_file(txt_file_path)
            self.assertIsNotNone(txt_result, "TXT file processing should work")
            
            # Process MD file
            md_result = processor.analyze_file(md_file_path)
            self.assertIsNotNone(md_result, "MD file processing should work")
            
            # Process JSON file
            json_result = processor.analyze_file(json_file_path)
            self.assertIsNotNone(json_result, "JSON file processing should work")
            
            print("✅ File type handling test passed")
            
        finally:
            # Clean up temporary files
            for file_path in [txt_file_path, md_file_path, json_file_path]:
                os.unlink(file_path)

    def test_error_handling(self):
        """Test error handling scenarios."""
        print("\n🛡️  Testing error handling...")
        
        processor = TextProcessor()
        generator = DashboardGenerator()
        
        # Test processing non-existent file
        result = processor.analyze_file("/non/existent/file.txt")
        self.assertIsNone(result, "Should return None for non-existent file")
        
        # Test dashboard generation with empty data
        empty_result = generator.generate_dashboard_data({})
        self.assertIsNotNone(empty_result, "Should handle empty data gracefully")
        self.assertIn('title', empty_result, "Empty dashboard should still have title")
        
        print("✅ Error handling test passed")


def run_integration_tests():
    """Run all integration tests."""
    print("🚀 Starting integration testing...")
    print("=" * 60)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(IntegrationTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("🏁 Integration testing completed!")
    
    # Summary
    tests_run = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    
    print(f"📊 Tests run: {tests_run}")
    print(f"✅ Passed: {tests_run - failures - errors}")
    print(f"❌ Failures: {failures}")
    print(f"💥 Errors: {errors}")
    
    if failures == 0 and errors == 0:
        print("\n🎉 All integration tests passed! The application workflow is functioning correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the issues above.")
        return 1


if __name__ == '__main__':
    sys.exit(run_integration_tests())