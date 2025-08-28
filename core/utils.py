import json
import os

def mask_email(email: str) -> str:
    """Mask email for privacy (y****@domain.com)."""
    parts = email.split("@")
    return parts[0][0] + "****@" + parts[1]

def mask_phone(phone: str) -> str:
    """Mask phone number, show only last 2 digits."""
    return "*******" + phone[-2:]

def save_candidate(data: dict, filename="data/candidates.json"):
    """Save candidate info safely with masking."""
    safe_data = data.copy()

    if "Email" in safe_data:
        safe_data["Email"] = mask_email(safe_data["Email"])
    if "Phone Number" in safe_data:
        safe_data["Phone Number"] = mask_phone(safe_data["Phone Number"])

    # Ensure data folder exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    try:
        with open(filename, "r") as f:
            candidates = json.load(f)
    except FileNotFoundError:
        candidates = []

    candidates.append(safe_data)

    with open(filename, "w") as f:
        json.dump(candidates, f, indent=4)
