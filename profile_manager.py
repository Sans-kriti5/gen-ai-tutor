import os
import json
from datetime import datetime

PROFILE_FILE = "user_profile.json"

def load_profile():
    """
    Loads user profile and learning history from user_profile.json.
    """
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
            
    # Default empty profile
    return {
        "name": "",
        "roll_number": "",
        "department": "",
        "learning_history": []
    }

def save_profile(profile_data):
    """
    Saves the profile data to user_profile.json.
    """
    try:
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving profile: {e}")
        return False

def add_to_learning_history(topic, activity_type):
    """
    Adds a learning topic and activity type (e.g. 'Chat Q&A', 'Sequential Chain', 'Quiz')
    to the student's persistent history.
    """
    profile = load_profile()
    history_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "topic": topic,
        "activity_type": activity_type
    }
    # Avoid duplicate sequential runs of the same topic and activity
    if profile["learning_history"]:
        last_entry = profile["learning_history"][-1]
        if last_entry["topic"] == topic and last_entry["activity_type"] == activity_type:
            return
            
    profile["learning_history"].append(history_entry)
    save_profile(profile)

def get_personalization_prompt():
    """
    Generates a prompt system prefix based on the student's profile info.
    """
    profile = load_profile()
    if profile.get("name") or profile.get("department"):
        name = profile.get("name", "Student")
        dept = profile.get("department", "general studies")
        roll = profile.get("roll_number", "N/A")
        
        personalization = f"You are tutoring a student named {name}. "
        if dept:
            personalization += f"They are studying in the {dept} department. "
        if roll and roll != "N/A":
            personalization += f"Their Student ID/Roll Number is {roll}. "
            
        personalization += (
            "Tailor your explanations, code examples, academic depth, and tone "
            "to match their department level and academic background. Address them by name occasionally.\n\n"
        )
        return personalization
    return ""
