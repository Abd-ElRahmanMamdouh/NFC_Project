from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class URLBatch(models.Model):
    count = models.PositiveBigIntegerField("Count", blank=True, null=True)
    user = models.ForeignKey(
        User,
        related_name="user_URL_batchs",
        verbose_name="User",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)


    def __str__(self):
        return f"{self.count} URLs Generated at {self.created_at.strftime('%Y-%m-%d, %H:%M %p')} By {self.user}"


class CodeBatch(models.Model):
    count = models.PositiveBigIntegerField("Count", blank=True, null=True)
    user = models.ForeignKey(
        User,
        related_name="user_code_batchs",
        verbose_name="User",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)


    def __str__(self):
        return f"{self.count} Purchasing Codes Generated at {self.created_at.strftime('%Y-%m-%d, %H:%M %p')} By {self.user}"
