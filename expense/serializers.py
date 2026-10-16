from django.contrib.auth import get_user_model
from django.utils.text import slugify
from rest_framework import serializers
from decimal import Decimal
from .models import *


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=50)

    class Meta:
        model = User
        fields = ["id", "name"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        name = validated_data["name"]

        # Generate a unique username
        base_username = slugify(name) or "user"
        username = base_username
        counter = 1

        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        return User.objects.create_user(
            username=username,
            name=name,
        )



class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name"]
        read_only_fields = ["id"]


class GroupMembershipCreateSerializer(serializers.ModelSerializer):
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        source="group"
    )
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="member"
    )

    class Meta:
        model = GroupMembership
        fields = ["group_id", "user_id"]

    def validate(self, attrs):
        if GroupMembership.objects.filter(
            group=attrs["group"],
            member=attrs["member"]
        ).exists():
            raise serializers.ValidationError(
                "This user is already a member of this group."
            )
        return attrs

    def create(self, validated_data):
        return GroupMembership.objects.create(**validated_data)




class ExpenseSerializer(serializers.ModelSerializer):
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        source="group"
    )

    # Accept the user ID when creating an expense.
    paid_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True
    )

    # Return the payer's name in the response.
    paid_by_name = serializers.SerializerMethodField()

    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.01")
    )

    category = serializers.ChoiceField(
        choices=Expense.CATEGORY_CHOICES,
        default="other"
    )

    class Meta:
        model = Expense
        fields = [
            "id",
            "group_id",
            "paid_by",
            "paid_by_name",
            "amount",
            "description",
            "category",
        ]
        read_only_fields = ["id", "paid_by_name"]

    def get_paid_by_name(self, obj):
        payment = obj.payments.select_related(
            "member__member"
        ).first()

        if payment:
            user = payment.member.member
            return user.name or user.username

        return None

    def validate(self, data):
        group = data["group"]
        payer = data["paid_by"]

        if not GroupMembership.objects.filter(group=group).exists():
            raise serializers.ValidationError({
                "group_id": "The group must have at least one member."
            })

        if not GroupMembership.objects.filter(
            group=group,
            member=payer
        ).exists():
            raise serializers.ValidationError({
                "paid_by": "The payer must belong to this group."
            })

        return data

    def create(self, data):
        payer = data.pop("paid_by")
        expense = Expense.objects.create(**data)

        membership = GroupMembership.objects.get(
            group=expense.group,
            member=payer
        )

        ExpensePayment.objects.create(
            expense=expense,
            member=membership,
            amount_paid=expense.amount
        )

        return expense
