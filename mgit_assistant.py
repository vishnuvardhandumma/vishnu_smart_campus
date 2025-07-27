import re
import os
import webbrowser
from flask import url_for
import sqlite3
from datetime import datetime
import string



# Global Maps
branch_map = {
    'cse': 'cse', 'csc': 'cse', 'cs':'cse',
    'ece': 'ece',
    'eee': 'eee',
    'it': 'it',
    'civil': 'civil',
    'mechanical': 'mechanical',
    'mech': 'mechanical'
}

section_map = {
    '1': '1', 'one': '1',
    '2': '2', 'two': '2', 'to':'2',
    '3': '3', 'three': '3',
    '4': '4', 'four': '4'
}

year_map = {
    '1st': '1styear', 'first': '1styear',
    '2nd': '2ndyear', 'second': '2ndyear',
    '3rd': '3rdyear', 'third': '3rdyear',
    '4th': '4thyear', 'fourth': '4thyear'
}


def log_query(query, response):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO query_logs (query, response, timestamp) VALUES (?, ?, ?)",
              (query, response, datetime.now()))
    conn.commit()
    conn.close()

def take_command_mgit(query,student_email=None):
    query = query.lower().strip()
    print("DEBUG: User query ->", query)

    # Simple Text Responses
    responses = {
        "hello": "Hello! How can I assist you today?",
        "hi": "Hello! How can I assist you today?",
        "hey": "Hello! How can I assist you today?",
        "how are you": "I'm just a program, but I'm here to help you!",
        "how are you doing": "I'm just a program, but I'm here to help you!",
        "who are you": "I am the MGIT Smart Assistant, here to help you with MGIT-related queries!",
        "what is your name": "I am the MGIT Smart Assistant, here to help you with MGIT-related queries!",
        "hu r u": "I am the MGIT Smart Assistant, here to help you with MGIT-related queries!",
        "thank you": "You're welcome! Happy to help. 😊",
        "thanks": "You're welcome! Happy to help. 😊",
        "thank": "You're welcome! Happy to help. 😊",
        "who made you": "I was developed by MGIT students to assist with campus-related information!",
        "tell me a joke": "Why do programmers prefer dark mode? Because light attracts bugs! 😂",
        "make me laugh": "Why do programmers prefer dark mode? Because light attracts bugs! 😂",
        "bye": "Goodbye! Have a great day at MGIT. 😊",
        "goodbye": "Goodbye! Have a great day at MGIT. 😊"
    }
    
    
    

    if query in responses:
        return responses[query]

    # Website & Map Queries
    if re.search(r'\b(mgit|mgit website|open mgit website|mgit site|open mg it website)\b', query):
       webbrowser.open("https://mgit.ac.in")
       return "Opening MGIT website."

   # Campus Location Queries (put these above the general ones)
   # elif re.search(r'\bwhere is\b.*\blibrary\b', query):
   #     webbrowser.open("http://127.0.0.1:5000/library_map?location=library")
    #    return "Showing the MGIT Library on the campus map."

    if re.search(r'\bcanteen\b', query):
        if re.search(r'\btiming|hours|open\b', query):
            return "The MGIT canteen is open from 9:00 AM to 6:00 PM on all working days."
        webbrowser.open("http://127.0.0.1:5000/canteen_map?location=canteen")
        return "MGIT canteen is located in the A block ground floor ."

    elif re.search(r'\bwhere is\b.*\bauditorium\b', query):
        webbrowser.open("http://127.0.0.1:5000/auditorium_map?location=auditorium")
        return "Showing the MGIT auditorium on the campus map."

# (Add other locations similarly...)

