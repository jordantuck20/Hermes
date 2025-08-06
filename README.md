# Hermes Discord Bot

A Discord bot that automatically fetches and posts game news from the Steam API to subscribed Discord servers.

---

### Key Features:

- Automated News Updates: Periodically checks the Steam API for new game announcements.
- Subscription Management: Users can easily subscribe and unsubscribe to game news directly from Discord.
- Server-Specific Configuration: Allows administrators to set a dedicated news channel for each server.
- Database-Driven: Stores all configurations and subscriptions in a MySQL database for persistence.
- Secure Deployment: Uses environment variables for sensitive information and is managed by PM2 on a Linux server.

---

### Technologies Used

- Python: The core programming language.
- discord.py: The bot framework.
- MySQL: The relational database for all data persistence.
- SQLAlchemy: The ORM used to manage database interactions.
- Steam API: The external API for fetching game news.
- requests: The library for making API calls.
- python-dotenv: For managing environment variables.
- Linux (Ubuntu): The operating system of the deployment server.
- PM2: The process manager for keeping the bot running 24/7.
- pytest: The framework used for unit and integration testing.

---

### Getting Started

This section is for other developers who want to run the bot locally.

1. **Clone the Repository**

   ```bash
   git clone git@github.com:your-username/your-repo-name.git
   ```

2. **Set Up the Environment**

   - Create a virtual environment: `python -m venv venv`
   - Activate it: `source venv/Scripts/activate` (Windows) or `source venv/bin/activate` (Linux/macOS)
   - Install dependencies: `pip install -r requirements.txt`

3. **Configure Credentials**

   - Create a .env file in the root of the project with your Discord bot token and database credentials.

4. **Run the Bot**
   - `python bot.py`

---

### License

This project is licensed under the MIT License. See the `LICENSE` file for details.
