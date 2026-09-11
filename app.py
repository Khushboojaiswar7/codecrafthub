from flask import Flask, jsonify, request
import json
import os
from datetime import datetime

# Create the Flask application
app = Flask(__name__)

# Name of the JSON file used to store course data
DATA_FILE = "courses.json"

# Allowed course status values
VALID_STATUSES = ["Not Started", "In Progress", "Completed"]


# ---------------------------------------------------------
# Helper function: Load courses from the JSON file
# ---------------------------------------------------------
def load_courses():
    """
    Reads course data from courses.json.

    If the file does not exist, it is created automatically
    with an empty list.
    """

    # Create the file if it does not exist
    if not os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "w") as file:
                json.dump([], file, indent=2)
            return []
        except OSError:
            raise RuntimeError("Unable to create courses.json")

    # Read existing course data
    try:
        with open(DATA_FILE, "r") as file:
            courses = json.load(file)

        # Make sure the JSON contains a list
        if not isinstance(courses, list):
            raise RuntimeError("courses.json must contain a list")

        return courses

    except json.JSONDecodeError:
        raise RuntimeError("courses.json contains invalid JSON")

    except OSError:
        raise RuntimeError("Unable to read courses.json")


# ---------------------------------------------------------
# Helper function: Save courses to the JSON file
# ---------------------------------------------------------
def save_courses(courses):
    """
    Saves the list of courses into courses.json.
    """

    try:
        with open(DATA_FILE, "w") as file:
            json.dump(courses, file, indent=2)

    except OSError:
        raise RuntimeError("Unable to write to courses.json")


# ---------------------------------------------------------
# Helper function: Generate the next course ID
# ---------------------------------------------------------
def get_next_id(courses):
    """
    Generates a new ID.

    The first course receives ID 1.
    """

    if not courses:
        return 1

    return max(course["id"] for course in courses) + 1


# ---------------------------------------------------------
# Helper function: Validate target date
# ---------------------------------------------------------
def validate_date(target_date):
    """
    Checks whether the date follows YYYY-MM-DD format.
    """

    try:
        datetime.strptime(target_date, "%Y-%m-%d")
        return True

    except ValueError:
        return False


# ---------------------------------------------------------
# GET /api/courses
# Get all courses
# ---------------------------------------------------------
@app.route("/api/courses", methods=["GET"])
def get_all_courses():

    try:
        courses = load_courses()

        return jsonify({
            "success": True,
            "count": len(courses),
            "courses": courses
        }), 200

    except RuntimeError as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ---------------------------------------------------------
# GET /api/courses/<id>
# Get a specific course
# ---------------------------------------------------------
@app.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):

    try:
        courses = load_courses()

        # Find the course with the requested ID
        course = next(
            (course for course in courses if course["id"] == course_id),
            None
        )

        if course is None:
            return jsonify({
                "success": False,
                "error": "Course not found"
            }), 404

        return jsonify({
            "success": True,
            "course": course
        }), 200

    except RuntimeError as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ---------------------------------------------------------
# POST /api/courses
# Add a new course
# ---------------------------------------------------------
@app.route("/api/courses", methods=["POST"])
def add_course():

    # Get JSON data from the request
    data = request.get_json(silent=True)

    # Check whether JSON data was provided
    if data is None:
        return jsonify({
            "success": False,
            "error": "Request body must contain valid JSON"
        }), 400

    # Required fields
    required_fields = [
        "name",
        "description",
        "target_date",
        "status"
    ]

    # Check for missing fields
    for field in required_fields:

        if field not in data:
            return jsonify({
                "success": False,
                "error": f"Missing required field: {field}"
            }), 400

        # Also make sure fields are not empty
        if not isinstance(data[field], str) or not data[field].strip():
            return jsonify({
                "success": False,
                "error": f"Field '{field}' cannot be empty"
            }), 400

    # Validate status
    if data["status"] not in VALID_STATUSES:
        return jsonify({
            "success": False,
            "error": (
                "Status must be one of: "
                + ", ".join(VALID_STATUSES)
            )
        }), 400

    # Validate target date
    if not validate_date(data["target_date"]):
        return jsonify({
            "success": False,
            "error": "target_date must use YYYY-MM-DD format"
        }), 400

    try:
        courses = load_courses()

        # Create the new course
        new_course = {
            "id": get_next_id(courses),
            "name": data["name"],
            "description": data["description"],
            "target_date": data["target_date"],
            "status": data["status"],
            "created_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }

        # Add the new course
        courses.append(new_course)

        # Save updated list
        save_courses(courses)

        return jsonify({
            "success": True,
            "message": "Course added successfully",
            "course": new_course
        }), 201

    except RuntimeError as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ---------------------------------------------------------
# PUT /api/courses/<id>
# Update an existing course
# ---------------------------------------------------------
@app.route("/api/courses/<int:course_id>", methods=["PUT"])
def update_course(course_id):

    data = request.get_json(silent=True)

    # Check JSON input
    if data is None:
        return jsonify({
            "success": False,
            "error": "Request body must contain valid JSON"
        }), 400

    try:
        courses = load_courses()

        # Find the course
        course_index = next(
            (
                index
                for index, course in enumerate(courses)
                if course["id"] == course_id
            ),
            None
        )

        # Course does not exist
        if course_index is None:
            return jsonify({
                "success": False,
                "error": "Course not found"
            }), 404

        course = courses[course_index]

        # Update name if provided
        if "name" in data:

            if not isinstance(data["name"], str) or not data["name"].strip():
                return jsonify({
                    "success": False,
                    "error": "Name cannot be empty"
                }), 400

            course["name"] = data["name"]

        # Update description if provided
        if "description" in data:

            if (
                not isinstance(data["description"], str)
                or not data["description"].strip()
            ):
                return jsonify({
                    "success": False,
                    "error": "Description cannot be empty"
                }), 400

            course["description"] = data["description"]

        # Update target date if provided
        if "target_date" in data:

            if not validate_date(data["target_date"]):
                return jsonify({
                    "success": False,
                    "error": "target_date must use YYYY-MM-DD format"
                }), 400

            course["target_date"] = data["target_date"]

        # Update status if provided
        if "status" in data:

            if data["status"] not in VALID_STATUSES:
                return jsonify({
                    "success": False,
                    "error": (
                        "Status must be one of: "
                        + ", ".join(VALID_STATUSES)
                    )
                }), 400

            course["status"] = data["status"]

        # Save changes
        save_courses(courses)

        return jsonify({
            "success": True,
            "message": "Course updated successfully",
            "course": course
        }), 200

    except RuntimeError as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ---------------------------------------------------------
# DELETE /api/courses/<id>
# Delete a course
# ---------------------------------------------------------
@app.route("/api/courses/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):

    try:
        courses = load_courses()

        # Find the course
        course_index = next(
            (
                index
                for index, course in enumerate(courses)
                if course["id"] == course_id
            ),
            None
        )

        # Course does not exist
        if course_index is None:
            return jsonify({
                "success": False,
                "error": "Course not found"
            }), 404

        # Remove the course
        deleted_course = courses.pop(course_index)

        # Save the updated list
        save_courses(courses)

        return jsonify({
            "success": True,
            "message": "Course deleted successfully",
            "deleted_course": deleted_course
        }), 200

    except RuntimeError as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ---------------------------------------------------------
# Start the Flask application
# ---------------------------------------------------------
if __name__ == "__main__":

    print("CodeCraftHub API is starting...")
    print(
        f"Data will be stored in: "
        f"{os.path.abspath(DATA_FILE)}"
    )
    print("API available at: http://localhost:5000")

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
    