# Now the general Library query
    elif re.search(r'\blibrary\b', query):
        if re.search(r'\btiming|hours|open\b', query):
            return "The MGIT Library is open from 9:00 AM to 6:00 PM on all working days."
        else:
            webbrowser.open("http://127.0.0.1:5000/library_map?location=library")
            return "MGIT Library is located in the B block 1st floor and provides various academic resources."
        
    elif re.search(r'\b(id card|identity card|college id)\b', query):
        if re.search(r'\bapply|application|how|get\b', query):
            return "To apply for an ID card in MGIT, please visit your department administrator's office. Collect the application form, fill it with your details, attach a passport size photo, and submit it. You’ll be informed when your card is ready."
        else:
            webbrowser.open("http://127.0.0.1:5000/contact_admin")
            return "For ID card-related queries, please visit your department administrator's office or the main college office for further assistance."
    elif re.search(r'\bevents|hackathon|fest\b', query):
        return "Check the MGIT website or follow the official Instagram page for the latest event updates."
    elif re.search(r'\becet|lateral entry\b', query):
        return "MGIT accepts lateral entry admissions through ECET for diploma students."
    
    
    elif re.search(r'\bcreated|developed\b', query):
        return "i was creaed or developed by the varun chandhupatla and vishnu vardhan dumma ,cse branch, MGIT"
    
    elif re.search(r'\|explain about you| tell about your self|what about this project| assistant\b', query):
        return "This is a web-based assistant developed for Mahatma Gandhi Institute of Technology (MGIT) that helps both students and administrators. It allows students to view their timetables based on their branch, section, and year. For admins, it offers tools to upload, manage, and view timetables, respond to student queries, and manage admin users.."

    elif re.search(r'\b(attendance|attendence|atttendance)\b', query):
        if re.search(r'\b(forgot|reset|recover)\b', query) and re.search(r'\b(username|password)\b', query):
            return (
                "If you've forgotten your Winnou username or password:\n"
                "1. Go to https://mvsr.winnou.net/\n"
                "2. Click on the 'Forgot Password' link.\n"
                "3. Enter your registered email or mobile number.\n"
                "4. Follow the instructions sent to your email or phone.\n"
                "For further help, contact the admin department or your class coordinator."
            )
        else:
            webbrowser.open("https://mgit.winnou.net/")
            return (
                "Opening Winnou portal to check your attendance.\n"
                "After the portal opens:\n"
                "1. Login using your student credentials.\n"
                "2. Go to the 'Attendance' section in the menu.\n"
                "3. Select the semester and subjects to view your attendance details."
            )

    elif re.search(r'\bexam\b', query):
        if re.search(r'\bwhen|schedule|date\b', query):
            return "Check the MGIT website or your department notice board for the latest exam schedule."
        elif re.search(r'\bresults\b', query):
            webbrowser.open("https://mgit.ac.in/exam-results")
            return "Opening MGIT exam results page."
        return "MGIT exams are conducted as per the academic calendar."

    elif re.search(r'\bfaculty\b', query):
        return "Find faculty details on the MGIT website under the 'Faculty' section."
    
    # Informational Queries
    elif re.search(r'\bdepartments\b', query):
        return "MGIT offers CSE, IT, ECE, EEE, Mechanical, Civil, and more."

    elif re.search(r'\bbus|transport|how to reach mgit\b', query):
        return "MGIT is well connected by TSRTC buses. Check TSRTC schedules for accurate timings."

    elif re.search(r'\bhostel\b', query):
        return "MGIT does not have an official hostel, but students stay in nearby private hostels and PGs in Gandipet."

    elif re.search(r'\bwhere is mgit|mgit location\b', query):
        webbrowser.open("https://www.google.com/maps/place/Mahatma+Gandhi+Institute+of+Technology")
        return "Opening MGIT location on Google Maps."

    elif re.search(r'\bplacements\b', query):
        return "MGIT has a strong placement cell. Companies like TCS, Infosys, and Wipro recruit students every year."

    elif re.search(r'\binternship\b', query):
        return "For internships, check with your department or visit the placement cell."

    elif re.search(r'\bsports\b', query):
        return "MGIT has a playground, a basketball court, and an indoor sports area for table tennis and chess."

    elif re.search(r'\bfee payment\b', query):
        return "Pay your MGIT fees online through the official website or at the accounts office."

    elif re.search(r'\bscholarship\b', query):
        return "MGIT offers scholarships based on merit and financial need. Contact the administration for details."

    elif re.search(r'\bclass timings\b', query):
        return "MGIT classes usually start at 9:30 AM and end at 4:30 PM. Check your department schedule for details."

    elif re.search(r'\bclubs\b', query):
        return "MGIT has clubs like Coding Club, Robotics Club, Music Club, Literary Club, and more."

    elif re.search(r'\blost\b', query):
        return "Check with the college administration or security office for lost and found items."

    elif re.search(r'\bwifi|wi-fi\b', query):
        return "Connect to MGIT Wi-Fi using credentials from the IT department."

    elif re.search(r'\bproject room\b', query):
        return "Use project labs in your department. Contact your faculty advisor for access."
    

    elif re.search(r'\btime table\b', query):
        branch = next((branch_map[b] for b in branch_map if b in query), None)
        section = next((section_map[s] for s in section_map if re.search(rf'\b{s}\b', query)), None)
        year = next((year_map[y] for y in year_map if y in query), None)

        if branch and section and year:
            file_name = f"{branch}_{section}_{year}_timetable.pdf"
            file_path = f"static/pdfs/{file_name}"

            if os.path.exists(file_path):
                webbrowser.open_new_tab(url_for('static', filename=f"pdfs/{file_name}", _external=True))
                readable = f"{branch.upper()} {section} {year.replace('year', ' Year').title()}"
                return f"Opening {readable} Timetable."
            else:
                return f"Timetable for {branch.upper()} {section} {year.replace('year', ' Year').title()} is not available yet."

        else:
            return "Please say your full query like 'CSE 1 first year timetable'."
        
    response_from_logs = search_query_logs(query)
    if response_from_logs:
        return response_from_logs
    
    if student_email:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notifications (student_email, query) VALUES (?, ?)", (student_email, query))
        conn.commit()
        conn.close()
        return "Your query has been forwarded to the admin. You'll get a reply soon!"
    
    

    return "I'm sorry, I didn't understand that. Could you please rephrase?"


