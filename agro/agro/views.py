from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib import auth
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import random
from django.core.mail import send_mail
from django.http import JsonResponse
import json
import time
from django.conf import settings
from datetime import datetime, timedelta
import logging
import requests

logger = logging.getLogger(__name__)

# OTP validity period in seconds (2 minutes)
OTP_VALIDITY_SECONDS = 120

def register_view(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                data = json.loads(request.body)
                username = data.get('username')
                email = data.get('email')
                password1 = data.get('password1')
                password2 = data.get('password2')
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)

            errors = {}

            # Validate email
            try:
                validate_email(email)
            except ValidationError:
                errors['email'] = 'Please enter a valid email address!'

            if password1 != password2:
                errors['password2'] = 'Passwords do not match!'

            if User.objects.filter(username=username).exists():
                errors['username'] = 'Username is already taken!'
            if User.objects.filter(email=email).exists():
                errors['email'] = 'Email is already registered!'

            if errors:
                return JsonResponse({'success': False, 'errors': errors}, status=400)

            # Generate OTP and store with timestamp
            otp = random.randint(1000, 9999)
            request.session['pending_user'] = {
                'username': username,
                'email': email,
                'password': password1,
                'otp': str(otp),
                'otp_timestamp': int(time.time())
            }
            request.session.modified = True

            subject = f"Verify Your AgroBuild Account, {username}!"
            message = (
                f"Dear {username},\n\n"
                f"Welcome to AgroBuild! 🌱 Thank you for joining our mission to grow a greener future.\n "
                f"To complete your registration, please use the following One-Time Password (OTP):\n\n"
                f"OTP: {otp}\n\n"
                f"This OTP is valid for {OTP_VALIDITY_SECONDS // 60} minutes. Do not share it with anyone to keep your account secure.\n\n"
                f"With Green Regards,\n"
                f"The AgroBuild Team\n"
                f"AGROBUILD Private Limited\n"
                f"B-42 Akruti Garden, Nehrunagar\n"
                f"Ahmedabad, 380015\n"
                f"📞 8128383925\n"
                f"✉️ shopmulti9859@gmail.com"
            )
            try:
                send_mail(
                    subject,
                    message,
                    None,
                    [email],
                    fail_silently=False,
                )
                return JsonResponse({'success': True, 'email': email})
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'Failed to send OTP email: {e}'}, status=500)
        else:
            messages.error(request, "Please enable JavaScript for registration.")
            return render(request, 'htmldemo.net/Registration.html')

    # For GET request, just render the initial registration page
    return render(request, 'htmldemo.net/Registration.html')


# NEW: otp_verify_view now handles AJAX POST requests for OTP validation
def otp_verify_view(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            otp_input = data.get('otp')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)

        pending_user = request.session.get('pending_user')

        if not pending_user:
            return JsonResponse({'success': False, 'message': 'OTP session expired or invalid. Please register again.'}, status=400)

        otp_timestamp = pending_user.get('otp_timestamp')
        if otp_timestamp and (time.time() - otp_timestamp > OTP_VALIDITY_SECONDS):
            # OTP has expired
            # Clear expired OTP from session to prevent re-use
            # del request.session['pending_user']
            request.session.modified = True
            return JsonResponse({'success': False, 'message': 'The OTP has expired. Please request a new one.'}, status=400)

        if otp_input == pending_user['otp']:
            # Correct OTP
            user = User.objects.create_user(
                username=pending_user['username'],
                email=pending_user['email'],
                password=pending_user['password']
            )
            del request.session['pending_user']
            request.session.modified = True
            # Return success and URL to redirect to
            return JsonResponse({'success': True, 'redirect_url': str(redirect('login').url)})
        else:
            # Incorrect OTP
            return JsonResponse({'success': False, 'message': 'Incorrect OTP. Please enter the correct OTP from your email.'}, status=400)
    else:
        # If someone directly accesses /otp-verify/ via GET or non-AJAX POST, redirect them to registration.
        messages.error(request, "Please complete registration first.")
        return redirect('registration')


