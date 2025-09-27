# 🐍 PyLadies Kuala Lumpur Website 🇲🇾

Welcome to the official GitHub repository for the PyLadies Kuala Lumpur website! This site is the central hub for our community, showcasing events, committee members, and mission.

This project is built using **Django** and styled with **Tailwind CSS**. We welcome contributions from everyone in the Python community, especially women and non-binary individuals.

---

## 🚀 Quick Start (Local Development)

Follow these steps to get a local copy of the project running for development.

### Prerequisites

You must have Python (3.9+) and pip installed.

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
    The project uses AWS S3 for static files and content. For local development, you need a placeholder `.env` file.

    **Create a file named `.env` in the root directory:**
    ```env
    # Essential Django Settings
    SECRET_KEY='django-insecure-your-secret-key-for-local'
    DEBUG=True
    
    # Optional: Mock S3 Credentials for Boto3 (Only needed if local file listing fails)
    # AWS_ACCESS_KEY_ID='AKIA...'
    # AWS_SECRET_ACCESS_KEY='...'
    
    # Set AWS_LOCATION to match your settings.py if using S3 locally
    AWS_LOCATION='theme/static' 
    
    # Use the local filesystem for static files by default (DEBUG=True)
    # If using custom S3 logic, ensure you have read access.
    ```

5.  **Run Migrations (if needed) & Server:**
    ```bash
    python manage.py makemigrations 
    python manage.py migrate
    python manage.py runserver
    ```
    The site should now be running at `http://127.0.0.1:8000/`.

---

## 📁 Project Structure

Key files and directories for collaborators to understand:

| Path | Description |
| :--- | :--- |
| `pyladies_kl/settings.py` | theme Django configuration, including S3 settings. |
| `theme/views.py` | Contains all page logic (`home`, `about`, `events`, etc.). This is where **S3 content fetching and filtering** occurs. |
| `theme/templates/` | Django templates (`home.html`, `about.html`, etc.). Uses Jinja-style syntax and Tailwind classes. |
| `theme/static/images/` | **The S3 content directories.** Static assets like committee photos, speaker photos, and JSON data files are stored here (e.g., `images/committee/`, `images/events/`). |
| `theme/static/css/` | Tailwind CSS output and custom styles. |

---

## 🤝 How to Contribute

We follow a standard GitHub flow.

### 1. Identify Content Tasks

Most contributions will involve updating static content.

| Task | Location | Details |
| :--- | :--- | :--- |
| **Update Committee** | S3: `images/committee/` | Upload image files named `firstname-lastname_role.jpg` |
| **Add Events** | S3: `images/events/events_data.json` | Edit the JSON file with new event entries. |
| **Add Blog Posts** | S3: `images/blog/blog_posts.json` | Edit the JSON file with new post entries. |
| **Code Fixes** | `theme/views.py` & `theme/templates/` | Fix bugs, enhance UI, or improve S3 interaction logic. |

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
