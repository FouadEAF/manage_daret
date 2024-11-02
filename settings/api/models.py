from django.db import models


class Helpers(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @classmethod
    def get_all(cls):
        data = cls.objects.all()
        return data

    @classmethod
    def get_one(cls, **filters):
        try:
            return cls.objects.get(**filters)
        except cls.DoesNotExist:
            # return None
            return False
        except cls.MultipleObjectsReturned:
            # Handle the case where more than one object is returned
            # return None
            return False

    @classmethod
    def create(cls, **data):
        new_item = cls.objects.create(**data)
        if new_item:
            return True
        return False

    @classmethod
    def update(cls, record_id, **data):
        update_count = cls.objects.filter(id=record_id).update(**data)
        if update_count:
            return True
        return False

    @classmethod
    def delete(cls, record_id):
        delete_record = cls.objects.filter(id=record_id).delete()[0]
        if delete_record:
            return True
        return False

    @classmethod
    def filter(cls, **filters):
        return cls.objects.filter(**filters)
