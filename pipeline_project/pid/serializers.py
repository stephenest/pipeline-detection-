from rest_framework import serializers

class PipelineSerializer(serializers.Serializer):
    source = serializers.ListField(child=serializers.FloatField())
    destination = serializers.ListField(child=serializers.FloatField())