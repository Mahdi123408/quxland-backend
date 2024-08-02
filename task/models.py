from django.db import models
from authentication.models import CustomUser


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    expired = models.BooleanField(default=False)
    point_value = models.IntegerField(default=0)
    image_url = models.ImageField(upload_to='tasks')
    link = models.URLField(max_length=500)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title[:15]}: {self.point_value}'

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'


class CompletedTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='users_completed')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='completed_tasks')
    count = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.task} - {self.user}'

    class Meta:
        verbose_name = 'Completed Task'
        verbose_name_plural = 'Completed Tasks'
        unique_together = (('task', 'user'),)


# class DailyTask(models.Model):
#     title = models.CharField(max_length=200)
#     description = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     expires_at = models.DateTimeField()
#     expired = models.BooleanField(default=False)
#     point_value = models.IntegerField(default=0)
#     image_url = models.ImageField(upload_to='tasks/daily/')
#     is_active = models.BooleanField(default=False)
#
#     def __str__(self):
#         return f'{self.title[:15]}: {self.point_value}'
#
#     class Meta:
#         verbose_name = 'Daily Task'
#         verbose_name_plural = 'Daily Tasks'


class DailyCompletedTask(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='daily_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    last_claimed_at = models.DateTimeField(auto_now=True)
    count = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.user}: {self.count}'

    class Meta:
        verbose_name = 'Daily Completed Task'
        verbose_name_plural = 'Daily Completed Tasks'
