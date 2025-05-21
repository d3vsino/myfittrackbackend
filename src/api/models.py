from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_premium = models.BooleanField(default=False)
    # Macronutrient targets for maintenance
    maintenance_protein = models.FloatField(null=True, blank=True)
    maintenance_fat = models.FloatField(null=True, blank=True)
    maintenance_carbs = models.FloatField(null=True, blank=True)
    # Macronutrient targets for gain
    gain_protein = models.FloatField(null=True, blank=True)
    gain_fat = models.FloatField(null=True, blank=True)
    gain_carbs = models.FloatField(null=True, blank=True)
    # Macronutrient targets for loss
    loss_protein = models.FloatField(null=True, blank=True)
    loss_fat = models.FloatField(null=True, blank=True)
    loss_carbs = models.FloatField(null=True, blank=True)
    current_protein_goal = models.FloatField(null=True, blank=True)
    current_fat_goal = models.FloatField(null=True, blank=True)
    current_carbs_goal = models.FloatField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')], null=True, blank=True)
    height_cm = models.FloatField(null=True, blank=True)
    weight_kg = models.FloatField(null=True, blank=True)
    bmr = models.FloatField(null=True, blank=True)
    maintenance_calories = models.FloatField(null=True, blank=True)
    gain_calories = models.FloatField(null=True, blank=True)
    loss_calories = models.FloatField(null=True, blank=True)
    activity_level = models.CharField(
        max_length=20,
        choices=[
            ('sedentary', 'Sedentary'),
            ('light', 'Lightly active'),
            ('moderate', 'Moderately active'),
            ('active', 'Very active'),
            ('super', 'Super active'),
        ],
        null=True, blank=True
    )
    current_calorie_goal = models.FloatField(null=True, blank=True)

    # `first_name` and `last_name` already exist in AbstractUser

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Don't require username

    def __str__(self):
        return self.email

class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="New Chat")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.created_at:%Y-%m-%d})"


class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    is_user = models.BooleanField()
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        role = "User" if self.is_user else "AI"
        return f"{role} @ {self.timestamp:%H:%M}: {self.message[:30]}"

    def __str__(self):
        return f"{self.user.email} @ {self.timestamp:%Y-%m-%d %H:%M}: {self.message[:30]}..."

class CalorieLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='calorie_logs')
    date = models.DateField()
    calories = models.PositiveIntegerField()
    protein = models.FloatField(null=True, blank=True)
    fat = models.FloatField(null=True, blank=True)
    carbs = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'date')  # Only one log per user per day

    def __str__(self):
        return f"{self.user.username} - {self.date}: {self.calories} kcal"