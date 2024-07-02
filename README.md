# Loan Schedule API

## Опис

Цей API дозволяє створювати та змінювати графік платежів за кредитом.

## Технології

- Docker
- Django
- Django REST Framework
- SQLite
- Redis (для кешування)

## Інструкція по розгортанню

1. Клонувати репозиторій:
    ```bash
    git clone <repository-url>
    cd loan_project
    ```

2. Запустити Docker:
    ```bash
    docker-compose up --build
    ```

3. Міграції бази даних:
    ```bash
    docker-compose run web python manage.py migrate
    ```

4. Створити суперкористувача для доступу до адмін-панелі:
    ```bash
    docker-compose run web python manage.py createsuperuser
    ```

5. API буде доступний за адресою:
    ```
    http://localhost:8000/loans/
    ```

## Використання API

    ### Створення графіка платежів

    POST /loans/create-loan/

    Поля:
    ```json
    {
        "amount": 1000,
        "loan_start_date": "10-01-2024",
        "number_of_payments": 4,
        "periodicity": "1m",
        "interest_rate": 0.1
    }

    ### Зміна платежу

    POST /loans/update-payment/<id>/

    Поля:
    ```json
    {
        "reduction_amount": 50
    }

6. Запуск тестів:

    ```bash
    docker-compose run web python manage.py test
    ```