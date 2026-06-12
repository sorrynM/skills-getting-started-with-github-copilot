"""
FastAPI endpoint tests using the AAA (Arrange-Act-Assert) pattern.
Tests cover GET /activities, POST signup, and DELETE unregister endpoints.
"""

import pytest
from src.app import activities


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client, setup_activities):
        """
        Test that GET /activities returns all activities with correct structure.
        
        AAA Pattern:
        - Arrange: Activities are set up via fixture
        - Act: Make GET request to /activities
        - Assert: Verify status code and response contains all activities
        """
        # Arrange: (setup_activities fixture handles this)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Test Activity" in data
        assert "Empty Activity" in data
        assert len(data) == 2
    
    def test_get_activities_includes_participants(self, client, setup_activities):
        """
        Test that activity data includes participants list.
        
        AAA Pattern:
        - Arrange: Activities fixture is loaded
        - Act: Fetch activities
        - Assert: Verify participants are included with correct data
        """
        # Arrange: (setup_activities fixture handles this)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        data = response.json()
        assert "participants" in data["Test Activity"]
        assert data["Test Activity"]["participants"] == ["alice@test.edu", "bob@test.edu"]
        assert data["Empty Activity"]["participants"] == []
    
    def test_get_activities_includes_all_fields(self, client, setup_activities):
        """
        Test that activity objects include all required fields.
        
        AAA Pattern:
        - Arrange: Activities are set up
        - Act: Get activities
        - Assert: Verify all required fields are present
        """
        # Arrange: (setup_activities fixture handles this)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        data = response.json()
        activity = data["Test Activity"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_successful(self, client, setup_activities):
        """
        Test successful signup for an activity.
        
        AAA Pattern:
        - Arrange: Create request parameters
        - Act: Make POST request to signup
        - Assert: Verify response and participant was added
        """
        # Arrange
        activity_name = "Test Activity"
        email = "charlie@test.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == 3
    
    def test_signup_adds_email_to_participants_list(self, client, setup_activities):
        """
        Test that signup correctly adds email to the participants list.
        
        AAA Pattern:
        - Arrange: Set up test parameters
        - Act: Sign up a new student
        - Assert: Verify email is in the participants list
        """
        # Arrange
        activity_name = "Empty Activity"
        email = "david@test.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "message" in data
        assert email in activities[activity_name]["participants"]
    
    def test_signup_for_nonexistent_activity_returns_404(self, client, setup_activities):
        """
        Test that signup for non-existent activity returns 404.
        
        AAA Pattern:
        - Arrange: Prepare request with invalid activity name
        - Act: Attempt to sign up
        - Assert: Verify 404 error is returned
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test@test.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_response_contains_success_message(self, client, setup_activities):
        """
        Test that successful signup returns a success message.
        
        AAA Pattern:
        - Arrange: Create valid request
        - Act: Submit signup
        - Assert: Verify response message
        """
        # Arrange
        activity_name = "Test Activity"
        email = "frank@test.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        data = response.json()
        
        # Assert
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
    
    def test_signup_with_url_encoded_activity_name(self, client, setup_activities):
        """
        Test that signup works with URL-encoded activity names.
        
        AAA Pattern:
        - Arrange: Create activity with space in name, prepare encoded request
        - Act: Signup with URL-encoded name
        - Assert: Verify signup succeeded
        """
        # Arrange
        activities["New Activity"] = {
            "description": "Test",
            "schedule": "Monday",
            "max_participants": 5,
            "participants": []
        }
        activity_name = "New Activity"
        encoded_name = "New%20Activity"
        email = "grace@test.edu"
        
        # Act
        response = client.post(
            f"/activities/{encoded_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]
    
    def test_duplicate_signup_adds_participant_again(self, client, setup_activities):
        """
        Test that signing up the same email twice adds them twice (current behavior).
        This documents the duplicate registration bug.
        
        AAA Pattern:
        - Arrange: Prepare email and activity
        - Act: Sign up same email twice
        - Assert: Verify email appears twice in participants and list grows by 1
        """
        # Arrange
        activity_name = "Test Activity"
        email = "alice@test.edu"  # Already in participants
        initial_count = len(activities[activity_name]["participants"])
        initial_email_count = activities[activity_name]["participants"].count(email)
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        # Verify the email now appears one more time
        assert activities[activity_name]["participants"].count(email) == initial_email_count + 1
        # Verify total participants increased by 1
        assert len(activities[activity_name]["participants"]) == initial_count + 1


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_successful(self, client, setup_activities):
        """
        Test successful unregistration of a participant.
        
        AAA Pattern:
        - Arrange: Identify participant to remove
        - Act: Make DELETE request to unregister
        - Assert: Verify participant was removed
        """
        # Arrange
        activity_name = "Test Activity"
        email = "alice@test.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1
    
    def test_unregister_removes_email_from_list(self, client, setup_activities):
        """
        Test that unregister correctly removes email from participants list.
        
        AAA Pattern:
        - Arrange: Prepare unregister request
        - Act: Unregister a participant
        - Assert: Verify email is removed
        """
        # Arrange
        activity_name = "Test Activity"
        email = "bob@test.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "message" in data
        assert email not in activities[activity_name]["participants"]
    
    def test_unregister_nonexistent_participant_returns_404(self, client, setup_activities):
        """
        Test that unregistering non-existent participant returns 404.
        
        AAA Pattern:
        - Arrange: Prepare request with non-existent email
        - Act: Attempt to unregister
        - Assert: Verify 404 error
        """
        # Arrange
        activity_name = "Test Activity"
        email = "nonexistent@test.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]
    
    def test_unregister_from_nonexistent_activity_returns_404(self, client, setup_activities):
        """
        Test that unregistering from non-existent activity returns 404.
        
        AAA Pattern:
        - Arrange: Prepare request with invalid activity
        - Act: Attempt to unregister
        - Assert: Verify 404 error
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "alice@test.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_response_contains_success_message(self, client, setup_activities):
        """
        Test that unregister returns a success message.
        
        AAA Pattern:
        - Arrange: Prepare valid unregister request
        - Act: Unregister participant
        - Assert: Verify response message
        """
        # Arrange
        activity_name = "Test Activity"
        email = "alice@test.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        data = response.json()
        
        # Assert
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
    
    def test_unregister_from_empty_activity_returns_404(self, client, setup_activities):
        """
        Test that unregistering from activity with no participants returns 404.
        
        AAA Pattern:
        - Arrange: Target empty activity
        - Act: Attempt to unregister
        - Assert: Verify 404 error
        """
        # Arrange
        activity_name = "Empty Activity"
        email = "anyone@test.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]


class TestIntegrationScenarios:
    """Integration tests combining multiple operations."""
    
    def test_signup_and_unregister_flow(self, client, setup_activities):
        """
        Test complete flow: sign up, verify, then unregister.
        
        AAA Pattern:
        - Arrange: Prepare test data
        - Act: Sign up, then unregister
        - Assert: Verify participant count changes correctly
        """
        # Arrange
        activity_name = "Empty Activity"
        email = "henry@test.edu"
        
        # Act: Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert signup succeeded
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == 1
        
        # Act: Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert unregister succeeded
        assert unregister_response.status_code == 200
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == 0
    
    def test_multiple_participants_signup(self, client, setup_activities):
        """
        Test that multiple different participants can sign up.
        
        AAA Pattern:
        - Arrange: Prepare multiple emails
        - Act: Sign up multiple participants
        - Assert: Verify all are added
        """
        # Arrange
        activity_name = "Empty Activity"
        emails = ["ivy@test.edu", "jack@test.edu", "kate@test.edu"]
        
        # Act: Sign up all participants
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Assert: All participants are added
        for email in emails:
            assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == 3
    
    def test_get_activities_reflects_signup_changes(self, client, setup_activities):
        """
        Test that GET /activities reflects changes after signup.
        
        AAA Pattern:
        - Arrange: Get initial state
        - Act: Sign up new participant and fetch activities
        - Assert: Verify updated participant count in response
        """
        # Arrange
        activity_name = "Empty Activity"
        email = "leo@test.edu"
        
        # Act: Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Act: Fetch activities
        get_response = client.get("/activities")
        
        # Assert
        assert get_response.status_code == 200
        data = get_response.json()
        assert email in data[activity_name]["participants"]
        assert len(data[activity_name]["participants"]) == 1
