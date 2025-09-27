import os
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse, Http404
from datetime import date
import json
from datetime import datetime
from django.contrib.staticfiles.storage import staticfiles_storage 
import requests 
import boto3 
from botocore.exceptions import ClientError 


def fetch_json_from_s3(relative_path):
    try:
        file_url = staticfiles_storage.url(relative_path)
        response = requests.get(file_url)
        response.raise_for_status() 
        return response.json()
    except Exception as e:
        print(f"Error fetching JSON from S3 at {relative_path}: {e}")
        if "expertise_map" in relative_path:
            return {}
        return []

def list_s3_files(prefix):
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        
        s3_prefix = f"{settings.AWS_LOCATION}/{prefix}" 

        response = s3.list_objects_v2(
            Bucket=bucket_name,
            Prefix=s3_prefix,
            Delimiter='/'
        )
        
        filenames = []
        if 'Contents' in response:
            for obj in response['Contents']:
                full_key = obj['Key']
                
                relative_path = full_key.replace(s3_prefix, '', 1).lstrip('/')
                
                if relative_path and relative_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    filenames.append(relative_path)
        
        return filenames
    
    except ClientError as e:
        print(f"Boto3 ClientError listing S3 files for prefix {prefix}: {e}")
        return []
    except Exception as e:
        print(f"General error listing S3 files: {e}")
        return []

BLOG_POSTS_PATH = 'images/blog/blog_posts.json'
EVENTS_DATA_PATH = 'images/events/events_data.json'
SPEAKERS_EXPERTISE_MAP_PATH = 'images/speakers/speakers_expertise_map.json'

COMMITTEE_PREFIX = 'images/committee/'
SPEAKERS_PREFIX = 'images/speakers/'
GROUPPIC_PREFIX = 'images/grouppic/'


def become_member(request):
    return render(request, 'becomeMember.html')

def load_blog_posts():
    return fetch_json_from_s3(BLOG_POSTS_PATH)

def blog(request):
    posts = load_blog_posts()
    print(f"Loaded {len(posts)} posts.")
    posts.sort(key=lambda x: x['date'], reverse=True)
    return render(request, 'blog.html', {'posts': posts})

def blog_detail(request, slug):
    posts = load_blog_posts()
    post = next((p for p in posts if p['slug'] == slug), None)
    if post is None:
        raise Http404("Blog post not found.")

    return render(request, 'blog_detail.html', {'post': post})

def home(request):
    total_members = 0
    upcoming_events = 0
    past_events = 0
    mentors = 0
    
    committee_image_files = list_s3_files(COMMITTEE_PREFIX)
    total_members += len(committee_image_files) 

    speakers_image_files = list_s3_files(SPEAKERS_PREFIX)
    mentors = len(speakers_image_files) 
    total_members += mentors
        
    events_data = fetch_json_from_s3(EVENTS_DATA_PATH)
    
    today = datetime.now().date()
    for event in events_data:
        try:
            event_date = datetime.strptime(event['date'], '%Y-%m-%d').date()
            if event_date >= today:
                upcoming_events += 1
            else:
                past_events += 1
        except (ValueError, KeyError):
            continue

    context = {
        'total_members': total_members,
        'upcoming_events': upcoming_events,
        'mentors': mentors,
        'past_events': past_events,
    }
    return render(request, 'home.html', context)

def about(request):
    committee_image_files = list_s3_files(COMMITTEE_PREFIX)
    committee_members = []
    
    for filename in committee_image_files:
        base_name, file_extension = os.path.splitext(filename)
        parts = base_name.rsplit('_', 1)
        
        if len(parts) == 2:
            name_part, role_part = parts
            role = role_part.replace('-', ' ').capitalize()
        else:
            name_part = parts[0]
            role = 'Committee Member'
            
        formatted_name = ' '.join(word.capitalize() for word in name_part.replace('-', ' ').split())
        member = {
            'name': formatted_name,
            'role': role,
            'image_url': f'{COMMITTEE_PREFIX}{filename}' 
        }
        committee_members.append(member)

    grouppic_image_files = list_s3_files(GROUPPIC_PREFIX)
    grouppic_urls = []
    
    for filename in sorted(grouppic_image_files):
        grouppic_urls.append(f'{GROUPPIC_PREFIX}{filename}')

    context = {
        'committee_members': committee_members,
        'grouppic_urls': grouppic_urls,
    }
    
    return render(request, 'about.html', context)

def events(request):
    events = []

    raw_events_data = fetch_json_from_s3(EVENTS_DATA_PATH)
    
    for event in raw_events_data:
        start_date_str = event.get('date')
        end_date_str = event.get('end_date')

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            if end_date_str and start_date_str != end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                formatted_date = f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
            else:
                formatted_date = start_date.strftime('%B %d, %Y')
        except (ValueError, TypeError):
            formatted_date = "Invalid Date" 

        event['formatted_date'] = formatted_date
        events.append(event)
    
    events_json = json.dumps(events)
    
    context = {
        'events': events,
        'events_json': events_json,
        'is_past_events_page': request.GET.get('m') == 'false'
    }

    return render(request, 'events.html', context)

def speakers(request):
    
    speakers_data = []
    expertises = set()

    expertise_map = fetch_json_from_s3(SPEAKERS_EXPERTISE_MAP_PATH) or {}

    speaker_image_files = list_s3_files(SPEAKERS_PREFIX)
    
    for filename in speaker_image_files:
        
        base_name = os.path.splitext(filename)[0]
        parts = base_name.split('_')
        
        name_part = parts[0]
        formatted_name = ' '.join([word.capitalize() for word in name_part.replace('-', ' ').split()])
        
        if len(parts) > 1:
            title_part = parts[1]
            title = ' '.join([word.capitalize() for word in title_part.replace('-', ' ').split()])
        else:
            title = 'Speaker' 

        speaker_expertise = expertise_map.get(formatted_name, [])
        
        speaker_info = {
            'name': formatted_name,
            'title': title,
            'image_url': f'{SPEAKERS_PREFIX}{filename}',
            'expertise': speaker_expertise
        }
        speakers_data.append(speaker_info)
        
        for exp in speaker_expertise:
            expertises.add(exp)

    context = {
        'speakers_json': json.dumps(speakers_data),
        'expertises': sorted(list(expertises))
    }
    
    return render(request, 'speakers.html', context)

def articles(request):
    return render(request, 'articles.html')

def faq(request):
    return render(request, 'faq.html')