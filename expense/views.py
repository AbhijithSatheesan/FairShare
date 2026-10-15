from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User, Group, GroupMembership, Expense, ExpensePayment
from .serializers import (
    UserSerializer,
    GroupSerializer,
    GroupMembershipCreateSerializer,
    ExpenseSerializer,
)



# User Management


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer



# Group Management


class GroupListCreateView(generics.ListCreateAPIView):
    queryset = Group.objects.all().order_by("id")
    serializer_class = GroupSerializer


class AddGroupMemberView(generics.CreateAPIView):
    queryset = GroupMembership.objects.all()
    serializer_class = GroupMembershipCreateSerializer


class GroupMemberListView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        group = get_object_or_404(
            Group,
            pk=self.kwargs["group_id"]
        )

        return User.objects.filter(
            members_of_group__group=group
        ).order_by("id")


# Manage Expense

class ExpenseCreateView(generics.CreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer


class GroupExpenseListView(generics.ListAPIView):
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        return Expense.objects.filter(
            group_id=self.kwargs["group_id"]
        ).order_by("id")


# --> Calculate balance

class GroupBalancesView(APIView):
    def get(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)

        members = list(
            GroupMembership.objects.filter(group=group)
            .select_related("member")
        )

        if not members:
            return Response({})

       
        # the balance of each membe start at zero, if the balance becomes +ve then they should recieve, if negative -> they owe
        balances = {
            member.member_id: Decimal("0.00")
            for member in members
        }

        expenses = Expense.objects.filter(group=group)

        for expense in expenses:
            # Split the expense equally among group members.
            share = expense.amount / Decimal(len(members))

            # Subtract each member's share.
            for member in members:
                balances[member.member_id] -= share

            # Credit whoever actually paid.
            for payment in ExpensePayment.objects.filter(
                expense=expense
            ).select_related("member__member"):
                payer_id = payment.member.member_id
                balances[payer_id] += payment.amount_paid

        # we should seperate the member who paid
        debtors = [
            member for member in members
            if balances[member.member_id] < 0
        ]

        creditors = [
            member for member in members
            if balances[member.member_id] > 0
        ]

        result = {}

        # Match debts against money owed to one paid more
        for debtor in debtors:
            owes = -balances[debtor.member_id]
            debtor_name = (
                debtor.member.name or debtor.member.username
            )

            for creditor in creditors:
                available = balances[creditor.member_id]

                if owes <= 0:
                    break

                if available <= 0:
                    continue

                amount = min(owes, available)

                creditor_name = (
                    creditor.member.name or creditor.member.username
                )

                result.setdefault(debtor_name, {"owes": {}})
                result[debtor_name]["owes"][creditor_name] = round(
                    float(amount), 2
                )

                owes -= amount
                balances[creditor.member_id] -= amount

        return Response(result)


# See the expenses by categroy

class GroupExpenseListView(generics.ListAPIView):
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        queryset = Expense.objects.filter(
            group_id=self.kwargs["group_id"]
        )

        # Optional category filter
        category = self.request.query_params.get("category")

        if category:
            queryset = queryset.filter(category=category)

        return queryset.order_by("id")
