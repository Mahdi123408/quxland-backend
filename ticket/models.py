from django.db import models
from authentication.models import CustomUser


class TicketType(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    ticket_type = models.ForeignKey(TicketType, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to='tickets')
    answered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} - {self.id}'

    def save(self, *args, **kwargs):
        if self.answers:
            self.answered = True
        super(Ticket, self).save(*args, **kwargs)


class TicketAnswer(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ticket

    def save(self, *args, **kwargs):
        self.ticket.answered = True
        super(TicketAnswer, self).save(*args, **kwargs)
