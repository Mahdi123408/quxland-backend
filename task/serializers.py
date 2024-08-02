from rest_framework import serializers
from task import models


class TaskSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(TaskSerializer, self).__init__(*args, **kwargs)

    is_done = serializers.SerializerMethodField()

    class Meta:
        model = models.Task
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'expires_at', 'point_value',
                  'image_url', 'is_done', 'link', 'is_active', 'expired']

    def get_is_done(self, obj):
        if obj.users_completed:
            users = obj.users_completed.all()
            for user in users:
                if user.user == self.user and user.count >= 2:
                    return True
        return False

# class DailyTaskSerializer(serializers.ModelSerializer):
#     last_submit = serializers.SerializerMethodField()
#     can_submit = serializers.SerializerMethodField()
#     can_submit_time = serializers.SerializerMethodField()
#
#     class Meta:
#         model = models.DailyTask
#         fields = '__all__'
#
#     def __init__(self, *args, **kwargs):
#         self.user = kwargs.pop('user', None)
#         super(DailyTaskSerializer, self).__init__(*args, **kwargs)
#
#     def get_last_submit(self, obj):
#         chek = models.DailyCompletedTask.objects.filter(daily_task_id=obj.id, user_id=self.user.id).first()
#         if chek:
#             return chek.last_claimed_at + timedelta(hours=3, minutes=30)
#
#     def get_can_submit_time(self, obj):
#         chek = models.DailyCompletedTask.objects.filter(daily_task_id=obj.id, user_id=self.user.id).first()
#         if chek:
#             return chek.last_claimed_at + timedelta(days=1, hours=3, minutes=30)
#
#     def get_can_submit(self, obj):
#         can_submit_time = self.get_can_submit_time(obj)
#         if can_submit_time:
#             now = timezone.now() + timedelta(hours=3, minutes=30)
#             if can_submit_time < now:
#                 return True
#         return False
