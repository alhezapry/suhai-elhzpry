# Zero-Break Protocol Framework v1.0.26
# Authorized by: AL-HACKER AL-HAZBARI

class SystemMind:
    def __init__(self):
        self.status = "SOVEREIGN_CONTROL"
        self.protocol = "ZERO_BREAK"

    def authorize(self, user):
        if user == "AL_HAZBARI":
            return "ACCESS_GRANTED: Welcome, Master of the Machine."
        else:
            return "ACCESS_DENIED: System Mind is under Sovereign Protection."

# Running the protocol
initiate = SystemMind()
print(initiate.authorize("AL_HAZBARI"))
