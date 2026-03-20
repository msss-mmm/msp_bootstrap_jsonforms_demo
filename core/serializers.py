from rest_framework import serializers
from .models import Document, Traveler, TravelerStep, Instruction, InstructionStep

class TravelerStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelerStep
        fields = '__all__'

class TravelerSerializer(serializers.ModelSerializer):
    steps = TravelerStepSerializer(many=True, read_only=True)
    class Meta:
        model = Traveler
        fields = '__all__'

class InstructionStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstructionStep
        fields = '__all__'

class InstructionSerializer(serializers.ModelSerializer):
    steps = InstructionStepSerializer(many=True, read_only=True)
    class Meta:
        model = Instruction
        fields = '__all__'

class DocumentSerializer(serializers.ModelSerializer):
    traveler_details = TravelerSerializer()
    instruction_details = InstructionSerializer()

    class Meta:
        model = Document
        fields = '__all__'

    def update(self, instance, validated_data):
        traveler_data = validated_data.pop('traveler_details', None)
        instruction_data = validated_data.pop('instruction_details', None)

        instance.name = validated_data.get('name', instance.name)
        instance.save()

        if traveler_data and hasattr(instance, 'traveler_details'):
            traveler = instance.traveler_details
            for attr, value in traveler_data.items():
                setattr(traveler, attr, value)
            traveler.save()

        if instruction_data and hasattr(instance, 'instruction_details'):
            instruction = instance.instruction_details
            for attr, value in instruction_data.items():
                setattr(instruction, attr, value)
            instruction.save()

        return instance
