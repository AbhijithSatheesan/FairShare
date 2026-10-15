
from django.urls import path
from .views import *
urlpatterns = [
    path("users/", UserListCreateView.as_view(), name="users"),

    path("groups/", GroupListCreateView.as_view(), name="groups"),
    path("groups/members/", AddGroupMemberView.as_view(), name="add-member"),
    path(
        "groups/<int:group_id>/members/",
        GroupMemberListView.as_view(),
        name="group-members",
    ),

    path("expenses/", ExpenseCreateView.as_view(), name="expenses"),
    path(
        "groups/<int:group_id>/expenses/",
        GroupExpenseListView.as_view(),
        name="group-expenses",
    ),
    path(
        "groups/<int:group_id>/balances/",
        GroupBalancesView.as_view(),
        name="group-balances",
    ),
]
