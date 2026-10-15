# FairShare — Group Expense Sharing API

FairShare is a REST API built with Django REST Framework to manage shared expenses. Users can create groups, add members, record expenses, and check who owes money to whom.

## Features

- Create and list users and groups
- Add members to groups
- Record expenses and identify the payer
- Split expenses equally among group members
- Calculate balances between members
- Filter expenses by category
- Validate expense amounts and group membership
- Automated tests and Docker support

## Tech Stack

- Python
- Django and Django REST Framework
- SQLite
- Docker and Docker Compose

## Setup

### Run locally

**Requirements:** Python, pip, and Git.

```bash
git clone https://github.com/AbhijithSatheesan/FairShare.git
cd FairShare

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The API runs at `http://127.0.0.1:8000/`.

### Run with Docker

```bash
docker compose up -d --build
```

Run the tests:

```bash
docker compose exec web python manage.py test expense
```

Stop the application:

```bash
docker compose down
```

Use `sudo` before Docker commands if your system requires it.

## API Endpoints

All endpoints use the `/api/expense/` prefix.

| Method | Endpoint | Description |
|---|---|---|
| GET, POST | `/users/` | List or create users |
| GET, POST | `/groups/` | List or create groups |
| POST | `/groups/members/` | Add a member to a group |
| GET | `/groups/<group_id>/members/` | List group members |
| POST | `/expenses/` | Create an expense |
| GET | `/groups/<group_id>/expenses/` | List group expenses |
| GET | `/groups/<group_id>/balances/` | Calculate group balances |

### Example: Create an expense

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

The group must have members, and the payer must belong to that group. The amount must be greater than zero.

Supported categories: `food`, `travel`, `accommodation`, `shopping`, `utilities`, `other`.

Filter expenses using:

`GET /api/expense/groups/1/expenses/?category=food`

## Database Design

The application uses four main models:

- **User:** Extends Django's `AbstractUser`.
- **Group:** Stores group information.
- **GroupMembership:** Connects users to groups and prevents duplicate memberships.
- **Expense:** Stores the group, amount, description, category, and creation time.
- **ExpensePayment:** Records the amount paid by a group member for an expense.

## Balance Calculation

Expenses are split equally among the group's current members. Each member's share is deducted from their balance, and the amount paid is credited to the payer. The API matches members who owe money with members who are owed money.

## Testing

The test suite covers expense creation, invalid amounts, invalid payers, empty groups, balance calculation, and category filtering.

Run the tests locally:

```bash
python manage.py test expense
```

All seven tests passed inside Docker during development.

## Assumptions and Limitations

- Expenses are split equally among current group members.
- Each expense is recorded against one payer.
- Historical shares are not stored separately, so membership changes can affect balance calculations for earlier expenses.
- SQLite is used for simple local development.

Possible future improvements include unequal splits, expense settlements, and PostgreSQL support.