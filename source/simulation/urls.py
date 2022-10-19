from django.urls import path
from . import views

app_name = 'simulation'
urlpatterns = [
    path('generate/', views.generate, name='generate'),
    path('generate_votes/', views.generate_votes, name='generate_votes'),
    path('seal/', views.seal, name='seal'),
    path('transactions/', views.transactions, name='transactions'),
    path('blockchain/', views.blockchain, name='blockchain'),
    path('block/<str:block_hash>/', views.block_detail, name='block_detail'),
    path('verify/', views.verify, name='verify'),
    path('sync/', views.sync, name='sync'),
    path('sync_with_firebase/', views.sync_with_firebase, name='sync_with_firebase'),
    path('sync_block/<int:block_id>/', views.sync_block, name='sync_block'),
]
