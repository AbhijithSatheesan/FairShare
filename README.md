# FairShare — Group Expense Sharing API

FairShare is a REST API built with Django and Django REST Framework for managing shared expenses between members of a group. It allows users to create groups, add members, record expenses, filter expenses by category, and calculate who owes money to whom.

## Features

- **User management:** Create and list users.
- **Group management:** Create groups and manage group membership.
- **Expense tracking:** Record expenses against a group and identify the person who paid.
- **Equal expense splitting:** Divide each expense equally among all current members of the group.
- **Balance calculation:** Calculate outstanding balances and generate simplified debtor-to-creditor relationships.
- **Category filtering:** Filter group expenses by category, such as food, travel, accommodation, shopping, utilities, and other.
- **Input validation:** Reject invalid amounts, expenses for groups without members, and payers who do not belong to the selected group.
- **Automated testing:** Unit tests covering expense creation, validation, balance calculations, and category filtering.
- **Docker support:** Build and run the application in a container.

## Tech Stack

- Python
- Django
- Django REST Framework
- SQLite
- Docker and Docker Compose

## Project Structure

```text
fairshare/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
├── fairshare/
│   ├── settings.py
│   └── urls.py
└── expense/
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    ├── tests.py
    └── migrations/
```

## Getting Started

### Prerequisites

For local development:

- Python 3.10 or later, compatible with the installed dependencies
- pip
- Git

For containerized execution:

- Docker Engine
- Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/AbhijithSatheesan/FairShare
cd fairshare
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with your actual repository URL.

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

On Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Start the development server

```bash
python manage.py runserver
```

The API will be available at:

`http://127.0.0.1:8000/`

The API endpoints are mounted under `/api/expense/`.

## Running with Docker

Ensure Docker Engine and Docker Compose are installed and running.

Build the image and start the application:

```bash
docker compose up -d --build
```

The application should be available at:

`http://127.0.0.1:8000/`

Run the automated tests inside the running container:

```bash
docker compose exec web python manage.py test expense
```

Stop the application:

```bash
docker compose down
```

If your Docker installation requires elevated permissions, prefix the Docker commands with `sudo`.

## API Documentation

All endpoints use the `/api/expense/` prefix.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/expense/users/` | List users |
| POST | `/api/expense/users/` | Create a user |
| GET | `/api/expense/groups/` | List groups |
| POST | `/api/expense/groups/` | Create a group |
| POST | `/api/expense/groups/members/` | Add a member to a group |
| GET | `/api/expense/groups/<group_id>/members/` | List group members |
| POST | `/api/expense/expenses/` | Create an expense |
| GET | `/api/expense/groups/<group_id>/expenses/` | List expenses in a group |
| GET | `/api/expense/groups/<group_id>/balances/` | Calculate group balances |

### Example: Create a User

`POST /api/expense/users/`

```json
{
  "name": "Mohit"
}
```

### Example: Create a Group

`POST /api/expense/groups/`

```json
{
  "name": "Goa Trip"
}
```

### Example: Add a Member to a Group

`POST /api/expense/groups/members/`

```json
{
  "group_id": 1,
  "user_id": 1
}
```

Both IDs must refer to existing records.

### Example: Create an Expense

`POST /api/expense/expenses/`

```json
{
  "group_id": 1,
  "paid_by": 1,
  "amount": "1200.00",
  "description": "Dinner",
  "category": "food"
}
```

The group must have members, and the user identified by `paid_by` must belong to that group. The expense amount must be greater than zero.

### Example: Filter Expenses by Category

`GET /api/expense/groups/1/expenses/?category=food`

Returns expenses belonging to group 1 whose category is `food`.

Supported categories:

- `food`
- `travel`
- `accommodation`
- `shopping`
- `utilities`
- `other`

### Example: Calculate Group Balances

`GET /api/expense/groups/1/balances/`

The response represents outstanding amounts between members. For example:

```json
{
  "Rahul": {
    "owes": {
      "Mohit": 400.0
    }
  },
  "Ankit": {
    "owes": {
      "Mohit": 400.0
    }
  }
}
```

This example assumes Mohit paid ₹1,200 for three group members, including himself, and the expense is split equally.

## Database Design

The application uses four main models.

### User

Stores user information and extends Django's `AbstractUser`.

Important fields include the user's name, username, and Django authentication fields.

### Group

Represents a group that shares expenses.

- `id`: Primary key
- `name`: Group name

### GroupMembership

Connects users to groups through foreign keys.

- `group`: Reference to the group
- `member`: Reference to the user

A unique constraint on `(group, member)` prevents the same user from joining the same group more than once.

### Expense

Stores each expense recorded for a group.

- `group`: Reference to the group
- `amount`: Expense amount
- `description`: Expense description
- `category`: Expense category
- `created_at`: Creation timestamp

### ExpensePayment

Records who paid for an expense and how much they paid.

- `expense`: Reference to the expense
- `member`: Reference to a group membership
- `amount_paid`: Amount paid by that member

The current implementation records the full expense amount against one payer. The balance endpoint calculates each member's equal share and compares it with the amount they paid.

### Relationships

- A group can have many memberships.
- A user can belong to multiple groups.
- A group can contain many expenses.
- An expense can have one or more payment records.
- Each payment record references a group membership, ensuring the payer is associated with a group.

## Balance Calculation Logic

For each expense, the application divides the expense amount equally among the group's current members.

Each member's balance is adjusted as follows:

- Subtract their equal share of the expense.
- Add the amount they paid, if any.

A positive balance means the member is owed money. A negative balance means the member owes money.

The API then matches members with negative balances to members with positive balances to produce a simplified list of transfers.

## Validation and Testing

The project includes automated API tests for:

1. Successful expense creation.
2. Rejection of zero-value expenses.
3. Rejection of negative-value expenses.
4. Rejection of a payer outside the group.
5. Rejection of expenses for groups without members.
6. Correct balance calculation for an equal split.
7. Filtering expenses by category.

Run the tests locally:

```bash
python manage.py test expense
```

Run them inside Docker:

```bash
docker compose exec web python manage.py test expense
```

**Verification:** All seven tests passed inside the Docker container during development.

## Assumptions and Design Decisions

- Expenses are split equally among all current members of the group.
- The person who pays an expense must be a member of the selected group.
- An expense cannot be created for a group without members.
- Expense amounts must be greater than zero.
- Expense categories are restricted to the supported choices.
- Group membership is unique per user and group.
- Expense shares are calculated dynamically when balances are requested instead of storing a separate share record for every member.
- SQLite is used as the default database to keep local setup simple.

## Limitations and Future Improvements

Given more development time, the following improvements could be added:

- Support unequal splits and custom per-member shares.
- Add expense editing, deletion, and settlement tracking.
- Preserve historical expense shares when group membership changes.
- Add authentication and permissions to restrict access to user-specific data.
- Improve decimal rounding for expenses that cannot be divided evenly into currency units.
- Add pagination and query optimization for larger groups.
- Add API schema documentation using OpenAPI and Swagger.
- Use PostgreSQL for production deployment.
- Add environment-based configuration and production deployment settings.
- Expand tests for edge cases, permissions, and larger expense histories.

## License

This project was developed as a backend engineering assignment. Add a license here if one is required by the repository or project owner.
