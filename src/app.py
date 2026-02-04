"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

from pydantic import BaseModel
from typing import Optional

# In-memory user database (students and clubs)
users = {
    "students": {},  # email: {"name": ..., "password": ..., "profile": {...}}
    "clubs": {}      # email: {"name": ..., "password": ..., "profile": {...}}
}

# In-memory activity database
activities = {
    class UserRegister(BaseModel):
        email: str
        name: str
        password: str

    class UserLogin(BaseModel):
        email: str
        password: str

    class UserProfile(BaseModel):
        name: Optional[str] = None
        bio: Optional[str] = None

    # --- Authentication & Profile Endpoints ---
    @app.post("/register/{user_type}")
    def register_user(user_type: str, user: UserRegister):
        if user_type not in users:
            raise HTTPException(status_code=400, detail="Invalid user type")
        if user.email in users[user_type]:
            raise HTTPException(status_code=400, detail="User already exists")
        users[user_type][user.email] = {
            "name": user.name,
            "password": user.password,
            "profile": {"name": user.name, "bio": ""}
        }
        return {"message": f"{user_type.title()} registered successfully"}

    @app.post("/login/{user_type}")
    def login_user(user_type: str, creds: UserLogin):
        if user_type not in users:
            raise HTTPException(status_code=400, detail="Invalid user type")
        user = users[user_type].get(creds.email)
        if not user or user["password"] != creds.password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {"message": f"{user_type.title()} logged in", "profile": user["profile"]}

    @app.get("/profile/{user_type}/{email}")
    def get_profile(user_type: str, email: str):
        if user_type not in users:
            raise HTTPException(status_code=400, detail="Invalid user type")
        user = users[user_type].get(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user["profile"]

    @app.put("/profile/{user_type}/{email}")
    def update_profile(user_type: str, email: str, profile: UserProfile):
        if user_type not in users:
            raise HTTPException(status_code=400, detail="Invalid user type")
        user = users[user_type].get(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if profile.name is not None:
            user["profile"]["name"] = profile.name
        if profile.bio is not None:
            user["profile"]["bio"] = profile.bio
        return {"message": "Profile updated", "profile": user["profile"]}

    @app.put("/change-password/{user_type}/{email}")
    def change_password(user_type: str, email: str, data: UserLogin):
        if user_type not in users:
            raise HTTPException(status_code=400, detail="Invalid user type")
        user = users[user_type].get(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user["password"] != data.password:
            raise HTTPException(status_code=401, detail="Current password incorrect")
        user["password"] = data.name  # Here, 'name' field is used for new password
        return {"message": "Password changed"}
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