def handle_query(user_query):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Try to find a matching query in query_logs
    c.execute("SELECT response FROM query_logs WHERE LOWER(query) = LOWER(?)", (user_query,))
    result = c.fetchone()
    conn.close()

    if result:
        response = result[0]
        # Check if response is a URL
        if response.startswith("http://") or response.startswith("https://"):
            webbrowser.open(response)
            return f"Opening {response}"
        else:
            return response
    else:
        return "Sorry, I don't have an answer for that yet."

# Example usage
user_input = "open mgit website"
print(handle_query(user_input))





def normalize_query(query):
    query = query.lower().strip()
    query = query.translate(str.maketrans('', '', string.punctuation))
    return query

def handle_student_query(student_email, query):
    # First check: predefined responses
    responses = {
        "when is the exam": "The exam schedule is usually released by the exam cell. Please check the academic calendar.",
        "what is the timetable": "You can view your timetable from the Timetable section.",
        "academic calendar": "You can download the academic calendar from the Academic section."
    }

    for key in responses:
        if key in query.lower():
            return responses[key]

    # Second check: search from previous query_logs
    previous_response = search_query_logs(query)
    if previous_response:
        return previous_response

    # Unknown query → Save to notifications
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO notifications (student_email, query, status, timestamp)
        VALUES (?, ?, 'Pending', ?)
    """, (student_email, query, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

    return "Your query has been forwarded to the admin. You will get a response soon."
def search_query_logs(user_query):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Try partial match search — case insensitive
    c.execute("SELECT response FROM query_logs WHERE LOWER(query) LIKE ?", ('%' + user_query.lower() + '%',))
    result = c.fetchone()

    conn.close()

    if result:
        response = result[0]
        # If response is a URL, open it
        if response.startswith("http://") or response.startswith("https://"):
            webbrowser.open(response)
            return f"Opening {response}"
        else:
            return response

    return None  # No match found