def resend_otp_ajax_view(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        pending_user = request.session.get('pending_user')
        if not pending_user:
            return JsonResponse({'success': False, 'message': 'No pending registration session found. Please register again.'}, status=400)

        username = pending_user.get('username')
        email = pending_user.get('email')

        # Generate new OTP and update session
        new_otp = random.randint(1000, 9999)
        pending_user['otp'] = str(new_otp)
        pending_user['otp_timestamp'] = int(time.time()) # Update timestamp for new OTP
        request.session['pending_user'] = pending_user # Update the session
        request.session.modified = True

        subject = f"Your New AgroBuild OTP, {username}!"
        message = (
            f"Dear {username},\n\n"
            f"You requested a new OTP for your AgroBuild account. Here it is:\n\n"
            f"New OTP: {new_otp}\n\n"
            f"This OTP is valid for {OTP_VALIDITY_SECONDS // 60} minutes. Do not share it with anyone to keep your account secure.\n\n"
            f"With Green Regards,\n"
            f"The AgroBuild Team\n"
            f"AGROBUILD Private Limited\n"
            f"B-42 Akruti Garden, Nehrunagar\n"
            f"Ahmedabad, 380015\n"
            f"📞 8128383925\n"
            f"✉️ shopmulti9859@gmail.com"
        )
        try:
            send_mail(
                subject,
                message,
                None,
                [email],
                fail_silently=False,
            )
            return JsonResponse({'success': True, 'message': 'New OTP sent successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Failed to resend OTP email: {e}'}, status=500)
    return JsonResponse({'success': False, 'message': 'Invalid request method or not an AJAX call.'}, status=400)


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'htmldemo.net/login.html',
                        {'error': 'Please enter a valid email address!'})

        try:
            user = User.objects.get(email=email)
            authenticated_user = authenticate(username=user.username, password=password)
            if authenticated_user is not None:
                auth_login(request, authenticated_user)
                messages.success(request, "You have successfully logged in!")
                return redirect('index')
            else:
                return render(request, 'htmldemo.net/login.html',
                            {'error': 'Invalid password!'})
        except User.DoesNotExist:
            return render(request, 'htmldemo.net/login.html',
                        {'error': 'Email not found!'})
    else:
        return render(request, 'htmldemo.net/login.html')

def logout_view(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request, "You have successfully logged out!")
        return redirect('index')

def index(request):
    return render(request, 'htmldemo.net/index.html')

def agriculture_news_page(request):
    """
    Render the main agriculture news page
    """
    context = {
        'title': 'Agriculture News - India',
        'current_date': datetime.now().strftime('%A, %B %d'),
        'username': request.user.username if request.user.is_authenticated else 'Guest'
    }
    return render(request, 'htmldemo.net/news.html', context)

def fetch_agriculture_news(request):
    try:
        NEWS_API_KEY = getattr(settings, 'NEWS_API_KEY', None)
        if not NEWS_API_KEY:
            return JsonResponse({'error': 'News API key not configured', 'articles': []})
        # Use a single broad query for maximum results
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': 'agriculture OR farming OR crop OR harvest OR irrigation OR fertilizer OR seeds',
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 50,  # Fetch more articles
            'apiKey': NEWS_API_KEY,
            'from': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')  # Last 30 days
        }
        response = requests.get(url, params=params, timeout=15)
        all_articles = []
        if response.status_code == 200:
            data = response.json()
            all_articles = data.get('articles', [])
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article.get('url') and article.get('url') not in seen_urls:
                seen_urls.add(article.get('url'))
                unique_articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'urlToImage': article.get('urlToImage', ''),
                    'publishedAt': article.get('publishedAt', ''),
                    'source': {
                        'name': article.get('source', {}).get('name', 'Unknown Source')
                    },
                    'category': 'Agriculture',
                    'relevance_score': 1,
                    'matched_keywords': []
                })
        return JsonResponse({
            'success': True,
            'articles': unique_articles[:20],  # Show up to 20
            'total': len(unique_articles),
            'queries_searched': 1
        })
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return JsonResponse({'error': 'Network error occurred', 'articles': []})
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred', 'articles': []})

