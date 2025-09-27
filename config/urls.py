from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from theme import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('events/', views.events, name='events'),
    path('speakers/', views.speakers, name='speakers'),
    path('articles/', views.articles, name='articles'),
    path('faq/', views.faq, name='faq'),
    path('becomeMember/', views.become_member, name='become_member'),
    path('blog/', views.blog, name='blog'),
    path('<slug:slug>/', views.blog_detail, name='blog_detail'),
]

if settings.DEBUG:
    # Include django_browser_reload URLs only in DEBUG mode
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]