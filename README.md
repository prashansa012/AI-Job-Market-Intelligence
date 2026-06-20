# AI-Powered Job Market Intelligence & Recommendation System

## Overview

The AI-Powered Job Market Intelligence & Recommendation System is a Python-based analytics platform that collects job postings from multiple sources, stores them in MySQL, extracts skills from job descriptions, analyzes hiring trends, and generates personalized job recommendations.

This project helps job seekers understand current market demand, identify skill gaps, explore salary trends, and discover relevant job opportunities through automated data collection and analysis.

---

## Features

### Multi-Source Job Collection

* Collects job postings from multiple APIs.
* Standardizes job information into a unified format.
* Stores collected data in a MySQL database.

### Skill Extraction

* Extracts technical skills from job descriptions.
* Categorizes skills into relevant technology domains.
* Maintains structured skill data for analytics.

### Job Market Analytics

Generates insights such as:

* Top in-demand skills
* Highest-paying skills
* City-wise hiring trends
* Remote vs onsite opportunities
* Experience-level demand
* Monthly hiring trends

### Recommendation Engine

* Matches candidate skills with available job opportunities.
* Identifies missing skills required by the market.
* Suggests high-demand skills for career growth.
* Generates personalized recommendation reports.

### Automated Reporting

Exports analytical results into:

* JSON dashboard reports
* CSV trend reports
* Recommendation reports

---

## Tech Stack

* Python
* MySQL
* SQL
* REST APIs
* JSON
* CSV
* Git
* GitHub

---

## Project Structure

```text
AI-Job-Market-Intelligence/
│
├── analytics/
│   ├── recommendation_engine.py
│   ├── skill_extractor.py
│   └── trend_analyzer.py
│
├── collectors/
│   ├── adzuna_collector.py
│   ├── muse_collector.py
│   └── remoteok_collector.py
│
├── config/
│   └── settings.py
│
├── database/
│   └── db_manager.py
│
├── exporters/
│   └── exporter.py
│
├── reports/
│   ├── dashboard.json
│   ├── top_skills.csv
│   ├── hiring_trends.csv
│   └── salary_intelligence.csv
│
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Workflow

1. Collect job postings from external APIs.
2. Store job data in MySQL.
3. Extract technical skills from job descriptions.
4. Analyze hiring patterns and salary trends.
5. Generate personalized recommendations.
6. Export insights as JSON and CSV reports.

---

## Installation

### Clone Repository

```bash
git clone https://github.com/prashansa012/AI-Job-Market-Intelligence.git
cd AI-Job-Market-Intelligence
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Settings

Update database credentials and API keys in:

```text
config/settings.py
```

### Run Project

```bash
python main.py
```

---

## Example Insights Generated

* Most in-demand skills in the current job market.
* Salary intelligence by skill category.
* Hiring demand by city and experience level.
* Remote versus onsite opportunity trends.
* Personalized job recommendations based on user skills.

---

## Skills Demonstrated

* Python Programming
* SQL & Database Management
* API Integration
* Data Collection
* Data Analysis
* Data Modeling
* Recommendation Systems
* Report Generation
* Business Intelligence Concepts

---

## Future Enhancements

* Interactive dashboard visualization.
* Real-time job market monitoring.
* Machine learning-based recommendation models.
* Web-based user interface.

---

## Author

**Prashansa Goswami**

Aspiring Data Analyst | Python | SQL | Power BI | Tableau
