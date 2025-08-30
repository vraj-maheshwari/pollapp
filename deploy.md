# 🚀 Deployment Guide

## 🎯 Best Deployment Options (Ranked)

### 1. 🥇 Railway (Recommended - Full Features)
**✅ Supports WebSockets, persistent storage, real-time updates**

```bash
# 1. Connect GitHub repo to Railway
# 2. Set environment variables in Railway dashboard:
SECRET_KEY=your-secret-key-here
FLASK_ENV=production

# 3. Deploy automatically from GitHub
```

**Features**: Full real-time WebSocket support, persistent database, creator dashboard

### 2. 🥈 Render (Great Alternative)
**✅ Supports WebSockets, persistent storage**

```bash
# 1. Create Web Service from GitHub
# 2. Build Command: pip install -r requirements.txt
# 3. Start Command: gunicorn --worker-class eventlet -w 1 app:app
# 4. Environment Variables:
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
```

### 3. 🥉 Heroku (Classic Choice)
**✅ Supports WebSockets, but database resets on dyno restart**

```bash
heroku create your-poll-app
heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(16))')
heroku config:set FLASK_ENV=production
git push heroku main
```

### 4. ⚠️ Vercel (Limited Features)
**❌ No WebSockets, ❌ No persistent database, ✅ Fast deployment**

```bash
# Already configured with vercel.json
# Uses app_vercel.py (polling instead of WebSockets)
vercel --prod
```

**Limitations**: No real-time updates, database resets between requests

## 📋 Deployment Comparison

| Platform | Real-time | Database | Setup | Cost |
|----------|-----------|----------|-------|------|
| Railway  | ✅ Full   | ✅ Persistent | Easy | Free tier |
| Render   | ✅ Full   | ✅ Persistent | Easy | Free tier |
| Heroku   | ✅ Full   | ⚠️ Resets | Easy | Free tier |
| Vercel   | ❌ Polling | ❌ Temporary | Instant | Free |

## 🚀 Quick Deploy Commands

### Railway (Recommended)
1. Push to GitHub
2. Connect repo to Railway
3. Set environment variables
4. Deploy automatically

### Render
```bash
# Connect GitHub repo, then:
# Build: pip install -r requirements.txt
# Start: gunicorn --worker-class eventlet -w 1 app:app
```

### Heroku
```bash
heroku create your-poll-app
heroku config:set SECRET_KEY=$(openssl rand -hex 32)
git push heroku main
```

### Vercel (Instant)
```bash
vercel --prod
```

## 🎬 Demo URLs Structure

After deployment, you'll have:

```
Your App URLs:
├── https://your-app.railway.app/              # Create polls
├── https://your-app.railway.app/poll/123      # Vote on poll
├── https://your-app.railway.app/results/123   # View results  
├── https://your-app.railway.app/creator/123/secret # Creator dashboard
└── https://your-app.railway.app/api/results/123    # JSON API
```

## 🧪 Testing Your Deployment

1. **Create Poll**: Visit your deployed URL
2. **Get Links**: Copy both public poll + creator dashboard links
3. **Multi-device Test**: Vote from phone + computer
4. **Real-time Check**: Watch live updates (Railway/Render/Heroku)
5. **Insights Test**: Get 20+ votes to see AI insights
6. **QR Code**: Test QR code sharing

## 🎥 Perfect Demo Flow

1. **Create**: "Pizza vs Burger vs Tacos vs Sushi" 
2. **Share**: Show QR code + social media preview
3. **Vote**: Use 2 devices simultaneously
4. **Real-time**: Show live progress bars updating
5. **Analytics**: Open creator dashboard
6. **Insights**: Demonstrate AI insights after 20+ votes
7. **Mobile**: Show mobile responsiveness

## 🔧 Environment Variables

```bash
# Required for all platforms
SECRET_KEY=your-32-character-secret-key
FLASK_ENV=production

# Optional
PORT=5000  # Auto-set by most platforms
```

## 📊 Performance Notes

- **Railway/Render**: Best for demos, full features
- **Heroku**: Good but database resets on sleep
- **Vercel**: Fastest deploy but limited functionality
- **For production**: Consider PostgreSQL instead of SQLite

---

**🎯 For your Loom demo: Use Railway or Render for full real-time features!**