
  ![image](https://github.com/user-attachments/assets/84acdca9-9338-4091-a0b3-79657c3c8e07)





**Presentation about our Project ( file a bit large so i decided to upload video at YouTube )**

https://www.youtube.com/watch?v=gS2lu6bgro8

---

# 🎯 **Sales Monitoring & Analytics Platform**  
📊 *A Django-based platform for tracking and analyzing additional product sales at checkout.*  

![Django](https://img.shields.io/badge/Made%20with-Django-green?style=for-the-badge&logo=django)  
![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)  
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)  

---

## 📖 **Table of Contents**  
- [📌 Description](#-description)  
- [🚀 Getting Started](#-getting-started)  
  - [🔧 Dependencies](#-dependencies)  
  - [📥 Installing](#-installing)  
  - [▶️ Executing Program](#-executing-program)  
- [❓ Help](#-help)  
- [👥 Authors](#-authors)  
- [📜 Version History](#-version-history)  

---

## 📌 **Description**  
This project is a **Django-based** platform that allows businesses to **monitor and analyze sales** of additional products at checkout.  

### ✅ **Features:**  
✔️ **Set sales targets** for a specific period  
✔️ **Manage employees and products**  
✔️ **Track real-time sales records**  
✔️ **Generate leaderboards** to identify top-performing employees  
✔️ **View daily sales analytics** with reports  
✔️ **Secure admin panel & user role management**  
✔️ **REST API support** for external integrations  

---

## 🚀 **Getting Started**  

### 🔧 **Dependencies**  
Before running the program, ensure you have the following installed:  
✅ Python 3.x  
✅ Django  
✅ `pip` (Python package manager)  
✅ SQLite (or another database engine)  

### 📥 **Installing**  
```bash
# Clone the repository
git clone https://github.com/Vladis666/sigma_django.git
cd sigma_django
cd taskm

# Set up a virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Start the server
python manage.py runserver
```
🌍 Open **`http://127.0.0.1:8000/`** in your browser  

---

## ▶️ **Executing Program**  

1️⃣ **Launch the server:**  
   ```bash
   python manage.py runserver
   ```

2️⃣ **Access the admin panel:**  
   📌 Go to **`http://127.0.0.1:8000/admin/`** and log in with superuser credentials.  

3️⃣ **Use the API (optional):**  
   ```
   GET /api/sales/
   POST /api/sales/
   ```

---

## ❓ **Help**  

💡 **Common Issues & Fixes:**  
> **Virtual environment activation issues:**  
```bash
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows
```  
> **Database migration issues:**  
```bash
python manage.py migrate --run-syncdb
```

🔗 **Resources:**  
- 📖 [Django Docs](https://docs.djangoproject.com/)  
- 🎥 [Django Tutorials](https://www.djangoproject.com/start/)  

---

## 👥 **Authors**  
- **Vlad** – *Lead Developer* – [GitHub](https://github.com/Vladis666) 
- **Yaroslav** – *Project Manager* – [GitHub](https://github.com/Gorob4ikLoL)
- **Iryna** – *Frontend Developer* – [GitHub](https://github.com/Androshchuk-Iryna)
- **Anna** – *Frontend Developer* – [GitHub](https://github.com/anwalv) 
- **Sviatoslav** – *Backend Developer* – [GitHub](https://github.com/Koroway)
- **Vadym** – *DataBase* – [GitHub](https://github.com/VadymBabyn)
- **Max** – *Backend Developer* – [GitHub](https://github.com/m-ruzhynskyi)    

---


