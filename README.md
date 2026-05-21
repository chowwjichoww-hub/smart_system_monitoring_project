# 🚀 Smart System Monitoring Dashboard

A professional-grade system monitoring application with user authentication, admin panel, real-time metrics, and historical data visualization.

## ✨ Features

### 🔐 Authentication & Security
- User registration with email validation
- Secure login with password hashing (Werkzeug)
- Session management with Flask-Login
- Role-based access control (Admin/User)

### 📊 Admin Panel
- View all registered users
- Monitor user login history with IP addresses
- Track browser and OS information
- Manage user roles (promote/demote admins)
- Real-time login statistics

### 📧 Email Notifications
- Admin receives email on new user registration
- Admin gets notified of user logins with details:
  - Username and email
  - IP address
  - Browser and OS information
  - Login timestamp

### 📈 Beautiful Dashboard
- **Real-time Metrics**: CPU, RAM, Disk, Health Score
- **Interactive Charts**: Powered by Chart.js
- **Time-based Filters**: Today, Weekly, Monthly
- **Auto-refresh**: Updates every 30 seconds
- **Responsive Design**: Works on mobile and desktop

### 🎨 Modern UI
- Beautiful gradient backgrounds
- Smooth animations and transitions
- Font Awesome icons
- Professional color scheme
- Mobile-friendly layout

## 📋 Requirements

```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.2
psutil==5.9.5
gunicorn==21.2.0
user-agents==2.2.0
python-dotenv==1.0.0
```

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd smart_system_monitoring_project
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```
SECRET_KEY=your-secret-key-here-change-in-production
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
ADMIN_EMAIL=admin@example.com
```

### 5. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 📱 Usage

### First Time Setup
1. Register a new account
2. Login with your credentials
3. View your system metrics on the dashboard

### Admin Setup
1. Register a user account
2. Manually set `is_admin=True` in the database for that user
3. Login and access the admin panel

### Email Notifications
For Gmail SMTP:
1. Enable "Less secure app access" or use an "App Password"
2. Get your App Password from Google Account settings
3. Set `EMAIL_PASSWORD` in `.env`

## 🚀 Deployment

### Deploy to Render

1. Push your project to GitHub
2. Go to [Render.com](https://render.com)
3. Create a new Web Service
4. Connect your GitHub repository
5. Set environment variables:
   - `PYTHON_VERSION`: 3.9
   - `SECRET_KEY`: Generate a strong secret
   - `EMAIL_ADDRESS`: Your email
   - `EMAIL_PASSWORD`: Your app password
   - `ADMIN_EMAIL`: Admin email

6. Deploy!

Your app will be live at: `https://your-project-name.onrender.com`

### Deploy to Heroku

1. Install Heroku CLI
2. Run:
```bash
heroku login
heroku create your-app-name
heroku config:set SECRET_KEY=your-secret-key
heroku config:set EMAIL_ADDRESS=your-email@gmail.com
heroku config:set EMAIL_PASSWORD=your-app-password
heroku config:set ADMIN_EMAIL=admin@example.com
git push heroku main
```

## 📚 API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /login` - Login
- `GET /logout` - Logout

### User Dashboard
- `GET /dashboard` - User dashboard
- `GET /api/system-metrics` - Get current metrics
- `GET /api/history?period=today|weekly|monthly` - Get historical data

### Admin Panel
- `GET /admin` - Admin dashboard
- `GET /api/admin/user-details/<user_id>` - Get user details
- `POST /api/admin/make-admin/<user_id>` - Promote user to admin
- `POST /api/admin/remove-admin/<user_id>` - Remove admin privileges

## 🗄️ Database Schema

### User Model
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email
- `password`: Hashed password
- `is_admin`: Boolean flag
- `created_at`: Registration timestamp

### LoginHistory Model
- `id`: Primary key
- `user_id`: Foreign key to User
- `login_time`: Login timestamp
- `ip_address`: Client IP
- `browser`: Browser and OS info

### SystemData Model
- `id`: Primary key
- `user_id`: Foreign key to User
- `cpu`: CPU usage percentage
- `ram`: RAM usage percentage
- `disk`: Disk usage percentage
- `health_score`: System health score
- `timestamp`: Data collection time

## 🔒 Security Features

- Password hashing with Werkzeug
- CSRF protection with Flask
- SQL injection prevention with SQLAlchemy ORM
- Session management
- Admin-only pages with decorator
- IP and browser logging for security

## 📧 Email Configuration

### Gmail SMTP Setup
1. Enable 2-Factor Authentication on your Google Account
2. Generate an App Password
3. Use the App Password in `.env`

### Other Email Providers
Modify the SMTP configuration in `app.py` if using a different provider:
```python
server = smtplib.SMTP_SSL("smtp.your-provider.com", 465)
```

## 🐛 Troubleshooting

### Email not sending
- Check email credentials in `.env`
- Verify Gmail App Password is correct
- Check firewall/network settings
- Review application logs for errors

### Database errors
- Delete `monitoring.db` to reset the database
- Run `python app.py` to reinitialize

### Charts not loading
- Clear browser cache
- Check browser console for errors
- Ensure Chart.js is loaded from CDN

## 📝 License

This project is open source and available under the MIT License.

## 👨‍💻 Support

For issues, questions, or suggestions, please create an issue in the repository.

---

**Made with ❤️ for system monitoring**
