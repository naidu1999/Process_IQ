# Architecture

Presentation layer: HTML, CSS and JavaScript. API layer: FastAPI. Business layer: explainable scoring. Data layer: runtime CSV. The layers are separated so future databases and AI models can replace internal components without frontend redesign.
                         USER
                           │
                           ▼
                ┌──────────────────┐
                │   Web Browser    │
                └──────────────────┘
                           │
                           ▼
        ┌─────────────────────────────────┐
        │         FRONTEND                │
        │                                 │
        │  index.html                     │
        │  style.css                      │
        │  app.js                         │
        └─────────────────────────────────┘
                           │
                    HTTP/API Requests
                           │
                           ▼
        ┌─────────────────────────────────┐
        │          BACKEND                │
        │                                 │
        │          main.py                │
        │          FastAPI                │
        │                                 │
        │  Search                         │
        │  Filters                        │
        │  Process Details                │
        │  Add New Process                │
        │  Opportunity Scoring            │
        │  Recommendations                │
        └─────────────────────────────────┘
                           │
                           ▼
        ┌─────────────────────────────────┐
        │         DATA LAYER              │
        │                                 │
        │        processes.csv            │
        └─────────────────────────────────┘
                           │
                           ▼
        ┌─────────────────────────────────┐
        │      DEPLOYMENT LAYER           │
        │                                 │
        │ Dockerfile                      │
        │ docker-compose.yml              │
        │ Render                          │
        └─────────────────────────────────┘
