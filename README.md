# Human Resource Management System (HRMS)

This is a web-based Human Resource Management System developed using Python and Flask. It is designed to automate key HR functions such as employee management, attendance, leave tracking, and payroll generation.

## 🔑 Key Features

- **Login Page**  
  Secure login functionality for administrators and employees.

- **Registration Page**  
  Allows new employees to register into the system with necessary details.

- **Dashboard**  
  A centralized panel for accessing all major HR modules and viewing real-time stats.

- **Employee Directory**  
  Organized listing of employees categorized by department: Tech, Non-Tech, Interns.

- **Attendance Tracking**  
  Tracks daily attendance and maintains records for reporting.

- **Leave Management**  
  Enables employees to apply for leave and allows HR/admin to review and approve/reject requests.

- **Payroll Management**  
  Handles salary generation based on attendance, leaves, and predefined salary structure.

## 💻 Tech Stack

- **Backend**: Python, Flask  
- **Frontend**: HTML, CSS, JavaScript (Basic)  
- **Framework**: Flask (for routing and server-side logic)  
- **Templating Engine**: Jinja2 (used with Flask)

## 📁 Project Structure

- `app.py` – Main Flask application file  
- `templates/` – Contains HTML files  
- `static/` – Contains CSS and JavaScript files  
- `routes/` – Flask route handling for different modules  
- `database/` – Stores user and attendance data (if using files or SQLite)

## 🚀 How to Run

1. Clone the repository:  
   `git clone https://github.com/yourusername/Human-Resource-Management-System.git`

2. Navigate to the project folder:  
   `cd Human-Resource-Management-System`

3. Run the app:  
   `python app.py`

4. Open your browser and go to:  
   `http://127.0.0.1:5000`

## 📌 Note

This project was developed as part of an internship/learning experience. Future versions may include enhanced UI, email integration, detailed reporting, and secure authentication systems.
