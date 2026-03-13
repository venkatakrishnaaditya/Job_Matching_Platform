"""
Application status transition validator
Implements the locked business rules for status transitions
"""

# Valid status values
VALID_STATUSES = ["Applied", "Reviewed", "Shortlisted", "Rejected", "Withdrawn"]

# Status transition rules (LOCKED DESIGN)
VALID_TRANSITIONS = {
    "Applied": ["Reviewed", "Rejected", "Withdrawn"],
    "Reviewed": ["Shortlisted", "Rejected"],
    "Shortlisted": ["Rejected"],
    "Rejected": [],  # Terminal state
    "Withdrawn": []  # Terminal state
}


def is_valid_status(status: str) -> bool:
    """
    Check if a status value is valid
    
    Args:
        status: Status string to validate
        
    Returns:
        True if status is valid, False otherwise
    """
    return status in VALID_STATUSES


def is_valid_status_transition(current_status: str, new_status: str) -> bool:
    """
    Check if a status transition is allowed based on business rules
    
    Valid transitions (LOCKED):
    - Applied → Reviewed, Rejected, Withdrawn
    - Reviewed → Shortlisted, Rejected
    - Shortlisted → Rejected
    
    Args:
        current_status: Current application status
        new_status: Desired new status
        
    Returns:
        True if transition is valid, False otherwise
    """
    if not is_valid_status(current_status) or not is_valid_status(new_status):
        return False
    
    return new_status in VALID_TRANSITIONS.get(current_status, [])


def can_candidate_withdraw(status: str) -> bool:
    """
    Check if candidate can withdraw application based on current status
    
    Rule (LOCKED): Candidate can only withdraw if status = "Applied"
    
    Args:
        status: Current application status
        
    Returns:
        True if candidate can withdraw, False otherwise
    """
    return status == "Applied"


def is_terminal_status(status: str) -> bool:
    """
    Check if status is a terminal state (no further transitions allowed)
    
    Args:
        status: Status to check
        
    Returns:
        True if status is terminal (Rejected or Withdrawn)
    """
    return status in ["Rejected", "Withdrawn"]


def get_allowed_transitions(current_status: str) -> list:
    """
    Get list of allowed status transitions from current status
    
    Args:
        current_status: Current application status
        
    Returns:
        List of allowed next statuses
    """
    return VALID_TRANSITIONS.get(current_status, [])
