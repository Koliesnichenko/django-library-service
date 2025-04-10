# LibraryService API

## **Description of the Project:**

LibraryService is a Django-based web API to manage a library system, offering features like book borrowing, payments, notifications, and user management. The API provides efficient book tracking, borrowing status, and integrates with Stripe for payments and Telegram for notifications.

## **Technologies Used**
    ● **Backend**: Python 3.11+, Django 5.x, Django REST Framework 3.15+
    ● **Database**: PostgreSQL
    ● **Testing**: Django Test Framework
    ● **Other**: Pillow, psycopg2, stripe, pyjwt, Docker

## **Installation**

    **Prerequisites**:
    ● Python 3.11+

    ● Docker (for running the app with PostgreSQL)

    ● Stripe API key (for payment integration)

    ● Telegram API key (for notifications)

## **Setup**:
1. Clone the repository:
    ```bash
    git clone https://github.com/Koliesnichenko/django-library-service.git

2. Navigate to the project directory:
      ```
   cd django-library-service
      ```
3.  Create a virtual environment:
     ```
    python -m venv venv
    ```
4. Activate the virtual environment:

    ● On Windows:
    ```
    venv\Scripts\activate
    ```
    ● On macOS or Linux:
   ```
    source venv/bin/activate
    ```
5. Install the required dependencies:
    ```
    pip install -r requirements.txt
    ```
6. Create a .env file in the root directory and add the following:
   ```ini
   DJANGO_SECRET_KEY=your-secret-key
   DEBUG=True
   POSTGRES_DB=library_service
   POSTGRES_USER=library_user
   POSTGRES_PASSWORD=libraryservice
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   STRIPE_SECRET_KEY=your-stripe-secret-key
   TELEGRAM_BOT_TOKEN=your-telegram-bot-token
   TELEGRAM_CHAT_ID=your-telegram-chat-id
      ```

7. Configure your database settings in settings.py:
   ```
   DATABASES = {
       "default": {
           "ENGINE": "django.db.backends.postgresql",
           "NAME": os.getenv("POSTGRES_DB"),
           "USER": os.getenv("POSTGRES_USER"),
           "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
           "HOST": os.getenv("POSTGRES_HOST", "db"),
           "PORT": os.getenv("POSTGRES_PORT", 5432),
       }
   }
    ```
8. Start project:
   ```
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

**For Docker**:
   Build and start the Docker containers:
   
   ```
   docker-compose up --build -d
   ```
   Apply migrations inside Docker:
   ```
   docker-compose exec <name-your-app-in-docker> python manage.py migrate
   ```
   Create a superuser inside Docker:
   ```
   docker-compose exec <name-your-app-in-docker> python manage.py createsuperuser
   ```

**For getting access**:
   ● Email: admin@mail.com
   ● Password: 12345

## **API Endpoints**:
   **Authentication**:
      ● POST /api/users/: Create a new user with email, first name, last name, and password.
      
      ● POST /api/users/token/: Log in and obtain a JWT token.
   
      ● GET /api/users/me/: Retrieve the authenticated user's profile.
   
   **Book Management**:
      ● GET /api/books/: List all books.
      
      ● POST /api/books/: Create a new book (admin only).
      
      ● GET /api/books/{id}/: Retrieve details of a specific book.
      
      ● PUT/PATCH /api/books/{id}/: Update a book (admin only).
      
      ● DELETE /api/books/{id}/: Delete a book (admin only).
      
   **Borrowing Management**:
      ● POST /api/borrowings/: Create a new borrowing record (decreases book inventory by 1).
      
      ● GET /api/borrowings/: List all borrowings (filtered by user or active status).
      
      ● GET /api/borrowings/{id}/: Retrieve details of a specific borrowing.
      
      ● POST /api/borrowings/{id}/return/: Mark a borrowing as returned (increases book inventory by 1).
   
   **Payment Management**:
      ● GET /api/payments/: List my payments (List all payments for admin).
      
      ● POST /api/payments/: Create a payment.
      
      ● GET /api/payments/success/: Handle successful payment callback from Stripe.
      
      ● GET /api/payments/cancel/: Handle canceled payment callback from Stripe.
   
