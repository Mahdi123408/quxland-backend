from rest_framework import serializers
from ticket import models


class TicketSerializer(serializers.ModelSerializer):
    user_requested = serializers.SerializerMethodField()

    class Meta:
        model = models.Ticket
        fields = ['id', 'title', 'description', 'user_requested', 'ticket_type', 'file', 'answered', 'created_at',
                  'updated_at']

    def get_user_requested(self, obj):
        if obj.user:
            return obj.user.to_dict()
