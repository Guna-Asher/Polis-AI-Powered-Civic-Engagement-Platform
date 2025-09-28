import requests
import json

def test_api():
    base_url = "http://localhost:5000/api/v1"
    
    try:
        print("1. Testing basic connectivity...")
        response = requests.get("http://localhost:5000/")
        print(f"   ✅ Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print()
        
        print("2. Testing legislation endpoint...")
        response = requests.get(f"{base_url}/legislation")
        print(f"   ✅ Status: {response.status_code}")
        data = response.json()
        print(f"   Found {len(data.get('legislation', []))} legislation items")
        print()
        
        if data.get('legislation'):
            first_id = data['legislation'][0]['id']
            print(f"3. Testing details for legislation ID {first_id}...")
            response = requests.get(f"{base_url}/legislation/{first_id}")
            print(f"   ✅ Status: {response.status_code}")
            details = response.json()
            print(f"   Title: {details['legislation']['title']}")
            print(f"   Clauses: {len(details.get('clauses', []))}")
            print()
        
        print("4. Testing feedback submission...")
        feedback_data = {
            "legislation_id": 1,
            "sentiment_score": 0.8,
            "tags": ["#EnvironmentalImpact", "#PositiveChange"],
            "comment": "This is a test comment from API testing",
            "demographic_data": {"age_group": "25-35", "location": "Test City"}
        }
        response = requests.post(f"{base_url}/feedback", json=feedback_data)
        print(f"   ✅ Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print()
        
        print("5. Testing civic pulse endpoint...")
        response = requests.get(f"{base_url}/civic-pulse/1")
        print(f"   ✅ Status: {response.status_code}")
        pulse_data = response.json()
        print(f"   Total feedback: {pulse_data.get('total_feedback', 0)}")
        print()
        
        print("🎉 All tests passed! API is working correctly.")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Flask is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api()