from rest_framework import serializers
from .models import Question, Option, Result, Category, Contact
from rest_framework.validators import UniqueTogetherValidator

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'question', 'option']

        validators = [
            UniqueTogetherValidator(
                queryset=Option.objects.all(),
                fields=['question', 'option']
            )
        ]



class QuestionSerializer(serializers.ModelSerializer):
    option = OptionSerializer(read_only=True, many=True)
    class Meta:
        model = Question
        fields = ['id', 'category', 'question', 'option']


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ['id', 'account', 'category', 'questions', 'result']


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'



