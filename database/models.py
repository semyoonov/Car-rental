from tortoise.models import Model
from tortoise import fields

class Car(Model):
    id = fields.IntField(pk=True)
    brand = fields.CharField(max_length=100)
    model = fields.CharField(max_length=100)
    price = fields.IntField()    
    photo = fields.CharField(max_length=255, null=True)