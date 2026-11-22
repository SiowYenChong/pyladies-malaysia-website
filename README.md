# 🐍 PyLadies Kuala Lumpur Website 🇲🇾

Welcome to the official GitHub repository for the PyLadies Kuala Lumpur website! This site is the central hub for our community, showcasing events, committee members, and mission.

This project is built using **Django** and styled with **Tailwind CSS**. We welcome contributions from everyone in the Python community, especially women and non-binary individuals.

---

## 🚀 Quick Start (Local Development)

Follow these steps to get a local copy of the project running for development.

### Prerequisites

You must have Python 3.10+ (3.12 matches the Azure runtime) and pip installed.

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/PyLadies-MY/pyladies-my-website.git](https://github.com/PyLadies-MY/pyladies-my-website.git)
    cd pyladies-my-website
    ```

2.  **Create and Activate Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # venv\Scripts\activate   # On Windows
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Site content (images and JSON) is read from `theme/static/` in the repo, so no cloud storage or AWS credentials are needed. Create a file named `.env` in the root directory:
    ```env
    SECRET_KEY='django-insecure-your-secret-key-for-local'
    DEBUG=True
    ```
    `SECRET_KEY` is required. If `DATABASE_URL` is not set, the app uses a local SQLite database.

5.  **Run Migrations (if needed) & Server:**
    ```bash
    python manage.py makemigrations 
    python manage.py migrate
    python manage.py runserver
    ```
    The site should now be running at `http://127.0.0.1:8000/`.

---

## ☁️ Azure App Service (Deployment)

`startup.sh` runs `collectstatic` and then starts Gunicorn on `0.0.0.0:$PORT`. In the Web App's **Configuration > General settings**, set the startup command to `bash startup.sh`.

Required app settings:

| Setting | Value |
| :--- | :--- |
| `SECRET_KEY` | A long random value (required, the app will not start without it) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `<app-name>.azurewebsites.net` |
| `CSRF_TRUSTED_ORIGINS` | `https://<app-name>.azurewebsites.net` |
| `DATABASE_URL` | PostgreSQL connection string (optional; SQLite does not persist on App Service) |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` (installs `requirements.txt` on deploy) |

---

## 📁 Project Structure

Key files and directories for collaborators to understand:

| Path | Description |
| :--- | :--- |
| `config/settings.py` | Django configuration. Reads `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and `DATABASE_URL` from the environment. |
| `theme/views.py` | Contains all page logic (`home`, `about`, `events`, etc.). This is where **content loading and filtering** occurs. |
| `theme/templates/` | Django templates (`home.html`, `about.html`, etc.). Uses Jinja-style syntax and Tailwind classes. |
| `theme/static/images/` | **The site content directories.** Static assets like committee photos, speaker photos, and JSON data files are stored here (e.g., `images/committee/`, `images/events/`). |
| `theme/static/css/` | Tailwind CSS output and custom styles. |

---

## 🤝 How to Contribute

We follow a standard GitHub flow.

### 1. Identify Content Tasks

Most contributions will involve updating static content.

| Task | Location | Details |
| :--- | :--- | :--- |
| **Update Committee** | `theme/static/images/committee/` | Add image files named `firstname-lastname_role.jpg` |
| **Add Events** | `theme/static/images/events/events_data.json` | Edit the JSON file with new event entries. |
| **Add Blog Posts** | `theme/static/images/blog/blog_posts.json` | Edit the JSON file with new post entries. |
| **Code Fixes** | `theme/views.py` & `theme/templates/` | Fix bugs or enhance UI. |

Content changes take effect after they are committed and deployed. Editing files on the live server has no lasting effect.

### 2. Fork and Branch

1.  **Fork** this repository to your own GitHub account.
2.  **Create a new branch** for your work:
    ```bash
    git checkout -b feature/your-feature-name
    ```

### 3. Make Changes

Implement your changes, whether it's updating JSON files, adding templates, or fixing Python logic.

### 4. Commit and Push

Commit your changes with a clear, descriptive message:
```bash
git commit -am "feat: added new speaker to the speakers page"
git push origin feature/your-feature-name
