# Neurobit

Neurobit is a training program and web platform focused on helping teenagers and young adults start a career in software development. The site is built with **Django** and uses **Webpack** to bundle the front‑end assets. It provides information about the program, learning paths, mentoring, pricing and includes an application form for prospective students.

## Features

- Multi‑page website with a modern UI
- Application form with validation and file upload
- "Learning path" quiz that produces a radar chart with Chart.js
- Admin interface powered by [django-unfold](https://github.com/unfoldadmin/django-unfold)
- Bilingual content (English/Farsi) with language toggle
- Responsive layout with light/dark theme support

## Technology Stack

- **Python 3.12** and [Django 5](https://www.djangoproject.com/)
- **Node.js** and [Webpack](https://webpack.js.org/) for asset bundling
- [webpack-bundle-tracker](https://github.com/django-webpack/django-webpack-loader) for Django integration
- [Chart.js](https://www.chartjs.org/) for charts in the learning path quiz
- [jdatetime](https://github.com/slashmili/python-jalali) for Persian date handling
- [django-unfold](https://github.com/unfoldadmin/django-unfold) for the admin UI

## Requirements

- Python >= 3.12
- Node.js >= 18 (v20 tested)
- A database (SQLite by default, PostgreSQL in production)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://example.com/neurobit.git
   cd neurobit
   ```
2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Install Node dependencies and build assets**
   ```bash
   npm install
   npm run build   # or `npm run watch` during development
   ```
4. **Create a `.env` file** with at least the following variables:
   ```bash
   SECRET_KEY=your-secret-key
   DEBUG=True
   # DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/DBNAME   # optional
   ```
5. **Apply migrations and create a superuser**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000/` to explore the site.

## Running Tests

Run Django's test suite:
```bash
python manage.py test
```
(Only placeholder tests are included at the moment.)

## Project Structure

```
config/      Django settings and URL configuration
pages/       Main application with views, templates and models
static/      Source static files (styles, images, JS)
templates/   Base templates used by the app
webpack_*    Webpack configuration and generated bundles
```

## Deployment

The project includes a `liara.json` file for deploying to [Liara](https://liara.ir/). Adjust the environment variables and disk configuration as needed.

## License

This repository uses the ISC license as defined in `package.json`.

---
Crafted with ❤️ for Iranian youth.
