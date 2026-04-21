from django.db import models
from accounts.models.user import User

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    status = models.CharField(max_length=20, choices=[('confirmation', 'Confirmation'), ('cancellation', 'Cancellation')], default='confirmation')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.email} - {'Read' if self.is_read else 'Unread'}"