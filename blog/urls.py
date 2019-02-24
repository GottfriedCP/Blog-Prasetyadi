from django.urls import path
from . import views

app_name = 'blog'
urlpatterns = [
    path('<int:year>/<slug:slug>/', views.article, name='article'),
    path('<int:year>/<slug:slug>/edit/', views.edit, name='edit'),
    path('<int:year>/<slug:slug>/delete/', views.delete, name='delete-confirm'),
    path('article-list-all/', views.list_all, name='list'),
    path('article-create/', views.create, name='create'),
    path('article-delete/', views.delete_commit, name='delete'),
    path('article-publish/', views.publish, name='publish'),

    path('tag/<str:name>/', views.tag, name='tag'),
    path('tag/<str:name>/edit/', views.tag_edit, name='tag-edit'),
    path('tag-create/', views.tag_create, name='tag-create'),
    path('category/<str:name>/', views.category, name='category'),
    path('category/<str:name>/edit/', views.category_edit, name='category-edit'),
    path('category-create/', views.category_create, name='category-create'),
    
    path('search/', views.search, name='search'),
    path('about/', views.about, name='about'),
    
    path('loginx/', views.login_view, name='login'),
    path('logoutx/', views.logout_view, name='logout'),
    
    path('', views.home, name='home'),
]
