💡 Smart Campus Assistant: A Voice Assistant
Smart Campus Assistant is a web-based platform developed using Python Flask, HTML5, CSS3, and JavaScript. It’s designed to provide students with a seamless experience in navigating campus-related services—from viewing timetables and announcements to submitting academic queries and receiving admin support in real time.

🎯 Vision
To build a smart, responsive digital ecosystem that empowers students and simplifies campus interactions through intelligent automation and real-time connectivity.by using voice or Text.

🔑 Core Features
📅 Timetable Access

Students can instantly view timetables by selecting their branch, year, and section.

Timetables are uploaded by admins and served dynamically.

📢 Announcements

College-wide announcements posted by admin.

Students can read the latest academic and event-related updates in one place.

❓ Smart Query Submission

Students can submit academic or general queries.

Queries are answered automatically using a knowledge base or routed to admins for personalized responses.

📬 Admin Notifications

Admin is notified of unhandled queries.

Once resolved, the student receives an email with the admin’s response.

🧑‍💻 Admin Dashboard

Admins can manage users, view and resolve queries, edit student records, and update college-level data.

Includes password reset functionality via email OTP verification.

🗺️ Campus Map Navigation

Interactive maps for locations like library, canteen, auditorium.

Helps new students easily find key facilities on campus.

📚 Academic Calendar

Provides a visual calendar of important academic dates and events.

Students can plan accordingly for exams and submissions.

📂 Query Logs & Student History

Students can view previously asked queries and track their response status.

Improves transparency and reduces redundancy.

⚙️ Technologies Used
Frontend:

HTML5, CSS3 for structure and styling

JavaScript (vanilla) for interactive elements and form validation

Backend:

Flask (Python) for server-side logic and routing

SQLite as the lightweight database for students, queries, and timetable data

Email Integration:

smtplib and email.message in Python to send OTPs and admin replies

Session Management:

Flask sessions for login authentication and access control

📁 Project Structure
php
Copy
Edit
smart-campus-assistant/
├── app.py                  # Main Flask app
├── mgit_assistant.py       # Handles smart query responses
├── users.db                # SQLite database file
├── static/
│   ├── css/                # Stylesheets
│   ├── js/                 # Optional JavaScript files
│   └── pdfs/               # Uploaded timetable PDFs
├── templates/              # HTML templates
│   ├── login.html, register.html, dashboard.html ...
│   ├── admin_manage_users.html, admin_notifications.html ...
│   └── view_queries.html, timetable.html ...
└── README.md
🚀 How to Run the Project
Clone the repository:

bash
Copy
Edit
git clone https://github.com/vishnuvardhandumma/vishnu_smart_campus.git
cd vishnu_smart_campus
Install Flask and dependencies:

bash
Copy
Edit
pip install flask
Run the app:

bash
Copy
Edit
python app.py
Open http://localhost:5000 in your browser.

🔮 Future Enhancements
Add role-based login (e.g., faculty, staff)

AI-powered query suggestions

Timetable reminders via email/SMS

Real-time notifications with WebSockets

PWA support for offline access

Smart Campus Assistant — Bringing your campus to your fingertips. 🎓💡

