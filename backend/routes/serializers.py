from rest_framework import serializers


class TripInputSerializer(serializers.Serializer):
    current_location = serializers.CharField(max_length=255)
    pickup_location = serializers.CharField(max_length=255)
    dropoff_location = serializers.CharField(max_length=255)
    current_cycle_used = serializers.FloatField(min_value=0, max_value=70)


class StopSerializer(serializers.Serializer):
    name = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    type = serializers.CharField() 
    duration = serializers.FloatField(required=False)  


class TripOutputSerializer(serializers.Serializer):
    total_distance = serializers.FloatField()
    total_duration = serializers.FloatField()
    route_data = serializers.DictField()  
    stops = StopSerializer(many=True)
    eld_logs = ELDLogSerializer(many=True)
