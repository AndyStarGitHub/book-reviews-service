# Book Reviews Service

A service for managing books and reviews with **search** and **analytics** powered by Elasticsearch.

## ⚙️ Stack

* **FastAPI** (Python 3.12)
* **Elasticsearch 8.15.0**
* **Kibana 8.15.0**
* **Docker Compose**

---

## 🚀 Features

* Add books: `POST /books/`
* List books with pagination: `GET /books/`
* Get book by ID: `GET /books/{book_id}`
* Add review to book: `POST /books/{book_id}/reviews/`
* List reviews for a book: `GET /books/{book_id}/reviews/`
* List reviews for a book and average rating: `GET /books/plus-reviews/{book_id}/`
* Full-text search with filters: `GET /search/?q=...&genre=...&min_rating=...&year=...`
* Analytics — top 5 books by average rating: `GET /analytics/top-rated`

Swagger UI: **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## 📁 Project Structure

```
book-reviews-service/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example → .env
└── app/
    ├── __init__.py
    ├── main.py
    ├── es_client.py
    ├── index_migrations.py
    ├── schemas.py
    └── routers/
        ├── __init__.py
        ├── books.py
        ├── reviews.py
        ├── search.py
        └── analytics.py
```

---

## 🔧 Setup

1. Copy `.env.example` → `.env` (or create manually):

```
ELASTIC_HOST=http://elasticsearch:9200
BOOKS_INDEX=books
REVIEWS_INDEX=reviews
```

2. Ensure *requirements.txt* includes:

```
fastapi==0.116.1
uvicorn[standard]==0.35.0
elasticsearch==8.15.0
pydantic==2.11.7
python-dotenv==1.1.1
loguru==0.7.3
```

---

## Installation & Run

### Clone the repository and install dependencies:

```bash
git clone https://github.com/AndyStarGitHub/book-reviews-service.git
cd book-reviews-service
python -m venv .venv
.venv\Scripts\activate  # for Windows
pip install -r requirements.txt
````

## ▶️ Run

```bash
docker compose up --build
```

* API: [http://localhost:8000](http://localhost:8000)
* Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
* Kibana: [http://localhost:5601](http://localhost:5601)

---

## 🧱 Elasticsearch Indices

Indices are created automatically at app startup (`ensure_indices()` in `index_migrations.py`).

### books

* `id: keyword`
* `title: text` + `title.raw: keyword`
* `author: text` + `author.raw: keyword`
* `year: integer`
* `genres: keyword[]`
* `created_at: date`

### reviews

* `id: keyword`
* `book_id: keyword`
* `rating: integer (1..5)`
* `text: text`
* `created_at: date`

---

## 🔌 Endpoints

### Books

**POST /books/** — add a book

```json
{
  "title": "Dune",
  "author": "Frank Herbert",
  "year": 1965,
  "genres": ["sci-fi"]
}
```

**GET /books/** — list books (params: `page`, `size`)

**GET /books/{book_id}** — get book by ID (+ extended version includes `avg_rating` & `reviews`)

### Reviews

**POST /books/{book_id}/reviews/** — add a review to the book

```json
{ "rating": 5, "text": "Masterpiece" }
```

**GET /books/{book_id}/reviews/** — list reviews for the book (params: `page`, `size`)

**GET /books/plus-reviews/{book_id}/** — list reviews plus average rating for the book
(params: `page`, `size`)

### Search

**GET /search/** — examples:

* `?q=dune`
* `?genre=sci-fi&year=1965`
* `?q=tolkien&genre=fantasy&min_rating=4`

### Analytics

**GET /analytics/top-rated** — top 5 books by average rating.

* Returns `book_id` and `avg_rating`.

---

## 🧪 Example Requests (curl)

```bash
# add a book
curl -X POST http://localhost:8000/books/ \
  -H 'Content-Type: application/json' \
  -d '{"title":"Dune","author":"Frank Herbert","year":1965,"genres":["sci-fi"]}'

# add a review (replace BOOK_ID)
curl -X POST http://localhost:8000/books/BOOK_ID/reviews/ \
  -H 'Content-Type: application/json' \
  -d '{"rating":5,"text":"Masterpiece"}'

# get a book with reviews
curl http://localhost:8000/books/BOOK_ID

# search
curl "http://localhost:8000/search/?q=dune&genre=sci-fi&min_rating=4&year=1965"

# analytics
curl http://localhost:8000/analytics/top-rated
```

---

## 📊 Kibana Quick Start

1. Open Kibana → **Stack Management → Data Views** → create `books*` and `reviews*`.
2. Go to **Discover** to browse indexed documents.
3. Use **Lens** to visualize: e.g., distribution of ratings or top books by number of reviews.

---
