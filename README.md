# ACEest Fitness & Gym

A Flask-based fitness management application developed as part of the DevOps assignment. The application provides client management, workout tracking, progress monitoring, AI-assisted workout program generation, membership handling, reporting, and automated testing.

The project demonstrates a complete DevOps workflow using Git/GitHub, Pytest, Docker, Jenkins, and GitHub Actions.

---

## Features

- User login and session-based authentication
- Dashboard for fitness management
- Client management
- Add and manage client information
- AI-assisted workout program generation based on fitness goals
- Membership status handling
- Workout management
- Exercise tracking
- Progress and body-metric tracking
- Weekly adherence chart
- Client summary
- PDF client reports
- Health-check endpoint
- Automated Pytest test suite
- Dockerized application
- Jenkins CI pipeline
- GitHub Actions CI workflow

---

## Technology Stack

- Python 3.9
- Flask
- SQLite
- HTML/CSS
- Jinja2 templates
- Pytest
- Matplotlib
- FPDF
- Docker
- Jenkins
- Git/GitHub
- GitHub Actions

EOF

## Project Structure

The project is organized as follows:

aceest-fitness/
- app.py
- requirements.txt
- Dockerfile
- Jenkinsfile
- .dockerignore
- .gitignore
- README.md
- templates/
- static/
- tests/
  - test_app.py
- .github/
  - workflows/
    - main.yml
## Local Setup

### 1. Clone the repository

git clone https://github.com/abhi3627-bits/aceest-fitness-devops.git
cd aceest-fitness-devops

### 2. Create and activate a virtual environment

python3 -m venv venv
source venv/bin/activate

### 3. Install dependencies

pip install -r requirements.txt

### 4. Run the Flask application

python app.py

The application runs on:

http://127.0.0.1:5000

Default login credentials:

Username: admin
Password: admin ## Manual Testing

The main application functions were manually verified through the Flask web interface and HTTP requests.

Verified functionality includes:

- Application health check
- User login
- Dashboard access
- Adding a client
- AI-assisted workout program generation
- Membership status handling
- Adding workouts
- Adding exercises
- Viewing client progress
- Viewing client metrics
- Weekly adherence chart
- Client summary
- PDF report generation

Health check can be verified with:

curl http://127.0.0.1:5000/health

Expected response:

{"application":"ACEest Fitness & Gym","status":"UP"}## Automated Testing

The project uses Pytest for automated testing.

The test suite covers:

- Application health check
- User authentication
- Client creation
- AI workout program generation
- Workout creation
- Exercise creation
- Progress and metrics
- Weekly adherence chart
- PDF report generation

Run the tests with:

pytest -q

The test suite currently contains 9 tests.
## Docker

The application is containerized using Docker.

### Build the Docker image

docker build -t aceest-fitness:latest .

### Run the container

docker run -d --name aceest-fitness-container -p 5001:5000 aceest-fitness:latest

The application can then be accessed at:

http://127.0.0.1:5001

### Health check

curl http://127.0.0.1:5001/health

### Run tests inside the Docker container

docker run --rm aceest-fitness:latest pytest -q
## Jenkins CI Pipeline

Jenkins is used to automate the CI pipeline.

The Jenkins pipeline performs the following stages:

1. Checkout source code from GitHub
2. Create a Python virtual environment
3. Install project dependencies
4. Perform Python syntax validation
5. Run the Pytest test suite
6. Build the Docker image

The Jenkins pipeline is defined in:

Jenkinsfile

The Jenkins job used for this project is:

ACEest-Fitness-CI

The pipeline was successfully executed after configuring Jenkins with Docker access.
## GitHub Actions CI

GitHub Actions is configured to run automatically on every push and pull request.

The workflow file is:

.github/workflows/main.yml

The workflow contains three stages:

1. Build and Lint
   - Checks out the source code
   - Sets up Python 3.9
   - Installs dependencies
   - Performs Python syntax validation

2. Docker Image Assembly
   - Builds the Docker image
   - Saves the image as an artifact
   - Uploads the Docker image artifact

3. Automated Testing in Container
   - Downloads the Docker image artifact
   - Loads the image
   - Runs the Pytest test suite inside the container

The GitHub Actions workflow was successfully executed and completed all stages successfully.

Then press **Ctrl + D**.

When you are back at the normal prompt, reply **done**.
## CI/CD Flow

The overall DevOps workflow is:

Developer
   |
   v
Git Commit
   |
   v
GitHub Repository
   |
   +----------------------+
   |                      |
   v                      v
Jenkins CI          GitHub Actions
   |                      |
   v                      v
Build & Test        Build & Test
   |                      |
   v                      v
Docker Build        Docker Build
   |                      |
   +----------+-----------+
              |
              v
        Successful CI

---

## Git Commit History

The project was developed using meaningful commits representing major development stages.

Important commits include:

- Build ACEest Fitness Flask application
- Add automated tests for ACEest Fitness
- Add Docker support for ACEest Fitness
- Add Jenkins CI pipeline
- Add GitHub Actions CI workflow

This demonstrates incremental development and version control using Git and GitHub.
## Current Verification

The following components have been successfully verified:

- Flask application starts successfully
- Health endpoint returns HTTP 200
- User authentication works
- Client management works
- AI-assisted program generation works
- Membership handling works
- Workout and exercise tracking works
- Progress and metrics work
- PDF report generation works
- Pytest: 9 tests passed
- Docker image builds successfully
- Pytest passes inside the Docker container
- Jenkins CI pipeline completed successfully
- GitHub Actions CI workflow completed successfully

---

## Repository

GitHub repository:

https://github.com/abhi3627-bits/aceest-fitness-devops

The repository is public and contains the application source code, automated tests, Docker configuration, Jenkins pipeline, GitHub Actions workflow, and project documentation.
