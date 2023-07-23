# PigeonHub

PigeonHub is a social media website built using Flask, SQLite, and Jinja templates. It allows users to sign up, log in, post Flits, view user profiles, and interact with Flits.

## Features

- User sign up and login functionality
- Posting and viewing Flits
- User profile pages
- Formatting Flits with bold, italic, and underline text
- Logout functionality

## Prerequisites

- Python 3.7 or higher
- Flask 2.0 or higher
- SQLite (included with Python)

## Installation

1. Clone the repository:

``
git clone <repository_url>
``

2. Navigate to the project directory:

``
cd Fliter
``

3. Create a virtual environment:

``
python3 -m venv venv
``

4. Activate the virtual environment:

``
source venv/bin/activate
``

5. Install the dependencies:

``
pip install -r requirements.txt
``

6. Run the application:

``
python main.py
``

7. Open your web browser and visit `http://localhost:5000` to access Fliter.

## To-Do List

[x] Search functionality to find users and Flits
[x] Direct Messages (DMs) functionality
[ ] Following functionality
[ ] Implement an algorithm for personalized Flit recommendations (similar to Twitter's algorithm)
[ ] Add user profile picture upload functionality
[ ] Enhance the design and styling of the application
[ ] Implement reFlits and likes functionality
[ ] Integrate real-time updates using WebSocket (e.g., new Flits, notifications)
[ ] Implement pagination for Flits on the home page and user profiles
[ ] Implement trending topics and hashtags
[ ] Add user settings and account management features
[ ] Implement user authentication using OAuth (e.g., Google, Facebook, Twitter)
[ ] Add support for multimedia content (images, videos) in Flits
[ ] Implement user mentions and notifications
[ ] Implement hashtag autocompletion and suggestions
[ ] Improve security (e.g., password hashing, CSRF protection)
[ ] Implement email notifications for important events (e.g., new followers, mentions)
[ ] Perform code optimization and refactoring for better performance and maintainability

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
