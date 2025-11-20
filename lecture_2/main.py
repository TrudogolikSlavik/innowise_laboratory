# Profile Generation System
# This program creates user profiles based on personal information and hobbies

def generate_profile(age: int) -> str:
    """
    Categorizes iser into life stage based on age.

    Args:
        age: The age of the user in years

    Returns:
        Life stage category string
    """
    # Age classification logic:
    # - 12 and below: Child
    # - 13-19: Teenager
    # - 20 and above: Adult
    if age <= 12:
        return "Child"
    if age <= 19:
        return "Teenager"
    return "Adult"


def profile_summary(user_profile: dict) -> None:
    """
    Displays formatted user profile summary with special handling for hobbies.

    Args:
        user_profile (dict): Dictionary containing user profile data with keys:
            - 'Name': User's full name
            - 'Age': User's current age
            - 'Life stage': Developmental category
            - 'Hobbies': List of user's hobbies or empty list
            
    Returns:
        None: This function only prints output to console
        
    Example:
        >>> profile = {'Name': 'John', 'Age': 25, 'Life stage': 'Adult', 'Hobbies': ['Reading']}
        >>> profile_summary(profile)
        ---
        Profile Summary: 
        Name: John
        Age: 25
        Life stage: Adult
        Favourite Hobbies (1):
        - Reading
        ---"""
    # Print section separator
    print("\n")
    print("-"*3)
    print("Profile Summary: ")

    # Iterate through all profile fields
    for key, value in user_profile.items():
        # Special formatting for hobbies list
        if key == "Hobbies":
            if value:
                # Displays count and list of hobbies
                print(f"Favourite Hobbies ({len(value)}):")
                for hobby in value:
                    print(f"- {hobby}")
            else:
                # Handle empty hobbies list
                print("You didn't mention any hobbies")
        else:
            # Standard field display
            print(f"{key}: {value}")
    # Close summary section
    print("-"*3)


def main() -> None:
    """
    Main program flow - collects user data and generates profile.

    Workflow:
        1. Collect user's name and birth year
        2. Calculate current age
        3. Collect hobbies until user signals stop
        4. Generate life stage category
        5. Compile and display profile summary
    """
    # Constant for age calculation
    CURRENT_YEAR = 2025

    # Collect basic user information
    user_name = input("Enter Your full name: ")
    birth_year_str = input("Enter your birth year: ")

    # Convert birth year to integer  and calculate current age
    birth_year = int(birth_year_str)
    current_age = CURRENT_YEAR - birth_year

    # Initialize empty llist for hobbies
    hobbies = []

    # Collect hobbies until user enters 'stop'
    # Using walrus operator for coincise input loop
    while (hobby:= input("Enter a favourite hobby or type 'stop' to finish: ")).lower() != 'stop':
        # Only add non-empty hobbies to the list
        if hobby:
            hobbies.append(hobby)

    # Determine life stage category based on age
    life_stage = generate_profile(current_age)

    # Compile complete user profile dictionary
    user_profile = {
        "Name": user_name,
        "Age": current_age,
        "Life stage": life_stage,
        "Hobbies": hobbies,
    }

    # Display the final profile summary
    profile_summary(user_profile)


if __name__ == "__main__":
    # Entry point when script is executed directly
    main()
