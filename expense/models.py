from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    name = models.CharField(max_length= 50, null= True, blank= True)
    



class Group(models.Model):
    name = models.CharField(max_length= 50)

    def __str__(self):
        return self.name


class GroupMembership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name= 'membership')
    member = models.ForeignKey(User, on_delete= models.CASCADE, related_name= 'members_of_group')
    # A member should join the group only one time
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields= ['group', 'member'],
                name= 'unique_group_member'
            )
        ]

    def __str__(self):
        return f"{self.group} --> {self.member}"




class Expense(models.Model):
    CATEGORY_CHOICES = [
        ("food", "Food"),
        ("travel", "Travel"),
        ("accommodation", "Accommodation"),
        ("shopping", "Shopping"),
        ("utilities", "Utilities"),
        ("other", "Other"),
    ]
    group = models.ForeignKey(Group, on_delete= models.CASCADE, related_name= 'expense_group')
    amount = models.DecimalField(max_digits= 10, decimal_places= 2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add= True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="other")

    def __str__(self):
        return f"{self.description} --> Rs:{self.amount}"


# If we use a seperate table for payments, later we can accept unequal share for expenses and calculate the total spendings
# --- of the group and settle amounts

class ExpensePayment(models.Model):
    expense = models.ForeignKey(Expense, on_delete= models.CASCADE, related_name='payments')
    member = models.ForeignKey(GroupMembership, on_delete= models.PROTECT, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places= 2)

    def __str__(self):
        return f"{self.expense.description} - {self.member} Amount paid: {self.amount_paid}"

# ==> we can find the total expense by adding all expenses and total pay by taking th sum of individual payments so I'm 
# removing model which saves splits, it is saved it can save computational time but Expense payment should remain source
# of truth

    


