"""Backend tests for the FastAPI activities API using AAA (Arrange-Act-Assert) pattern."""
import pytest
from fastapi.testclient import TestClient


class TestRootPath:
    """Tests for the root path redirect."""
    
    def test_root_redirects_to_static(self, client, reset_activities):
        """
        ARRANGE: Client is ready.
        ACT: Make a GET request to the root path.
        ASSERT: Response status is 307 (temporary redirect) and Location header points to /static/index.html.
        """
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for retrieving all activities."""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """
        ARRANGE: Client is ready with initial activities data.
        ACT: Make a GET request to /activities.
        ASSERT: Response contains all 9 activities with expected structure.
        """
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        
        # Verify structure of a single activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupForActivity:
    """Tests for signing up for activities."""
    
    def test_signup_for_activity_succeeds(self, client, reset_activities):
        """
        ARRANGE: Client is ready; a new student email ready to sign up.
        ACT: POST to /activities/{activity_name}/signup with a new email.
        ASSERT: Response is 200, success message returned, and participant list updated.
        """
        # Arrange
        new_student_email = "newstudent@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_student_email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Signed up {new_student_email} for {activity_name}"
        
        # Verify the student was added to the activity
        activities_response = client.get("/activities")
        updated_activities = activities_response.json()
        assert new_student_email in updated_activities[activity_name]["participants"]
    
    def test_signup_for_activity_unknown_activity_returns_404(self, client, reset_activities):
        """
        ARRANGE: Client is ready; an activity name that does not exist.
        ACT: POST to /activities/{unknown_activity}/signup.
        ASSERT: Response is 404 with "Activity not found" detail.
        """
        # Arrange
        activity_name = "NonexistentActivity"
        student_email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate_email_returns_400(self, client, reset_activities):
        """
        ARRANGE: Client is ready; a student already in an activity.
        ACT: POST to signup the same student again for the same activity.
        ASSERT: Response is 400 with "Student already signed up" detail.
        """
        # Arrange
        activity_name = "Chess Club"
        existing_student = "michael@mergington.edu"  # Already in Chess Club per app.py
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_student}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student already signed up for this activity"


class TestUnregisterFromActivity:
    """Tests for unregistering from activities."""
    
    def test_unregister_from_activity_succeeds(self, client, reset_activities):
        """
        ARRANGE: Client is ready; a student already signed up for an activity.
        ACT: DELETE from /activities/{activity_name}/signup for an existing participant.
        ASSERT: Response is 200, success message returned, and participant removed from list.
        """
        # Arrange
        activity_name = "Chess Club"
        student_email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Unregistered {student_email} from {activity_name}"
        
        # Verify the student was removed from the activity
        activities_response = client.get("/activities")
        updated_activities = activities_response.json()
        assert student_email not in updated_activities[activity_name]["participants"]
    
    def test_unregister_unknown_activity_returns_404(self, client, reset_activities):
        """
        ARRANGE: Client is ready; an activity name that does not exist.
        ACT: DELETE from /activities/{unknown_activity}/signup.
        ASSERT: Response is 404 with "Activity not found" detail.
        """
        # Arrange
        activity_name = "NonexistentActivity"
        student_email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_non_participant_returns_400(self, client, reset_activities):
        """
        ARRANGE: Client is ready; a student not signed up for the activity.
        ACT: DELETE from /activities/{activity_name}/signup for a non-participant.
        ASSERT: Response is 400 with "Student not signed up" detail.
        """
        # Arrange
        activity_name = "Chess Club"
        non_participant_email = "notstudent@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": non_participant_email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student not signed up for this activity"
