from app.core.enums import ProjectRequestStatus, ProjectStatus, is_valid_request_transition, is_valid_project_transition

class TestProjectRequestStateMachine:
    def test_submitted_to_under_review_valid(self):
        assert is_valid_request_transition(ProjectRequestStatus.SUBMITTED, ProjectRequestStatus.UNDER_REVIEW) is True

    def test_under_review_to_accepted_valid(self):
        assert is_valid_request_transition(ProjectRequestStatus.UNDER_REVIEW, ProjectRequestStatus.ACCEPTED) is True

    def test_under_review_to_rejected_valid(self):
        assert is_valid_request_transition(ProjectRequestStatus.UNDER_REVIEW, ProjectRequestStatus.REJECTED) is True

    def test_submitted_to_accepted_skips_review_invalid(self):
        assert is_valid_request_transition(ProjectRequestStatus.SUBMITTED, ProjectRequestStatus.ACCEPTED) is False

    def test_rejected_cannot_transition_anywhere(self):
        for status in ProjectRequestStatus:
            assert is_valid_request_transition(ProjectRequestStatus.REJECTED, status) is False

    def test_converted_cannot_transition_anywhere(self):
        for status in ProjectRequestStatus:
            assert is_valid_request_transition(ProjectRequestStatus.CONVERTED_TO_PROJECT, status) is False

class TestProjectStateMachine:
    def test_pending_to_assigned_valid(self):
        assert is_valid_project_transition(ProjectStatus.PENDING, ProjectStatus.ASSIGNED) is True

    def test_pending_to_in_progress_invalid(self):
        assert is_valid_project_transition(ProjectStatus.PENDING, ProjectStatus.IN_PROGRESS) is False

    def test_in_progress_to_completed_valid(self):
        assert is_valid_project_transition(ProjectStatus.IN_PROGRESS, ProjectStatus.COMPLETED) is True

    def test_completed_cannot_transition(self):
        for status in ProjectStatus:
            assert is_valid_project_transition(ProjectStatus.COMPLETED, status) is False

    def test_waiting_supplier_back_to_in_progress(self):
        assert is_valid_project_transition(ProjectStatus.WAITING_SUPPLIER, ProjectStatus.IN_PROGRESS) is True
