from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(primary_key=True)
    username = fields.CharField(max_length=255, unique=True)
    email = fields.CharField(max_length=255, null=True)
    fullname = fields.CharField(max_length=255, null=True)
    hashed_password = fields.CharField(max_length=255)


class Recipe(Model):
    id = fields.IntField(primary_key=True)
    title = fields.TextField()
    ingredients = fields.JSONField(default=[])
    preparation = fields.TextField(null=True)
    duration = fields.TextField(null=True)
    schedule_at = fields.DateField()
    user = fields.ForeignKeyField("models.User", related_name="recipe", on_delete=fields.CASCADE)
