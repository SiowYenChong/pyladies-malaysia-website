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


# --- S3 Helper Functions ---

def fetch_json_from_s3(relative_path):
    """Fetches JSON content from a static file stored on S3."""
    try:
        # Get the public URL for the file from the static file storage (S3)
        file_url = staticfiles_storage.url(relative_path)
        
        # Use requests to fetch the content from the S3 URL
        response = requests.get(file_url)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except Exception as e:
        print(f"Error fetching JSON from S3 at {relative_path}: {e}")
        # Return an empty list/dict based on typical JSON data structure
        if "expertise_map" in relative_path:
            return {}
        return []

def list_s3_files(prefix):
    """
    Lists image files in a specific S3 path (prefix).
    Returns a list of filenames (relative to the base prefix).
    """
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        
        # 🌟 CORRECTED: The S3 listing prefix must include AWS_LOCATION (e.g., 'theme/static/')
        # The final prefix will look like: 'theme/static/images/committee/'
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
                
                # Strip the full S3 prefix to get the filename
                relative_path = full_key.replace(s3_prefix, '', 1).lstrip('/')
                
                # Exclude the directory path itself and non-image files
                if relative_path and relative_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    # We only need the base filename (e.g., 'name_role.jpg') 
                    # for the parsing logic in the view functions.
                    filenames.append(relative_path)
        
        return filenames
    
    except ClientError as e:
        print(f"Boto3 ClientError listing S3 files for prefix {prefix}: {e}")
        return []
    except Exception as e:
        print(f"General error listing S3 files: {e}")
        return []

# --- JSON Path Constants ---
BLOG_POSTS_PATH = 'images/blog/blog_posts.json'
EVENTS_DATA_PATH = 'images/events/events_data.json'
SPEAKERS_EXPERTISE_MAP_PATH = 'images/speakers/speakers_expertise_map.json'

# --- S3 Directory Prefix Constants ---
COMMITTEE_PREFIX = 'images/committee/'
SPEAKERS_PREFIX = 'images/speakers/'
GROUPPIC_PREFIX = 'images/grouppic/'


# --- Views ---

def become_member(request):
    return render(request, 'becomeMember.html')

# A helper function to load the JSON data (REPLACED LOCAL FILE READ)
def load_blog_posts():
    """Loads blog post data from S3."""
    return fetch_json_from_s3(BLOG_POSTS_PATH)

def blog(request):
    posts = load_blog_posts()
    print(f"Loaded {len(posts)} posts.")
    posts.sort(key=lambda x: x['date'], reverse=True)
    return render(request, 'blog.html', {'posts': posts})

def blog_detail(request, slug):
    """View to display a single blog post based on its slug."""
    posts = load_blog_posts()
    post = next((p for p in posts if p['slug'] == slug), None)
    if post is None:
        raise Http404("Blog post not found.")

    return render(request, 'blog_detail.html', {'post': post})

def home(request):
    """
    Calculates dynamic statistics for the website from JSON and S3 image files.
    """
    # Initialize all counters to zero
    total_members = 0
    upcoming_events = 0
    past_events = 0
    mentors = 0
    
    # Count committee members from S3 (REPLACED os.listdir)
    committee_image_files = list_s3_files(COMMITTEE_PREFIX)
    # 🌟 FIX: This will now return the correct count because list_s3_files works
    total_members += len(committee_image_files) 

    # Count speakers from S3 (REPLACED os.listdir)
    speakers_image_files = list_s3_files(SPEAKERS_PREFIX)
    # 🌟 FIX: This will now return the correct count
    mentors = len(speakers_image_files) 
    total_members += mentors
        
    # Count upcoming and past events (REPLACED LOCAL FILE READ)
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
    """
    Loads committee and group picture data by listing S3 contents and parsing filenames.
    """
    # --- Committee Member Logic (Uses S3 Listing) ---
    # This now returns a list of filenames (e.g., ['name_role.jpg', ...])
    committee_image_files = list_s3_files(COMMITTEE_PREFIX)
    committee_members = []
    
    for filename in committee_image_files:
        # The filename parsing logic remains, using the base filename
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
            # Path is constructed as 'images/committee/name_role.jpg'
            # which is correctly resolved by {% static %} using the settings.py AWS_LOCATION prefix
            'image_url': f'{COMMITTEE_PREFIX}{filename}' 
        }
        committee_members.append(member)

    # --- Group Picture Logic (Uses S3 Listing) ---
    grouppic_image_files = list_s3_files(GROUPPIC_PREFIX)
    grouppic_urls = []
    
    # Use sorted() for consistent ordering
    for filename in sorted(grouppic_image_files):
        # Path is constructed as 'images/grouppic/photo.jpg'
        grouppic_urls.append(f'{GROUPPIC_PREFIX}{filename}')

    context = {
        'committee_members': committee_members,
        'grouppic_urls': grouppic_urls,
    }
    
    return render(request, 'about.html', context)

