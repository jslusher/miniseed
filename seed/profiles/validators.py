from seed.profiles.execeptions import MissingProfileName

def validate_profile(profile):
    if not hasattr(profile, 'name'):
        raise ValueError("Profile must have name")
