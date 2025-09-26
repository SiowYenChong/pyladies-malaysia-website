import os
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse, Http404
from datetime import date
import json
from datetime import datetime



def become_member(request):
    return render(request, 'becomeMember.html')

# A helper function to load the JSON data
def load_blog_posts():
    """
    Loads blog post data from the specified JSON file.
    """
    # Construct the correct file path using the user-provided location
    file_path = os.path.join(settings.BASE_DIR, 'theme', 'static', 'images', 'blog', 'blog_posts.json')
    
    # Check if the file exists before trying to open it
    if not os.path.exists(file_path):
        # Return an empty list if the file is not found
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def blog(request):
    posts = load_blog_posts()
    print(f"Loaded {len(posts)} posts.") # Debugging line
    posts.sort(key=lambda x: x['date'], reverse=True)
    return render(request, 'blog.html', {'posts': posts})

def blog_detail(request, slug):
    """View to display a single blog post based on its slug."""
    posts = load_blog_posts()
    # Find the specific post by its slug
    post = next((p for p in posts if p['slug'] == slug), None)
    if post is None:
        raise Http404("Blog post not found.")

    return render(request, 'blog_detail.html', {'post': post})

def home(request):
    """
    Calculates dynamic statistics for the website from JSON and image files.
    """
    speakers_image_dir = os.path.join(settings.BASE_DIR, 'theme', 'static', 'images', 'speakers')
    committee_image_dir = os.path.join(settings.BASE_DIR, 'theme', 'static', 'images', 'committee')
    events_data_path = os.path.join(settings.BASE_DIR, 'theme', 'static', 'images', 'events', 'events_data.json')
    
    # Initialize all counters to zero
    total_members = 0
    upcoming_events = 0
    past_events = 0
    mentors = 0 # Now all speakers are considered mentors
    
    # Count committee members from the number of image files in the directory
    if os.path.exists(committee_image_dir):
        image_files = [f for f in os.listdir(committee_image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        total_members += len(image_files)

    # Count speakers from the number of image files in the directory
    if os.path.exists(speakers_image_dir):
        image_files = [f for f in os.listdir(speakers_image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        # Your request specifies to "consider them as mentors"
        mentors = len(image_files)
        total_members += mentors
        
    # Count upcoming and past events
    if os.path.exists(events_data_path):
        with open(events_data_path, 'r', encoding='utf-8') as f:
            events_data = json.load(f)
            today = datetime.now().date()
            for event in events_data:
                try:
                    # Your JSON uses "date", not "start_date"
                    event_date = datetime.strptime(event['date'], '%Y-%m-%d').date()
                    if event_date >= today:
                        upcoming_events += 1
                    else:
                        past_events += 1
                except (ValueError, KeyError):
                    # Continue if the date format is wrong or the key is missing
                    continue

    context = {
        'total_members': total_members,
        'upcoming_events': upcoming_events,
        'mentors': mentors,
        'past_events': past_events,
    }
    return render(request, 'home.html', context)

def about(request):
    # --- Committee Member Logic ---
    committee_image_dir = os.path.join(settings.BASE_DIR, 'theme', 'static', 'images', 'committee')
    committee_members = []
    if os.path.exists(committee_image_dir):
        image_files = os.listdir(committee_image_dir)
        for filename in image_files:
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                continue
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
                'image_url': f'images/committee/{filename}'
            }
            committee_members.append(member)

    # --- Group Picture Logic ---
    grouppic_dir = os.path.join(settings.BASE_DIR, 'theme', 'static', 'images', 'grouppic')
    grouppic_urls = []
    if os.path.exists(grouppic_dir):
        grouppic_files = sorted(os.listdir(grouppic_dir))
        for filename in grouppic_files:
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                continue
            grouppic_urls.append(f'images/grouppic/{filename}')

    context = {
        'committee_members': committee_members,
        'grouppic_urls': grouppic_urls,
    }
    
    return render(request, 'about.html', context)

def events(request):
    events_data_path = os.path.join(settings.BASE_DIR, 'theme', 'static', 'images', 'events', 'events_data.json')
    events = []

    if os.path.exists(events_data_path):
        with open(events_data_path, 'r', encoding='utf-8') as f:
            raw_events_data = json.load(f)
            for event in raw_events_data:
                # Get the raw date strings from the JSON
                start_date_str = event.get('date')
                end_date_str = event.get('end_date')

                # Format the dates for display
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    if end_date_str and start_date_str != end_date_str:
                        # For multi-day events, format as "November 1 - November 2, 2025"
                        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                        formatted_date = f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
                    else:
                        # For single-day events, format as "November 1, 2025"
                        formatted_date = start_date.strftime('%B %d, %Y')
                except (ValueError, TypeError):
                    formatted_date = "Invalid Date" # Handle malformed dates gracefully

                # Add the new formatted_date to the event dictionary
                event['formatted_date'] = formatted_date
                events.append(event)
    
    # You'll also need to pass a JSON-formatted version of the events for the calendar
    events_json = json.dumps(events)
    
    context = {
        'events': events,
        'events_json': events_json,
        'is_past_events_page': request.GET.get('m') == 'false'
    }

    return render(request, 'events.html', context)

def speakers(request):
    speakers_image_dir = os.path.join(settings.BASE_DIR, 'theme', 'static', 'images', 'speakers')
    speakers_expertise_map_path = os.path.join(speakers_image_dir, 'speakers_expertise_map.json')
    
    speakers_data = []
    expertises = set()

    # Step 1: Load the expertise mapping from the JSON file
    expertise_map = {}
    if os.path.exists(speakers_expertise_map_path):
        with open(speakers_expertise_map_path, 'r', encoding='utf-8') as f:
            expertise_map = json.load(f)

    # Step 2: Process speaker images and combine with expertise data
    if os.path.exists(speakers_image_dir):
        image_files = os.listdir(speakers_image_dir)
        for filename in image_files:
            # Skip the expertise map file itself
            if filename == 'speakers_expertise_map.json':
                continue
                
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                continue
            
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
                'image_url': f'images/speakers/{filename}',
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

