from django.db import models
from django.conf import settings

from users.managers import ActiveRecordsManager

class Record(models.Model):
    TYPE_CHOICES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )

    amount = models.FloatField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES,db_index=True)
    CATEGORY_CHOICES = (
        ('food', 'Food'),
        ('salary', 'Salary'),
        ('transport', 'Transport'),
        ('rent', 'Rent'),
        ('other', 'Other'),
    )

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES,db_index=True)
    custom_category = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(db_index=True)
    description = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    is_deleted = models.BooleanField(default=False,db_index=True)
    objects=ActiveRecordsManager()
    all_objects=models.Manager()
    def delete(self, *args,**kwargs):
        self.is_deleted = True
        self.save()
    def restore(self):
        self.is_deleted = False
        self.save()
    def __str__(self):
        return f"{self.type} - {self.amount}"
    