def events(request):
    raw_events_data = fetch_json_from_s3(EVENTS_DATA_PATH)
    
    # Determine the desired view (Upcoming or Past)
    is_past_events_page = request.GET.get('m') == 'false'
    today = datetime.now().date()
    
    upcoming_events = []
    past_events = []
    
    for event in raw_events_data:
        start_date_str = event.get('date')
        end_date_str = event.get('end_date')

        # Format the dates for display and determine status
        try:
            start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%d')
            event_date = start_date_obj.date()
            
            # Formatting logic
            if end_date_str and start_date_str != end_date_str:
                end_date_obj = datetime.strptime(end_date_str, '%Y-%m-%d')
                formatted_date = f"{start_date_obj.strftime('%B %d')} - {end_date_obj.strftime('%B %d, %Y')}"
            else:
                formatted_date = start_date_obj.strftime('%B %d, %Y')
        
            # Add the new formatted_date to the event dictionary
            event['formatted_date'] = formatted_date

            # Filter events into the appropriate list
            if event_date >= today:
                upcoming_events.append(event)
            else:
                past_events.append(event)
                
        except (ValueError, TypeError):
            event['formatted_date'] = "Invalid Date"
            continue # Skip invalid events

    # Select the correct list based on the page filter
    if is_past_events_page:
        # Sort past events newest to oldest (reverse chronological)
        final_events = sorted(past_events, key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d').date(), reverse=True)
    else:
        # Sort upcoming events oldest to newest (chronological)
        final_events = sorted(upcoming_events, key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d').date())
        
    # Pass all raw events data for the calendar component's JavaScript, regardless of view
    # The calendar usually needs all data to populate the full month/year.
    events_json = json.dumps(raw_events_data)
    
    context = {
        'events': final_events,
        'events_json': events_json,
        'is_past_events_page': is_past_events_page
    }

    return render(request, 'events.html', context)

def speakers(request):
    
    speakers_data = []
    expertises = set()

    # Step 1: Load the expertise mapping from S3 (REPLACED LOCAL FILE READ)
    expertise_map = fetch_json_from_s3(SPEAKERS_EXPERTISE_MAP_PATH) or {}

    # Step 2: Process speaker images and combine with expertise data (Uses S3 Listing)
    speaker_image_files = list_s3_files(SPEAKERS_PREFIX)
    
    for filename in speaker_image_files:
        
        base_name = os.path.splitext(filename)[0]
        parts = base_name.split('_')
        
        # Extract and format the name
        name_part = parts[0]
        formatted_name = ' '.join([word.capitalize() for word in name_part.replace('-', ' ').split()])
        
        # Extract and format the title, or use a default
        if len(parts) > 1:
            title_part = parts[1]
            title = ' '.join([word.capitalize() for word in title_part.replace('-', ' ').split()])
        else:
            title = 'Speaker' # Default title if none is specified

        # Retrieve expertise from the loaded map, defaulting to an empty list
        speaker_expertise = expertise_map.get(formatted_name, [])
        
        speaker_info = {
            'name': formatted_name,
            'title': title,
            # S3 relative path
            'image_url': f'{SPEAKERS_PREFIX}{filename}',
            'expertise': speaker_expertise
        }
        speakers_data.append(speaker_info)
        
        # Add expertises to the set
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