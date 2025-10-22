from fastapi.testclient import TestClient

def test_root_redirect(client: TestClient):
    """Test that the root endpoint redirects to the static index.html."""
    response = client.get("/")
    assert response.status_code == 200 or response.status_code == 307
    
def test_get_activities(client: TestClient):
    """Test retrieving the list of activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    
    # Check activity structure
    first_activity = next(iter(activities.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)

def test_signup_for_activity(client: TestClient):
    """Test signing up for an activity."""
    # Get available activities
    activities_response = client.get("/activities")
    activities = activities_response.json()
    first_activity_name = next(iter(activities.keys()))
    
    # Test successful signup
    test_email = "test_student@mergington.edu"
    response = client.post(f"/activities/{first_activity_name}/signup?email={test_email}")
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify the participant was added by getting the updated activities
    updated_activities_response = client.get("/activities")
    updated_activities = updated_activities_response.json()
    assert test_email in updated_activities[first_activity_name]["participants"]
    
    # Test duplicate signup
    response = client.post(f"/activities/{first_activity_name}/signup?email={test_email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

def test_signup_nonexistent_activity(client: TestClient):
    """Test signing up for a non-existent activity."""
    response = client.post("/activities/NonexistentActivity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unregister_from_activity(client: TestClient):
    """Test unregistering from an activity."""
    # First, sign up a test student
    test_email = "test_unregister@mergington.edu"
    activities_response = client.get("/activities")
    activities = activities_response.json()
    first_activity_name = next(iter(activities.keys()))
    
    # Sign up the student
    client.post(f"/activities/{first_activity_name}/signup?email={test_email}")
    
    # Test successful unregistration
    response = client.delete(f"/activities/{first_activity_name}/unregister?email={test_email}")
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify student is no longer in participants
    activities_response = client.get("/activities")
    updated_activities = activities_response.json()
    assert test_email not in updated_activities[first_activity_name]["participants"]
    
    # Test unregistering when not registered
    response = client.delete(f"/activities/{first_activity_name}/unregister?email={test_email}")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()