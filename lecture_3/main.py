"""Student Grade Analyzer program.

A comprehensive system for managing and analyzing student grades.
"""

from typing import List, Optional, TypedDict, Tuple


class Student(TypedDict):
    """Represent a student with their name and grades.

    Attributes:
        name: The student's name as a string.
        grades: List of integer grades between 0 and 100.
    """

    name: str
    grades: List[int]


def safe_input(prompt: str) -> Optional[str]:
    """Safely get input with basic error handling.

    Args:
        prompt: The message to display when asking for input.

    Returns:
        The input string or None if input was cancelled.
    """
    try:
        return input(prompt).strip()
    except KeyboardInterrupt:
        print("\nOperation cancelled")
        return None
    except EOFError:
        print("\nEnd of input reached")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def get_valid_int(
    prompt: str, min_val: Optional[int] = None, max_val: Optional[int] = None
) -> Optional[int]:
    """Get and validate integer input.

    Args:
        prompt: The message to display when asking for input.
        min_val: Minimum allowed value (inclusive).
        max_val: Maximum allowed value (inclusive).

    Returns:
        Validated integer or None if input was cancelled or invalid.
    """
    while True:
        user_input = safe_input(prompt)
        if user_input is None:
            return None

        if not user_input:
            print("Error: Input cannot be empty")
            continue

        try:
            value = int(user_input)

            if min_val is not None and value < min_val:
                print(f"Error: Value must be at least {min_val}")
                continue

            if max_val is not None and value > max_val:
                print(f"Error: Value must be at most {max_val}")
                continue

            return value

        except ValueError:
            print("Error: Please enter a valid number")


def find_student_by_name(students: List[Student], name: str) -> Optional[Student]:
    """Find a student in the list by name using case-insensitive matching.

    Args:
        students: List of student dictionaries to search through.
        name: The name of the student to find.

    Returns:
        The student dictionary if found, None otherwise.
    """
    return next(
        (student for student in students if student["name"].lower() == name.lower()),
        None,
    )


def get_menu_choice() -> Optional[int]:
    """Get and validate the user's menu choice.

    Returns:
        The validated menu choice as integer, or None if input was invalid
        or cancelled by the user.
    """
    return get_valid_int("\nEnter your choice (1-5): ", min_val=1, max_val=5)


def get_student_name_for_adding(students: List[Student]) -> Optional[str]:
    """Get student name for adding new student.

    Returns:
        Validated student name or None if cancelled.
    """
    while True:
        name = safe_input("Enter student name: ")
        if name is None:
            return None

        if not name:
            print("Error: Name cannot be empty")
            continue

        if find_student_by_name(students, name) is not None:
            print("Student with this name already exists")
            continue

        return name


def get_existing_student(students: List[Student]) -> Optional[Student]:
    """Get existing student for grade operations.

    Returns:
        Student object if found, None if not found or cancelled.
    """
    name = safe_input("Enter student name: ")
    if name is None:
        return None

    if not name:
        print("Error: Name cannot be empty")
        return None

    student = find_student_by_name(students, name)
    if student is None:
        print("Student not found")
        return None

    return student


def get_grade_input(student_name: str) -> Optional[int]:
    """Get a single grade input with validation.

    Args:
        student_name: Name of student for context in prompt.

    Returns:
        Valid grade between 0-100, or None if user wants to finish.
    """
    while True:
        grade_input = safe_input(
            f"Enter grade for {student_name} (0-100) or 'done' to finish: "
        )

        if grade_input is None:
            return None

        if not grade_input:
            continue

        if grade_input.lower() == "done":
            return None

        try:
            grade = int(grade_input)
            if 0 <= grade <= 100:
                return grade
            else:
                print("Error: Grade must be between 0 and 100")
        except ValueError:
            print("Error: Please enter a valid number")


def add_new_student(students: List[Student]) -> None:
    """Add a new student to the list."""
    name = get_student_name_for_adding(students)
    if name:
        students.append({"name": name, "grades": []})
        print(f"Student '{name}' added successfully")


def add_grades_for_student(students: List[Student]) -> None:
    """Add grades for an existing student.

    If student is not found, returns to main menu.
    """
    if not students:
        print("No students available. Please add students first")
        return

    student = get_existing_student(students)
    if student is None:
        return

    print(f"Adding grades for {student['name']}:")
    grades_added = 0

    while True:
        grade = get_grade_input(student["name"])
        if grade is None:
            break

        student["grades"].append(grade)
        grades_added += 1
        print(f"Grade {grade} added successfully")

    print(
        f"Added {grades_added} grades for {student['name']}"
        if grades_added > 0
        else "No grades were added"
    )


def calculate_average(grades: List[int]) -> Optional[float]:
    """Calculate the average of a list of grades.

    Args:
        grades: List of numerical grades to average.

    Returns:
        The average as a float if grades exist, None for empty lists.
    """
    return sum(grades) / len(grades) if grades else None


def get_students_with_averages(students: List[Student]) -> List[Tuple[Student, float]]:
    """Get list of students with their averages, excluding those without grades.

    Returns:
        List of (student, average) tuples for students with grades.
    """
    result: List[Tuple[Student, float]] = []
    for student in students:
        if student["grades"]:
            avg = calculate_average(student["grades"])
            if avg is not None:
                result.append((student, avg))
    return result


def show_report(students: List[Student]) -> None:
    """Generate and display a comprehensive report of all students."""
    print("\n" + "=" * 40)
    print("STUDENT REPORT")
    print("=" * 40)

    if not students:
        print("No students available")
        return

    averages: List[float] = []
    for student in students:
        avg = calculate_average(student["grades"])
        status = f"{avg:.1f}" if avg is not None else "N/A"
        print(f"  {student['name']}: {status}")

        if avg is not None:
            averages.append(avg)

    if averages:
        print("-" * 40)
        print(f"Maximum average: {max(averages):.1f}")
        print(f"Minimum average:  {min(averages):.1f}")
        print(f"Overall average: {sum(averages) / len(averages):.1f}")
    else:
        print("No students have grades")


def find_top_student(students: List[Student]) -> None:
    """Find and display the student with the highest average grade."""
    if not students:
        print("No students available")
        return

    students_with_grades = get_students_with_averages(students)

    if not students_with_grades:
        print("No students with grades available")
        return

    top_student, top_average = max(students_with_grades, key=lambda x: x[1])
    print(
        f"The student with the highest average is {top_student['name']} "
        f"with a grade of {top_average:.1f}"
    )


def display_menu() -> None:
    """Display the main menu options to the user."""
    print("\n--- Student Grade Analyzer ---")
    print("1. Add a new student")
    print("2. Add grades for a student")
    print("3. Generate a full report")
    print("4. Find top student")
    print("5. Exit program")


def main() -> None:
    """Run the main program loop."""
    students: List[Student] = []
    print("Welcome to Student Grade Analyzer!")

    menu_actions = {
        1: lambda: add_new_student(students),
        2: lambda: add_grades_for_student(students),
        3: lambda: show_report(students),
        4: lambda: find_top_student(students),
    }

    while True:
        display_menu()
        choice = get_menu_choice()

        if choice == 5:
            print("Exiting program.")
            break
        elif choice in menu_actions:
            menu_actions[choice]()
        elif choice is not None:
            print("Invalid menu choice. Please try again")


if __name__ == "__main__":
    main()
