# 🚀 Enterprise Asynchronous Email Microservice

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-blue?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic)](https://docs.pydantic.dev)
[![Architecture](https://img.shields.io/badge/Architecture-3--Tier%20Clean-orange?style=for-the-badge)](#-architecture-overview)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](#)

A high-performance, non-blocking **Transactional Email Notification Microservice** built with **FastAPI**, **Pydantic v2**, and **aiosmtplib**. Designed strictly following the **3-Tier Clean Architecture** principles to ensure loose coupling, high concurrency, and zero thread-blocking during SMTP network handshakes.

---

## 📑 Table of Contents

- [🏛️ Architecture Overview](#️-architecture-overview)
- [📂 Codebase Topology & File Breakdown](#-codebase-topology--file-breakdown)
- [⚡ Key Engineering Highlights](#-key-engineering-highlights)
- [🛠️ Tech Stack](#️-tech-stack)
- [🚀 Quick Start Guide](#-quick-start-guide)
- [📡 API Documentation & Testing](#-api-documentation--testing)
- [🗺️ Evolution Roadmap](#️-evolution-roadmap)

---

## 🏛️ Architecture Overview

The system decouples HTTP request routing from SMTP socket I/O using FastAPI's asynchronous event loop and `BackgroundTasks`. The client receives an immediate `202 ACCEPTED` response (< 15ms), while email delivery executes concurrently in the background.

```mermaid
flowchart LR
    Client["Client / Frontend"] -->|POST /api/v1/emails/send| Router["API Controller (emails.py)"]
    Router -->|Validate DTO| Schema["Pydantic Schema (email.py)"]
    Router -->|Dispatch Task| BG["FastAPI BackgroundTasks"]
    Router -->|Instant 202 Accepted < 15ms| Client
    
    subgraph "Background Non-Blocking Execution"
        BG -->|Invoke Async| Service["EmailService (email_service.py)"]
        Config["Settings (config.py)"] -->|Inject Credentials| Service
        Service -->|SSL Handshake (Port 465)| SMTP["Custom Domain SMTP Server"]
        SMTP -->|Deliver| Inbox["User Gmail Inbox"]
    end
```

---

## 📂 Codebase Topology & File Breakdown

All code evolves inside the unified `app/` directory following strict Separation of Concerns:

```text
e:\Sports\
├── app/
│   ├── api/
│   │   └── emails.py           # Layer 1: HTTP API Controller & Routing
│   ├── core/
│   │   └── config.py           # Configuration & Environment Management
│   ├── schemas/
│   │   └── email.py            # Layer 2: Pydantic Request & Response DTOs
│   ├── services/
│   │   └── email_service.py    # Layer 3: Pure Business Logic & SMTP Engine
│   └── main.py                 # Application Bootstrap & Lifecycle Gateway
├── .env                        # Local Secret Credentials (Git Ignored)
├── .env.example                # Template for Environment Configuration
├── .gitignore                  # Git Exclusion Rules
└── README.md                   # System Architecture & Documentation
```

### বিস্তারিত ফাইলের দায়িত্ব ও কার্যপদ্ধতি:

| ফাইল ও লোকেশন | রেসপনসিবিলিটি (Responsibility) | কী কাজ করে এবং কেন তৈরি হয়েছে? |
| :--- | :--- | :--- |
| **`app/schemas/email.py`** | **Data Transfer Object (DTO)** | ক্লায়েন্ট থেকে আসা রিকোয়েস্ট এবং রেসপন্সের ডেটা ভ্যালিডেশন করে। `EmailStr` ব্যবহার করায় ভুল ইমেইল ফরম্যাট হলে স্বয়ংক্রিয়ভাবে `422 Unprocessable Entity` রিটার্ন করে। |
| **`app/services/email_service.py`** | **Pure Business Logic** | ইমেইল কম্পোজিশন ও ডেলিভারির মূল কাজ করে। এতে স্ট্যান্ডার্ড ব্লকিং `smtplib`-এর পরিবর্তে নন-ব্লকিং **`aiosmtplib`** ব্যবহার করা হয়েছে। পোর্ট অনুযায়ী স্বয়ংক্রিয়ভাবে **SSL (465)** এবং **STARTTLS (587)** হ্যান্ডশেক ম্যানেজ করে। |
| **`app/api/emails.py`** | **Controller / Router** | HTTP রিকোয়েস্ট রিসিভ করে, `BackgroundTasks`-এ ইমেইল পাঠানোর কাজ পুশ করে এবং ইউজারকে সাথে সাথে `202 ACCEPTED` রেসপন্স পাঠায়। কোনো বিজনেস লজিক এতে নেই। |
| **`app/core/config.py`** | **Configuration Manager** | `pydantic-settings`-এর `BaseSettings` ব্যবহার করে নিরাপদভাবে `.env` ফাইল থেকে SMTP হোস্ট, পোর্ট, ইউজারনেম ও পাসওয়ার্ড রিড করে। কোনো ক্রেডেনশিয়াল কোডে হার্ডকোড থাকে না। |
| **`app/main.py`** | **Entrypoint & Router Hub** | FastAPI অ্যাপ ইনিশিয়ালাইজ করে, রাউটারগুলো মাউন্ট করে, হেলথ চেক এন্ডপয়েন্ট এক্সপোজ করে এবং প্রজেক্ট রুট পাথ অটো-বুস্ট্র্যাপ করে যাতে সরাসরি IDE Run বাটন থেকেও Uvicorn চালু করা যায়। |
| **`.env`** | **Secret Credentials** | SMTP সার্ভারের সংবেদনশীল তথ্য রাখে। গিটহাবে পাসওয়ার্ড লিক হওয়া রোধে এটিকে `.gitignore`-এ যুক্ত রাখা হয়েছে। |

---

## ⚡ Key Engineering Highlights

1. **Non-Blocking Asynchronous I/O:**  
   প্রচলিত `time.sleep()` বা সিঙ্ক্রোনাস সকেট কল পুরো সার্ভারের থ্রেড ফ্রিজ করে দেয়। `aiosmtplib` ব্যবহারের ফলে ১০০টি ইমেইল কনকারেন্টলি পাঠানো হলেও সার্ভার রেসপন্সিভ থাকে।
2. **Resilient Port & Protocol Auto-Detection:**  
   বাংলাদেশের ও বিশ্বব্যাপী অধিকাংশ আইএসপি (ISP) স্প্যামিং রোধে আউটবাউন্ড **Port 25** ব্লক করে রাখে। এই সার্ভিসটি স্বয়ংক্রিয়ভাবে **Port 465 (Direct SSL)** এবং **Port 587 (STARTTLS)** ডাইনামিক্যালি সনাক্ত করে সফল ডেলিভারি নিশ্চিত করে।
3. **Fail-Fast Input Sanitation:**  
   Pydantic v2 দিয়ে রিকোয়েস্ট লেভেলেই কড়া ভ্যালিডেশন (মিনিমাম/ম্যাক্সিমাম লেন্থ, সঠিক ইমেইল ডোমেইন) চেক হয়, ফলে ডাটাবেজ বা নেটওয়ার্ক লেয়ারে কোনো নোংরা ডেটা পৌঁছায় না।

---

## 🛠️ Tech Stack

- **Framework:** FastAPI
- **Data Validation:** Pydantic v2 (`pydantic[email]`)
- **Settings Management:** Pydantic Settings
- **Async SMTP Client:** `aiosmtplib`
- **ASGI Server:** Uvicorn (WatchFiles reloader)

---

## 🚀 Quick Start Guide

### ১. রিপোজিটরি ক্লোন ও ডিপেনডেন্সি ইনস্টল:
```bash
# গিট ক্লোন করুন
git clone <your-github-repo-url>
cd <repo-folder>

# প্রয়োজনীয় প্যাকেজ ইনস্টল করুন
pip install fastapi uvicorn "pydantic[email]" pydantic-settings aiosmtplib
```

### ২. পরিবেশ কনফিগারেশন (`.env`):
`.env.example` ফাইলটি কপি করে `.env` তৈরি করুন এবং আপনার SMTP ক্রেডেনশিয়াল দিন:
```env
SMTP_HOST=mail.yourdomain.com
SMTP_PORT=465
SMTP_USER=info@yourdomain.com
SMTP_PASSWORD=your_secure_smtp_password
EMAIL_FROM=info@yourdomain.com
```

### ৩. সার্ভার চালু করুন:
```bash
# অপশন ১: টার্মিনাল কমান্ড
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# অপশন ২: সরাসরি main.py রান করে
python app/main.py
```
সার্ভার সফলভাবে চালু হলে ভিজিট করুন:  
👉 **ইনটারেক্টিভ Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
👉 **সিস্টেম হেলথ চেক:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 📡 API Documentation & Testing

### Endpoint: `POST /api/v1/emails/send`
গ্রাহকের কাছে ব্যাকগ্রাউন্ডে নন-ব্লকিং ইমেইল পাঠানোর এন্ডপয়েন্ট।

#### Request Payload:
```json
{
  "recipient_email": "tonmoytarchera@gmail.com",
  "subject": "It's your first email test",
  "user_name": "Tarchera",
  "message": "স্বাগতম! আমাদের প্ল্যাটফর্মে আপনার অ্যাকাউন্ট সক্রিয় হয়েছে।"
}
```

#### Successful Response (`202 Accepted`):
```json
{
  "status": "queued",
  "message": "tonmoytarchera@gmail.com ঠিকানায় ইমেইল পাঠানোর কাজ কিউতে নেওয়া হয়েছে।"
}
```

#### cURL Command:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/emails/send" \
     -H "Content-Type: application/json" \
     -d '{
       "recipient_email": "tonmoytarchera@gmail.com",
       "subject": "Welcome to Platform",
       "user_name": "Tonmoy",
       "message": "Your registration is confirmed."
     }'
```

---

## 🗺️ Evolution Roadmap

এই রিপোজিটরিটি একটি **Single Evolving Codebase** হিসেবে দিন দিন পূর্ণাঙ্গ এন্টারপ্রাইজ প্ল্যাটফর্মে রূপান্তর হবে:

- [x] **Milestone 1 (Day 1):** Asynchronous Transactional Email Microservice (aiosmtplib, BackgroundTasks, DTOs).
- [ ] **Milestone 2 (Day 2):** User Model, PostgreSQL Database Integration & Registration API (Auto Welcome Email trigger).
- [ ] **Milestone 3 (Day 3):** JWT Authentication (Access + Refresh Token), Password Hashing (bcrypt).
- [ ] **Milestone 4 (Day 4):** Responsive HTML Email Templates with Jinja2.
- [ ] **Milestone 5 (Day 5):** Distributed Queue Migration with Celery/Redis & Dead Letter Queue (DLQ).

---
*Maintained under Enterprise Architectural Governance Standards.*

