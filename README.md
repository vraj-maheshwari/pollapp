 Flask Polling Application
- Create polls with 2–4 options 
- Polls expire after 24 hours
- Option to hide results until the poll ends  
- Anonymous voting with unique vote tokens & device/IP hashing  
- Live updates via WebSockets (Socket.IO)  
- Share polls with a link or QR code 
  


1. Install dependencies

pip install -r requirements.txt


2. Run the app

python app.py


├── app.py              # Main application file
├── poll.db             # SQLite database (auto-created on first run)
├── templates/          # HTML templates
│   ├── create.html
│   ├── poll.html
│   ├── results.html
│   └── share.html
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation

