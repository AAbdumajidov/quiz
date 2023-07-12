from django.http import HttpResponseNotFound
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.views import APIView
from .models import Category, Question, Option, Result, Contact
from .serializers import CategorySerializer, QuestionSerializer, ResultSerializer, ContactSerializer
from rest_framework.response import Response
from operator import attrgetter
from account.models import Account
from account.serializers import AccountSerializer
from django.utils import timezone
from django.db.models import Count, Avg
from django.db import models
from datetime import timedelta
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class QuestionListAPIView(generics.ListAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class ResultListAPIView(generics.ListAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = sorted(qs, key=attrgetter('result'), reverse=True)
        return qs


class AnswerFromStudentPostAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'category_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID of the category.'
                ),
                'questions': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'question_id': openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description='ID of the question.'
                            ),
                            'answers_id': openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description='ID of the answer.'
                            ),
                        }
                    )
                )
            },
            required=['category_id', 'questions'],
            example={
      "category_id": 1,
      "questions": [
        {
          "question_id": 1,
          "option_id": 1
        },
        {
          "question_id": 2,
          "option_id": 1
        },
{
          "question_id": 3,
          "option_id": 1
        },
{
          "question_id": 7,
          "option_id": 1
        }
      ]
    }
        )
    )
    def post(self, request):
        array = []
        count = 0
        t = 0
        account = self.request.user
        category_id = self.request.data.get('category_id')
        questions = self.request.data.get('questions')
        try:
            Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response("Category not found")
        result = Result.objects.create(account_id=account.id, category_id=category_id)
        for i in questions:
            question_id = int(i.get('question_id'))
            option_id = int(i.get('option_id'))
            try:
                question = Question.objects.get(id=question_id)
                option = Option.objects.get(id=option_id)
                print(F"{option}, {question}")
            except (Question.DoesNotExist, Option.DoesNotExist):
                continue
            option_ids = [i.id for i in question.option.all()]
            if option.id not in option_ids:
                return Response({'message': f"The '{option}' is not the option of '{question}'"})
            obj = {
                "option_id": option_id,
                "question_id": question_id,
                "is_correct": option.is_correct
            }
            array.append(obj)
            options = Question.objects.filter(option__is_correct=True, category_id=category_id, option=option, id=question_id)
            if options:
                count += 100 // len(questions)
            result.questions.add(question)

        result.result = count
        result.save()
        response_data = {
            'option_id': ResultSerializer(result).data,
            'result': array
        }
        return Response(response_data)

    # Example of sending data
    # {
    #   "category_id": 1,
    #   "questions": [
    #     {
    #       "question_id": 1,
    #       "option_id": 3
    #     },
    #     {
    #       "question_id": 2,
    #       "option_id": 1
    #     },
    #     ...
    #   ]
    # }

class AverageStatisticByCategoryListAPIView(APIView):
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response({'message': 'start_date and end_date parameters are required'}, status=400)

        try:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return Response({'message': 'start_date and end_date must be in the format YYYY-MM-DD'}, status=400)

        category_stats = Result.objects.filter(created_date__range=(start_date, end_date)).values_list('category')\
            .annotate(attempts=models.Count('id'), total_result=models.Avg('result'))\
            .values('category__title', 'account__username', 'attempts', 'total_result')

        statistics = []

        for category in category_stats:
            category_info = {
                'category': category['category__title'],
                'author': category["account__username"],
                'attempts': category['attempts'],
                'total_result': category['total_result']
            }
            statistics.append(category_info)

        return Response(statistics)

class AverageStatisticByAccountListAPIView(APIView):
    def get(self, request):
        accounts = Account.objects.all()
        account_results = []
        for account in accounts:
            average_result_account = Result.calculate_average_result_account(account)
            serialized_account = AccountSerializer(account).data
            account_results.append({
                "account": serialized_account,
                "average_result_account": average_result_account
            })
        return Response(account_results)


class DayStatic(APIView):
    def get(self, request, *args, **kwargs):
        day = []
        total_results = []
        average = []
        results = Result.objects.annotate(day=TruncDay('created_date'))
        daily_statistics = results.values('day').annotate(total_results=Count('id'), avg_result=Avg('result'))
        for stat in daily_statistics:
            day = stat['day']
            average = stat['avg_result']
            total_results = stat['total_results']
        return Response({"Day": day, "average": f"{round(average)}%", "Total Results": total_results})


class WeekStatic(APIView):
    def get(self, request, *args, **kwargs):
        week = []
        total_results = []
        average = []
        results = Result.objects.annotate(week=TruncWeek('created_date'))
        weekly_statistics = results.values('week').annotate(total_results=Count('id'), avg_result=Avg('result'))
        for stat in weekly_statistics:
            week = stat['week']
            average = stat['avg_result']
            total_results = stat['total_results']
        return Response({"week": week, "average": round(average), "Total Results": total_results})


class MonthStatic(APIView):
    def get(self, request, *args, **kwargs):
        month = []
        total_results = []
        average = []
        results = Result.objects.annotate(month=TruncMonth('created_date'))
        monthly_statistics = results.values('month').annotate(total_results=Count('id'), avg_result=Avg('result'))
        for stat in monthly_statistics:
            month = stat['month']
            average = stat['avg_result']
            total_results = stat['total_results']
        return Response({"Month": month, "average": round(average), "Total Results": total_results})
class ContactListCreateAPIView(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer