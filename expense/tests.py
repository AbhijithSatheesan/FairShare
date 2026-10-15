
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Group, GroupMembership, Expense, ExpensePayment

User = get_user_model()


class ExpenseAPITests(TestCase):
    def setUp(self):
        # Create three users.
        self.mohit = User.objects.create_user(
            username="mohit",
            password="testpass123",
            name="Mohit",
        )
        self.rahul = User.objects.create_user(
            username="rahul",
            password="testpass123",
            name="Rahul",
        )
        self.ankit = User.objects.create_user(
            username="ankit",
            password="testpass123",
            name="Ankit",
        )

        # Create a group and add all three users.
        self.group = Group.objects.create(name="Goa Trip")

        self.mohit_membership = GroupMembership.objects.create(
            group=self.group,
            member=self.mohit,
        )
        GroupMembership.objects.create(
            group=self.group,
            member=self.rahul,
        )
        GroupMembership.objects.create(
            group=self.group,
            member=self.ankit,
        )

        self.client = APIClient()

        self.expense_url = "/api/expense/expenses/"
        self.balance_url = (
            f"/api/expense/groups/{self.group.id}/balances/"
        )
        self.group_expenses_url = (
            f"/api/expense/groups/{self.group.id}/expenses/"
        )

    def create_expense(self, amount="1200.00"):
        return self.client.post(
            self.expense_url,
            {
                "group_id": self.group.id,
                "paid_by": self.mohit.id,
                "amount": amount,
                "description": "Dinner",
                "category": "food",
            },
            format="json",
        )

    # Test 1: A valid expense can be created.

    def test_expense_creation(self):
        response = self.create_expense()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Expense.objects.count(), 1)
        self.assertEqual(ExpensePayment.objects.count(), 1)

        expense = Expense.objects.get()

        self.assertEqual(expense.amount, Decimal("1200.00"))
        self.assertEqual(expense.description, "Dinner")
        self.assertEqual(expense.category, "food")

        payment = ExpensePayment.objects.get()

        self.assertEqual(payment.expense, expense)
        self.assertEqual(payment.member, self.mohit_membership)
        self.assertEqual(payment.amount_paid, Decimal("1200.00"))

        self.assertEqual(response.data["paid_by_name"], "Mohit")

    # Test 2: Zero and negative amounts are rejected.

    def test_zero_amount_is_rejected(self):
        response = self.create_expense("0.00")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Expense.objects.count(), 0)

    def test_negative_amount_is_rejected(self):
        response = self.create_expense("-100.00")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Expense.objects.count(), 0)

    # Test 3: The payer must belong to the group.

    def test_payer_outside_group_is_rejected(self):
        outsider = User.objects.create_user(
            username="outsider",
            password="testpass123",
            name="Outsider",
        )

        response = self.client.post(
            self.expense_url,
            {
                "group_id": self.group.id,
                "paid_by": outsider.id,
                "amount": "1200.00",
                "description": "Dinner",
                "category": "food",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Expense.objects.count(), 0)
        self.assertEqual(ExpensePayment.objects.count(), 0)

    # Test 4: A group with no members cannot have an expense.

    def test_expense_for_empty_group_is_rejected(self):
        empty_group = Group.objects.create(name="Empty Group")

        response = self.client.post(
            self.expense_url,
            {
                "group_id": empty_group.id,
                "paid_by": self.mohit.id,
                "amount": "500.00",
                "description": "Lunch",
                "category": "food",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Expense.objects.count(), 0)

    # Test 5: Balances are calculated correctly.

    def test_balance_calculation(self):
        response = self.create_expense("1200.00")

        self.assertEqual(response.status_code, 201)

        response = self.client.get(self.balance_url)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data,
            {
                "Rahul": {
                    "owes": {
                        "Mohit": 400.0,
                    }
                },
                "Ankit": {
                    "owes": {
                        "Mohit": 400.0,
                    }
                },
            },
        )

    # Test 6: Expenses can be filtered by category.

    def test_expense_category_filter(self):
        self.create_expense("1200.00")

        Expense.objects.create(
            group=self.group,
            amount=Decimal("500.00"),
            description="Taxi",
            category="travel",
        )

        response = self.client.get(
            self.group_expenses_url,
            {"category": "food"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["category"], "food")
        self.assertEqual(response.data[0]["description"], "Dinner")
