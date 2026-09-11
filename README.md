# CodeCraftHub Learning Management System

CodeCraftHub is a simple personalized learning platform for developers.

It provides a REST API that allows users to create, view, update, and delete courses they want to learn. Course information is stored in a JSON file instead of a database.

This project is designed for beginners who are learning how REST APIs work with Python and Flask.

---

## Features

- Create a new learning course
- View all courses
- View a specific course
- Update course information
- Delete a course
- Track course status
- Set a target completion date
- Automatically generate course IDs
- Automatically record the course creation timestamp
- Store data in a JSON file
- Automatically create `courses.json` if it does not exist
- Validate course status values
- Validate target dates using `YYYY-MM-DD` format
- Handle missing fields and invalid requests
- Handle JSON file read/write errors

---

## Technologies Used

- Python
- Flask
- REST API
- JSON
- curl for API testing

No database is required for this project.

---

## Project Structure

```text
codecrafthub/
│
├── app.py
├── courses.json
├── requirements.txt
└── README.md
