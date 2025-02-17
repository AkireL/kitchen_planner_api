from tortoise.models import Model
from tortoise import fields

class Recipe(Model):
    id = fields.IntField(primary_key=True)
    title = fields.TextField()
    ingredients = fields.JSONField(default=[])
    preparation = fields.TextField()
    duration = fields.TextField()
    schedule_at = fields.DateField()

class User(Model):
    id = fields.IntField(primary_key=True)
    username = fields.CharField(max_length=255, unique=True)
    email = fields.CharField(max_length=255, null=True)
    full_name = fields.CharField(max_length=255, null=True)

class Hash(Model):
    id = fields.IntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="hash", on_delete=fields.CASCADE)
    hashed_password = fields.CharField(max_length=255)
