# 🗳️ Advanced Flask Polling Application

A feature-rich polling application with real-time updates, creator analytics, and AI-powered insights.

## ✨ Features

- **Smart Poll Creation**: Auto-detect options from questions (e.g., "Pizza vs Burger")
- **Real-time Results**: Live updates via WebSockets
- **Creator Dashboard**: Private analytics and management interface
- **AI Insights**: Auto-generated insights after 20+ votes
- **Social Sharing**: Open Graph tags + QR codes for easy sharing
- **Anonymous Voting**: Secure voting with device fingerprinting
- **Auto-expiry**: Polls automatically expire after 24 hours
- **Mobile Responsive**: Works perfectly on all devices

## 🚀 Quick Start

### Local Development

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Run the application**
```bash
python app.py
```

3. **Open your browser**
```
http://localhost:5000
```

### Production Deployment

#### Heroku (Recommended)

1. **Create Heroku app**
```bash
heroku create your-poll-app-name
```

2. **Set environment variables**
```bash
heroku config:set SECRET_KEY=your-secret-key-here
heroku config:set FLASK_ENV=production
```

3. **Deploy**
```bash
git push heroku main
```

#### Railway

1. **Connect your GitHub repo to Railway**
2. **Set environment variables**:
   - `SECRET_KEY`: Your secret key
   - `FLASK_ENV`: production

#### Render

1. **Create new Web Service**
2. **Build Command**: `pip install -r requirements.txt`
3. **Start Command**: `gunicorn --worker-class eventlet -w 1 app:app`

## 📁 Project Structure

```
├── app.py                      # Main Flask application
├── poll.db                     # SQLite database (auto-created)
├── templates/
│   ├── create.html            # Poll creation form
│   ├── poll.html              # Voting interface
│   ├── results.html           # Public results view
│   ├── share.html             # Sharing interface
│   └── creator_dashboard.html # Creator analytics
├── requirements.txt           # Python dependencies
├── Procfile                   # Heroku deployment config
├── runtime.txt               # Python version specification
└── README.md                 # This file
```

## 🎯 Usage Flow

1. **Create Poll** → Get public poll link + private creator link
2. **Share Poll** → Via link, QR code, or social media
3. **Collect Votes** → Real-time updates for all viewers
4. **View Analytics** → Creator dashboard with insights (20+ votes)
5. **Auto-expire** → Poll closes after 24 hours

## 🔗 API Endpoints

- `GET /` - Create new poll
- `GET /poll/<id>` - Vote on poll
- `GET /results/<id>` - View results
- `GET /share/<id>` - Share poll
- `GET /creator/<id>/<secret>` - Creator dashboard
- `GET /api/results/<id>` - JSON results API
- `GET /qr/<id>` - QR code image

## 🛠️ Environment Variables

- `SECRET_KEY`: Flask secret key (required for production)
- `FLASK_ENV`: Set to 'production' for production deployment
- `PORT`: Port number (auto-set by most platforms)

## 📊 Features in Detail

### Creator Dashboard
- Real-time vote tracking
- Vote timeline and analytics
- AI-generated insights
- Private management interface

### AI Insights (20+ votes)
- Identifies clear winners vs close races
- Participation level analysis
- Competition analysis between options
- Automatically generated after reaching threshold

### Social Sharing
- Open Graph meta tags for rich previews
- QR codes for easy mobile sharing
- Copy-to-clipboard functionality
- Mobile-optimized sharing

## 🔒 Security Features

- Anonymous voting with device fingerprinting
- Vote token system prevents duplicate voting
- Creator secret links for dashboard access
- Input validation and sanitization

## 📱 Mobile Support

- Fully responsive Bootstrap design
- Touch-friendly voting interface
- QR code scanning support
- Real-time updates on mobile

## 🎨 Customization

The application uses Bootstrap 5 for styling. You can easily customize:
- Colors and themes in the HTML templates
- Poll expiry time in `app.py`
- Insight generation logic
- Vote limits and restrictions

