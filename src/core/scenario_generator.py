import random

class ScenarioGenerator:
    def __init__(self):
        self.sports = [
            "American Football (Lineman)", "American Football (Wide Receiver)", "American Football (Quarterback)",
            "Basketball (Center)", "Basketball (Point Guard)",
            "Soccer (Goalkeeper)", "Soccer (Midfielder)",
            "Volleyball (Outside Hitter)",
            "Baseball (Pitcher)", "Baseball (Catcher)",
            "Tennis", "Golf", "Swimming (Sprinter)", "Swimming (Distance)",
            "Track & Field (Sprinter)", "Track & Field (Marathon)", "Track & Field (Shot Put)",
            "Powerlifting", "Olympic Weightlifting", "CrossFit"
        ]
        self.training_statuses = [
            "Untrained (0-2 months)",
            "Novice (2-6 months)",
            "Intermediate (6-12 months)",
            "Advanced (1+ years)",
            "Elite (Competitive)"
        ]
        self.ages = ["16 (High School)", "18 (College Freshman)", "21 (College Senior)", "28 (Pro)", "35 (Veteran)", "45 (Masters)", "65 (Older Adult)"]
        self.goals = [
            "Hypertrophy", "Maximal Strength", "Power/Explosiveness", 
            "Muscular Endurance", "Aerobic Capacity", "Agility/Speed", 
            "Rehabilitation (ACL Return to Play)", "Injury Prevention"
        ]
        self.phases = [
            "Off-Season (Hypertrophy/Endurance)",
            "Off-Season (Strength)",
            "Pre-Season (Power)",
            "In-Season (Maintenance)",
            "Post-Season (Active Rest)"
        ]

    def generate_profile(self):
        """Generates a random athlete profile string."""
        sport = random.choice(self.sports)
        status = random.choice(self.training_statuses)
        age = random.choice(self.ages)
        goal = random.choice(self.goals)
        phase = random.choice(self.phases)

        return f"""
**Scenario Context (Use this athlete for Application/Analysis questions):**
- **Athlete:** {age}, {sport}
- **Training Status:** {status}
- **Current Phase:** {phase}
- **Primary Goal:** {goal}
"""

if __name__ == "__main__":
    sg = ScenarioGenerator()
    print(sg.generate_profile())
