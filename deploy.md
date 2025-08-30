# 🚀 Deployment Guide

## Quick Deploy Options

### 1. Heroku (Free Tier Available)

```bash
# Install Heroku CLI first
heroku create your-poll-app
heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(16))')
heroku config:set FLASK_ENV=production
git push heroku main
```

**Your URLs:**
- Frontend: `https://your-poll-app.herokuapp.com`
- Backend API: `https://your-poll-app.herokuapp.com/api/results/{poll_id}`

### 2. Railway

1. Connect GitHub repo to Railway
2. Set environment variables:
   - `SECRET_KEY`: Generate with `python -c 'import secrets; print(secrets.token_hex(16))'`
   - `FLASK_ENV`: `production`
3. Deploy automatically

### 3. Render

1. Create Web Service from GitHub
2. Build: `pip install -r requirements.txt`
3. Start: `gunicorn --worker-class eventlet -w 1 app:app`
4. Environment variables:
   - `SECRET_KEY`: Random string
   - `FLASK_ENV`: `production`

### 4. DigitalOcean App Platform

1. Create app from GitHub
2. Set build command: `pip install -r requirements.txt`
3. Set run command: `gunicorn --worker-class eventlet -w 1 app:app`

## Environment Variables Required

```bash
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
```

## Testing Your Deployment

1. **Create a poll** at your deployed URL
2. **Copy both links**: public poll + creator dashboard
3. **Vote from multiple devices/browsers**
4. **Watch real-time updates**
5. **Check insights after 20+ votes**

## Demo Flow for Loom Video

1. **Create Poll**: "Pizza vs Burger vs Tacos"
2. **Share**: Show QR code + copy links
3. **Vote**: Use 2 different devices/browsers
4. **Real-time**: Show live updates
5. **Insights**: Get 20+ votes to trigger AI insights
6. **Expiry**: Show countdown/expiry behavior

## Performance Notes

- SQLite works fine for moderate traffic
- For high traffic, consider PostgreSQL
- WebSocket connections scale with eventlet workers
- Static files served by Flask (consider CDN for production)