def fetch_category_news(request, category):
    try:
        NEWS_API_KEY = getattr(settings, 'NEWS_API_KEY', None)
        if not NEWS_API_KEY:
            return JsonResponse({'error': 'News API key not configured', 'articles': []})
        category_queries = {
            'crop-news': [
                'crop farming India',
                'wheat rice pulses India',
                'sugarcane cotton jute India',
                'harvest crop yield India',
                'kharif rabi crops India',
                'crop diseases India',
                'crop insurance India',
                'seed varieties India'
            ],
            'market-updates': [
                'agricultural markets India',
                'mandi prices India',
                'APMC market India',
                'agricultural exports India',
                'agricultural imports India',
                'commodity prices India',
                'agricultural trade India',
                'market rates India'
            ],
            'technology-agri': [
                'agricultural technology India',
                'agritech India',
                'precision farming India',
                'drone farming India',
                'AI agriculture India',
                'smart farming India',
                'digital agriculture India',
                'IoT farming India'
            ],
            'weather-climate': [
                'agriculture weather India',
                'monsoon agriculture India',
                'drought farming India',
                'climate change agriculture India',
                'weather forecast farming India',
                'rainfall agriculture India',
                'agricultural climate India'
            ],
            'government-policies': [
                'agricultural policy India',
                'PM Kisan India',
                'agricultural subsidies India',
                'MSP procurement India',
                'agricultural reforms India',
                'government farming India',
                'agricultural schemes India'
            ],
            'expert-insights': [
                'agricultural experts India',
                'farming advice India',
                'agricultural research India',
                'farming techniques India',
                'agricultural innovation India',
                'farming best practices India'
            ],
            'sustainable-farming': [
                'organic farming India',
                'sustainable agriculture India',
                'natural farming India',
                'eco-friendly farming India',
                'biodynamic farming India',
                'permaculture India'
            ]
        }
        search_queries = category_queries.get(category, [
            'agriculture farming India',
            'crop farming harvest India',
            'farmer agricultural India'
        ])
        all_articles = []
        for query in search_queries[:6]:
            try:
                url = "https://newsapi.org/v2/everything"
                params = {
                    'q': query,
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'pageSize': 30,  # Fetch more articles per query
                    'apiKey': NEWS_API_KEY,
                    'domains': 'timesofindia.indiatimes.com,indianexpress.com,thehindu.com,business-standard.com,livemint.com,financialexpress.com,deccanherald.com,tribuneindia.com,ndtv.com,hindustantimes.com,economic-times.indiatimes.com,zeenews.india.com,news18.com,cnbctv18.com',
                    'from': (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
                }
                response = requests.get(url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    all_articles.extend(data.get('articles', []))
                time.sleep(0.3)
            except Exception as e:
                logger.error(f"Error fetching news for query '{query}': {str(e)}")
                continue
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article.get('url') and article.get('url') not in seen_urls:
                seen_urls.add(article.get('url'))
                unique_articles.append(article)
        # Category-specific keywords
        category_keywords = {
            'crop-news': ['crop', 'harvest', 'yield', 'wheat', 'rice', 'pulses', 'sugarcane', 'cotton', 'seed', 'kharif', 'rabi'],
            'market-updates': ['market', 'price', 'mandi', 'apmc', 'export', 'import', 'trade', 'commodity', 'procurement'],
            'technology-agri': ['technology', 'agritech', 'digital', 'ai', 'drone', 'precision', 'smart', 'iot', 'innovation'],
            'weather-climate': ['weather', 'monsoon', 'climate', 'drought', 'rainfall', 'temperature', 'forecast'],
            'government-policies': ['policy', 'government', 'subsidy', 'msp', 'pm kisan', 'scheme', 'reform'],
            'expert-insights': ['expert', 'research', 'advice', 'technique', 'innovation', 'best practice'],
            'sustainable-farming': ['organic', 'sustainable', 'natural', 'eco-friendly', 'biodynamic', 'permaculture']
        }
        keywords = category_keywords.get(category, ['agriculture', 'farming'])
        filtered_articles = []
        general_articles = []
        for article in unique_articles:
            title = article.get('title', '').lower()
            description = article.get('description', '').lower()
            is_agri = any(keyword in title or keyword in description for keyword in keywords)
            clean_article = {
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'url': article.get('url', ''),
                'urlToImage': article.get('urlToImage', ''),
                'publishedAt': article.get('publishedAt', ''),
                'source': {
                    'name': article.get('source', {}).get('name', 'Unknown Source')
                },
                'category': category.replace('-', ' ').title(),
                'relevance_score': 1,
                'matched_keywords': []
            }
            if is_agri:
                filtered_articles.append(clean_article)
            else:
                general_articles.append(clean_article)
        # If fewer than 6, fill with general news
        if len(filtered_articles) < 6:
            filtered_articles += general_articles[:6-len(filtered_articles)]
        return JsonResponse({
            'success': True,
            'articles': filtered_articles[:20],
            'total': len(filtered_articles),
            'category': category,
            'queries_searched': len(search_queries[:6])
        })
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return JsonResponse({'error': 'Network error occurred', 'articles': []})
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred', 'articles': []})