# Smart Task Analyzer

An intelligent task management system that scores and prioritizes tasks based on multiple factors including urgency, importance, effort, and dependencies. Built with Django REST Framework and vanilla JavaScript.

## 🛠️ Setup Instructions

**Prerequisites:** Python 3.8+ and a modern browser.

### 1. Backend Setup (Django)
Navigate to the backend folder and run the following commands:
cd task-analyzer/backend

# Create and activate virtual environment
# On Windows:
python -m venv venv
venv\Scripts\activate
# On Mac/Linux:
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run migrations and start server
python manage.py migrate
python manage.py runserver

The API will be live at http://localhost:8000/api/


2. Frontend Setup
Open a new terminal, navigate to the frontend folder, and start a simple server:
cd task-analyzer/frontend

# Using Python's built-in server to avoid CORS issues
python -m http.server 8080

Then visit http://localhost:8080 in your browser.


3. Testing
To run the automated unit tests, navigate to the backend folder and run:
python manage.py test tasks


## 🧠 Algorithm Explanation

The core of this project is the prioritization engine. I didn't want a simple list sorted by date; I wanted a system that mimics how effective humans actually plan their day. The algorithm assigns a **Priority Score (0-100+)** based on four key factors:

### 1. Urgency (The "Deadline" Factor)
I decided against a simple linear scale. In real life, the difference between 30 days and 25 days is negligible, but the difference between 5 days and "due today" is massive.
* **The Math:** Uses an exponential curve for overdue tasks (to scream for attention) and a steep linear drop-off for the upcoming week.
* **Long-term:** Tasks due 30+ days out asymptotically approach a low baseline score so they don't clutter the top of the list.

### 2. Importance (The "Impact" Factor)
User ratings (1-10) are converted to a 0-100 scale using exponential scaling (`importance^1.5`).
> **Why?** This creates distinct separation. A "Level 10" task scores significantly higher than two "Level 5" tasks combined, ensuring critical work isn't buried by trivial tasks.

### 3. Effort (The "Quick Win" Factor)
I inverted the scoring here: **Lower effort = Higher score.**
> **Why?** This leverages "Quick Win" psychology. If two tasks are equally important, the algorithm suggests doing the shorter one first to clear mental bandwidth and build momentum.

### 4. Dependency Analysis (The "Blocker" Factor)
This was the most complex logic. The system builds a graph to identify blocking tasks.
* **The Logic:** A task that blocks 3 other tasks gets a massive score boost. Even if it isn't due soon, it rises to the top because it is holding up the rest of the project.


### 🎛️ Strategy Configuration
Different days require different workflows. I implemented a "Strategy" pattern to adjust the weights of the factors above:

| Strategy | Focus | Logic |
| :--- | :--- | :--- |
| **Smart Balance** | Default | Balanced weights across all factors. |
| **Fastest Wins** | Momentum | Heavily weights **Effort**. Great for clearing backlogs. |
| **Deadline Driven** | Crisis | Allocates 70% of weight to **Urgency**. |
| **High Impact** | Planning | Prioritizes **Importance** regardless of deadlines. |

---


## 🎨 Design Decisions & Trade-offs

I made several specific architectural choices to keep this project focused on the algorithm while remaining robust.

* **Django DRF vs. Flask**
    * **Decision:** I chose Django Rest Framework.
    * *Trade-off:* Slightly more boilerplate code initially.
    * **Benefit:** It provided a robust structure for serialization and makes future expansion (like adding User Auth) much easier than Flask.

* **Vanilla JS Frontend**
    * **Decision:** Deliberately avoided React or Vue.
    * **Why?** For a project focused on the *backend algorithm*, I didn't want to spend time configuring build tools like Webpack. This keeps deployment incredibly simple—just open the file.

* **Stateless Analysis**
    * **Decision:** The `/analyze` endpoint does not save to the database by default.
    * *Trade-off:* You can't "save" your list between sessions.
    * **Benefit:** Allows for rapid testing of different scenarios and strategies without needing to manually clean up the database after every test run.

* **Non-Linear Scoring**
    * **Decision:** Used exponential math/logarithmic decay instead of linear math.
    * *Trade-off:* It is harder to explain to a user exactly why a score is "76.5."
    * **Benefit:** The resulting ranking "feels" much more natural and human-like than a simple linear sort.


## 📡 API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Endpoints

#### 1. Analyze Tasks

**POST** `/tasks/analyze/`

Analyze and sort a list of tasks by priority.

**Request Body:**
json
{
  "tasks": [
    {
      "title": "Fix login bug",
      "due_date": "2025-11-30",
      "estimated_hours": 3,
      "importance": 8,
      "dependencies": []
    }
  ],
  "strategy": "smart_balance"  // optional
}

**Response:**
json
{
  "tasks": [
    {
      "id": 0,
      "title": "Fix login bug",
      "due_date": "2025-11-30",
      "estimated_hours": 3,
      "importance": 8,
      "dependencies": [],
      "priority_score": 75.5,
      "score_components": {
        "urgency": 85.0,
        "importance": 80.0,
        "effort": 70.0,
        "dependencies": 30.0
      },
      "explanation": "Due very soon (5 days) • High importance rating"
    }
  ],
  "strategy": "smart_balance",
  "total_tasks": 1
}

#### 2. Get Suggestions

**POST** `/tasks/suggest/`

Get top N task suggestions.

**Request Body:**
json
{
  "tasks": [...],
  "strategy": "smart_balance",
  "count": 3
}

**Response:**
json
{
  "suggestions": [
    {
      "rank": 1,
      "title": "Critical bug fix",
      "priority_score": 95.5,
      "suggestion_reason": "Rank #1: OVERDUE by 2 days • High importance rating",
      ...
    }
  ],
  "strategy": "smart_balance",
  "requested_count": 3,
  "returned_count": 3
}

## ⏱️ Time Breakdown
Total Time: ~6-7 hours

Backend (3h): Setting up DRF, designing the scoring logic (bulk of the time), and API views.

Frontend (2h): Building the UI, fetch logic, and dynamic DOM manipulation.

Testing (1h): Writing unit tests for the edge cases (especially circular dependencies).

Documentation (1h): Writing this README and code comments.


## 🏆 Bonus Challenges
I successfully implemented the following advanced features:

**Circular Dependency Detection:**: Used Depth-First Search (DFS) to detect logic loops (e.g., Task A waits for B, B waits for A) and handle them gracefully without crashing.

**Comprehensive Unit Testing:**
Built a robust `TestCase` suite validating 13 distinct scenarios, ensuring the scoring algorithm handles edge cases like past-due dates, missing fields, and complex dependency chains correctly.


## 🚀 Future Improvements
User Accounts: Add JWT authentication so users can save their lists permanently.

Drag-and-Drop: Move to a React frontend to allow dragging tasks to manually override the algorithm.

Calendar Sync: Import due dates directly from Google Calendar.