from django.urls import path

from .views import AdminView, ModelView, EditModelView, AdminLoginView

urlpatterns = [
    path('', AdminView.as_view(), name='dj_admin_plus'),
    path('<str:app_label>/<str:model_name>/', ModelView.as_view(), name='model_view'),
    path('<str:app_label>/<str:model_name>/add/', EditModelView.as_view(add_mode=True), name='add_model_view'),
    path('<str:app_label>/<str:model_name>/<int:pk>/change/', EditModelView.as_view(),
         name='change_model_view'),

    path('login/', AdminLoginView.as_view(), name='dj_admin_login')
]