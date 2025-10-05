# AI News Hub

A modern, AI-powered news aggregator built with Django and Bootstrap 5. Get personalized news recommendations, AI-generated insights, and browse news from multiple trusted sources across 6 categories.

## Features

### 🤖 AI-Powered
- **Personalized Recommendations**: AI curates news based on your reading history
- **News Insights**: Get AI-generated analysis of trending topics
- **Smart Categorization**: Automatic content categorization and tagging

### 📰 News Aggregation
- **12 News Sources**: TechCrunch, The Verge, Indian Express, Economic Times, and more
- **6 Categories**: Technology, Economy, Sports, Politics, Lifestyle, Entertainment
- **Real-time Updates**: Fresh content scraped regularly

### 👤 User Features
- **User Authentication**: Secure registration, login, and profile management
- **Comment System**: Rate and comment on articles (1-5 stars)
- **Profile Customization**: Upload profile pictures and manage preferences
- **Reading History**: Track your engagement and improve recommendations

### 🎨 Modern UI/UX
- **Bootstrap 5**: Modern, responsive design
- **Mobile-First**: Optimized for all devices
- **Dark Mode Ready**: Automatic theme detection
- **Accessibility**: WCAG compliant design

## Tech Stack

- **Backend**: Django 4.2
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **AI**: Google Gemini API
- **Deployment**: Railway
- **Scraping**: curl-cffi, lxml
- **Styling**: Bootstrap 5 + Custom CSS

## Quick Start

### Prerequisites
- Python 3.11+
- pip
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sudhan247/news_scraper.git
   cd news_scraper
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

5. **Run migrations**
   ```bash
   cd app
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000` to access the application.

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
GEMINI_API_KEY=your-gemini-api-key
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Gemini API Setup

1. Get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add it to your `.env` file as `GEMINI_API_KEY`

### Email Configuration

For password reset functionality:
1. Enable 2-factor authentication on your Gmail account
2. Generate an app password
3. Add your email and app password to `.env`

## Deployment

### Railway Deployment

1. **Connect to Railway**
   ```bash
   railway login
   railway link
   ```

2. **Set environment variables**
   ```bash
   railway variables set SECRET_KEY=your-production-secret-key
   railway variables set DEBUG=False
   railway variables set GEMINI_API_KEY=your-api-key
   # Add other production variables
   ```

3. **Deploy**
   ```bash
   railway up
   ```

The app is configured with:
- ✅ PostgreSQL database
- ✅ Static file serving (Whitenoise)
- ✅ Production security settings
- ✅ Environment-based configuration

## Project Structure

```
news_aggregator/
├── app/
│   ├── config/           # Django settings & URLs
│   ├── news/            # Main application
│   │   ├── models.py    # Article, Comment, Profile models
│   │   ├── views.py     # All views (news, auth, AI)
│   │   ├── forms.py     # User forms
│   │   ├── scraper.py   # News scraping logic
│   │   ├── gemini_client.py  # AI functionality
│   │   └── admin.py     # Admin configuration
│   ├── templates/       # HTML templates
│   ├── static/         # CSS, JS, images
│   └── manage.py
├── requirements.txt
├── Procfile           # Railway deployment
├── runtime.txt       # Python version
└── README.md
```

## News Sources

### Technology
- **TechCrunch**: Latest tech news and startup coverage
- **The Verge**: Technology, science, art, and culture

### Economy
- **Indian Express**: Business and economy news
- **Economic Times**: Market updates and financial news

### Sports
- **Indian Express**: Sports coverage
- **Hindustan Times**: Sports news and updates

### Politics
- **Economic Times**: Political developments
- **New York Times**: Political news and analysis

### Lifestyle
- **Indian Express**: Lifestyle and wellness
- **Fox News**: Health and lifestyle content

### Entertainment
- **Indian Express**: Entertainment news
- **Variety**: Film and entertainment industry

## API Endpoints

- `/` - Home page
- `/dashboard/` - User dashboard
- `/news/<category>/` - Category-specific news
- `/article/<id>/` - Article detail view
- `/insights/` - AI news insights
- `/personalized/` - Personalized recommendations
- `/api/article/<id>/summary/` - AI article summary
- `/api/sentiment/` - News sentiment analysis

## Admin Features

Staff users can:
- Access Django admin at `/admin/`
- Refresh news manually via dashboard
- Manage users, articles, and comments
- View analytics and user engagement

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue on GitHub or contact the development team.

---

Built with ❤️ using Django and AI technology.