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

Build and start the application:

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

## API Documentation

All endpoints use the `/api/expense/` prefix.

Requests with a body should use `Content-Type: application/json`.

### 1. Users

**List users**

`GET /api/expense/users/`

Returns the list of users.

**Create a user**

`POST /api/expense/users/`

Request body:

```json
{
  "name": "Mohit"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | String | Yes | Name of the user (maximum 50 characters) |

The API generates a unique username automatically.

Example response:

```json
{
  "id": 1,
  "name": "Mohit"
}
```

### 2. Groups

**List groups**

`GET /api/expense/groups/`

**Create a group**

`POST /api/expense/groups/`

Request body:

```json
{
  "name": "Weekend Trip"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | String | Yes | Name of the group (maximum 50 characters) |

Example response:

```json
{
  "id": 1,
  "name": "Weekend Trip"
}
```

### 3. Add a Member to a Group

`POST /api/expense/groups/members/`

Request body:

```json
{
  "group_id": 1,
  "user_id": 1
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `group_id` | Integer | Yes | ID of the group |
| `user_id` | Integer | Yes | ID of the user to add |

The user and group must already exist. Duplicate memberships are not allowed.

### 4. List Group Members

`GET /api/expense/groups/<group_id>/members/`

Example:

`GET /api/expense/groups/1/members/`

Returns the users belonging to the specified group.

Example response:

```json
[
  {
    "id": 1,
    "name": "Mohit"
  }
]
```

### 5. Create an Expense

`POST /api/expense/expenses/`

Request body:

```json
{
  "group_id": 1,
  "paid_by": 1,
  "amount": "1200.00",
  "description": "Dinner",
  "category": "food"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `group_id` | Integer | Yes | ID of the group |
| `paid_by` | Integer | Yes | ID of the user who paid |
| `amount` | Decimal string | Yes | Amount greater than zero, with up to two decimal places |
| `description` | String | Yes | Description of the expense |
| `category` | String | No | Expense category; defaults to `other` |

Supported categories: `food`, `travel`, `accommodation`, `shopping`, `utilities`, `other`.

The group must have at least one member, and the payer must belong to that group. The expense is recorded with the payer's full payment amount.

Example response:

```json
{
  "id": 1,
  "group_id": 1,
  "paid_by_name": "Mohit",
  "amount": "1200.00",
  "description": "Dinner",
  "category": "food"
}
```

### 6. List Group Expenses

`GET /api/expense/groups/<group_id>/expenses/`

Example:

`GET /api/expense/groups/1/expenses/`

To filter expenses by category, use the `category` query parameter:

`GET /api/expense/groups/1/expenses/?category=food`

Returns the expenses associated with the specified group, optionally filtered by category.

### 7. Calculate Group Balances

`GET /api/expense/groups/<group_id>/balances/`

Example:

`GET /api/expense/groups/1/balances/`

Returns the calculated amounts owed between group members.

Example response:

```json
{
  "Alice": {
    "owes": {
      "Mohit": 400.0
    }
  }
}
```

This example means Alice owes Mohit 400. The actual response depends on the group's members and recorded expenses. An empty group returns an empty JSON object.

### Validation

The API validates expense amounts, group membership, and category choices. Invalid requests return validation errors. Examples include:

- An amount of zero or a negative amount.
- A payer who does not belong to the specified group.
- An expense created for a group with no members.
- A duplicate group membership.

## Database Design

The application uses five models:

- **User:** Extends Django's `AbstractUser` and adds a `name` field.
- **Group:** Stores the group name.
- **GroupMembership:** Connects users to groups and prevents duplicate memberships using a unique constraint.
- **Expense:** Stores the group, amount, description, category, and creation time.
- **ExpensePayment:** Records the amount paid by a group member for an expense.

## Balance Calculation

Expenses are split equally among the group's current members. Each member's share is deducted from their balance, and the full amount paid is credited to the payer. The API matches members who owe money with members who are owed money.

Balances are calculated when requested rather than stored separately for each member.

## Testing

The test suite covers expense creation, invalid amounts, invalid payers, empty groups, balance calculation, and category filtering.

Run the tests locally:

```bash
python manage.py test expense
```

All seven tests passed inside Docker during development.

## Assumptions and Limitations

- Expenses are split equally among current group members.
- Each expense has one payer.
- Historical shares are not stored separately, so membership changes can affect balance calculations for earlier expenses.
- SQLite is used for local development.
- Unequal expense splits and settlement tracking are not implemented.

## Architecture and Design Decisions

Django REST Framework exposes the API endpoints, serializers validate incoming data, and Django models manage database operations.

A separate `ExpensePayment` model records payments independently from the expense itself. This provides a foundation for extending the application with additional payment and settlement functionality.

## Improvements with More Time

- Support unequal expense splits and settlement tracking.
- Track individual contributions and settlements to make it easier to determine how much each user has paid and what remains to be settled.
- Support PostgreSQL for production deployment.
- Add more comprehensive API tests and automated API documentation.
