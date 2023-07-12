from django.urls import path
from .views import CategoryListAPIView, QuestionListAPIView, ResultListAPIView, \
    AnswerFromStudentPostAPIView, AverageStatisticByCategoryListAPIView, AverageStatisticByAccountListAPIView, \
    DayStatic, WeekStatic, MonthStatic, ContactListCreateAPIView

urlpatterns = [
    path('category/', CategoryListAPIView.as_view()),
    path('category/<int:category_id>/question/', QuestionListAPIView.as_view()),
    path('result/', ResultListAPIView.as_view()),
    path('answer_from_student/', AnswerFromStudentPostAPIView.as_view()),
    path('average_by_category/', AverageStatisticByCategoryListAPIView.as_view()),
    path('average_by_account/', AverageStatisticByAccountListAPIView.as_view()),
    path('day_statistic/', DayStatic.as_view()),
    path('week_statistic/', WeekStatic.as_view()),
    path('month_statistic/', MonthStatic.as_view()),
    path('contact/', ContactListCreateAPIView.as_view()),
]