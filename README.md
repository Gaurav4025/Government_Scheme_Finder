Government Scheme Finder

An AI-powered web application that helps users discover relevant government schemes based on their profile, eligibility criteria, and preferences.

Built using FastAPI, Jinja templates, and a structured backend architecture.

Features:

-Intelligent scheme discovery

-User profile-based recommendations

-Conversation-based interaction

-File upload support

-Conversation history management

-Secure session handling

-Clean modular backend structure

Project Architecture:
GOVERNMENT_SCHEME_FINDER/
│
├── app/
│   ├── application.py        # Main FastAPI app
│   ├── repo.py               # Database interaction layer
│   ├── common/               # Logger, security, custom exceptions
│   ├── components/           # Core business logic
│   ├── config/               # Configuration management
│   ├── db/                   # Database setup
│   ├── profile/              # User profile handling
│   ├── documents/            # Document processing
│   ├── templates/            # Jinja2 HTML templates
│   └── static/               # Static files (CSS, JS)
│
├── frontend/                 # Frontend assets (if separate)
├── data/                     # Data storage
├── storage/                  # Uploaded files
├── logs/                     # Application logs
├── requirements.txt
└── .env
