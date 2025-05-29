from rest_framework import serializers
from .models import Voter


class VoterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voter
        fields = '__all__'  # Or specify the fields you want to include

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Include the data field contents directly in the main object
        if 'data' in representation and isinstance(representation['data'], dict):
            for key, value in representation['data'].items():
                representation[key] = value
        return representation