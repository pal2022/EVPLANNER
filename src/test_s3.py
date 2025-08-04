#!/usr/bin/env python3
"""
Test script to verify S3 connectivity and data loading
Run this to test if your S3 setup is working correctly
"""

import os
import sys

def test_s3_connection():
    """Test S3 connection and list files"""
    try:
        from s3_utils import get_s3_loader
        
        print("Testing S3 connection...")
        s3_loader = get_s3_loader()
        
        # List files in bucket
        files = s3_loader.list_files()
        print(f"Files in S3 bucket: {files}")
        
        # Check if required files exist
        required_files = [
            'roads_bc_regions.json',
            'charging_stations_bc_regions.json',
            'intersections_bc_regions.json'
        ]
        
        for file in required_files:
            exists = s3_loader.file_exists(file)
            print(f"  {file}: {'EXISTS' if exists else 'MISSING'}")
        
        return True
        
    except Exception as e:
        print(f"Error testing S3 connection: {e}")
        return False

def test_data_loading():
    """Test loading data from S3"""
    try:
        from map_construction import load_bc_province_data
        
        print("\nTesting data loading from S3...")
        road_network, charging_stations, intersections = load_bc_province_data()
        
        if road_network and charging_stations and intersections:
            print(f"✅ Successfully loaded data from S3:")
            print(f"  - Road network: {len(road_network.nodes)} nodes, {len(road_network.edges)} edges")
            print(f"  - Charging stations: {len(charging_stations)}")
            print(f"  - Intersections: {len(intersections)}")
            return True
        else:
            print("❌ Failed to load data from S3")
            return False
            
    except Exception as e:
        print(f"Error testing data loading: {e}")
        return False

def main():
    """Main test function"""
    print("=== S3 Integration Test ===\n")
    
    # Check environment variables
    required_env_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'S3_BUCKET_NAME',
        'AWS_REGION'
    ]
    
    print("Checking environment variables...")
    missing_vars = []
    for var in required_env_vars:
        value = os.environ.get(var)
        if value:
            print(f"  ✅ {var}: {'*' * len(value)} (hidden)")
        else:
            print(f"  ❌ {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {missing_vars}")
        print("Please set these environment variables before running the test.")
        return False
    
    print("\n✅ All environment variables are set")
    
    # Test S3 connection
    if not test_s3_connection():
        return False
    
    # Test data loading
    if not test_data_loading():
        return False
    
    print("\n🎉 All tests passed! Your S3 integration is working correctly.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 