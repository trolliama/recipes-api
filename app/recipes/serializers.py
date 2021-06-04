from rest_framework import serializers

import core.models as models


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ("id", "name")
        read_only_fields = ("id",)
