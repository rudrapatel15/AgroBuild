from django.conf import settings
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
from datetime import datetime, timedelta
import logging
import requests
from django.views.decorators.csrf import csrf_exempt
import re
# from agrobuild.models import ChatMessage  # Commented out temporarily

# Try to import ChatMessage, but don't fail if it doesn't exist yet
# try:
#     from agrobuild.models import ChatMessage
#     CHAT_MESSAGE_AVAILABLE = True
# except ImportError:
#     CHAT_MESSAGE_AVAILABLE = False
#     ChatMessage = None

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
            del request.session['pending_user']
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
            return JsonResponse({'success': True, 'redirect_url': str(redirect('login').url)})
        else:
            # Incorrect OTP
            return JsonResponse({'success': False, 'message': 'Incorrect OTP. Please enter the correct OTP from your email.'}, status=400)
    else:
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
        pending_user['otp_timestamp'] = int(time.time())
        request.session['pending_user'] = pending_user
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

def chatbot_response(request):
    """
    Handle chatbot queries and return appropriate responses
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').lower().strip()
            
            # Agriculture knowledge base
            agriculture_qa = {
                # Plant care
                'watering': {
                    'keywords': ['water', 'watering', 'how often water', 'when to water', 'irrigation', 'moisture'],
                    'response': "Most plants need regular watering. Check soil moisture by inserting your finger 1-2 inches deep. Water when the top layer feels dry. Avoid overwatering as it can cause root rot. Indoor plants typically need water every 1-2 weeks, while outdoor plants may need more frequent watering depending on weather. Succulents need less water, while tropical plants need more humidity."
                },
                'fertilizer': {
                    'keywords': ['fertilizer', 'fertilizing', 'nutrients', 'plant food', 'npk', 'feeding'],
                    'response': "Fertilizers provide essential nutrients (NPK - Nitrogen, Phosphorus, Potassium) to plants. Use organic fertilizers for better soil health. Apply during growing season (spring/summer) and reduce in winter. Follow package instructions for proper dosage. Over-fertilizing can harm plants. Nitrogen promotes leaf growth, phosphorus helps roots and flowers, potassium improves overall health."
                },
                'sunlight': {
                    'keywords': ['sunlight', 'sun', 'light', 'shade', 'bright', 'dark', 'exposure'],
                    'response': "Different plants have different light requirements. Full sun plants need 6+ hours of direct sunlight. Partial sun/shade plants need 3-6 hours. Full shade plants thrive with minimal direct sunlight. Check plant tags or research specific plant needs. South-facing windows get the most light, north-facing get the least. Rotate plants regularly for even growth."
                },
                'soil': {
                    'keywords': ['soil', 'potting mix', 'dirt', 'ph', 'drainage', 'compost'],
                    'response': "Good soil is crucial for plant health. Use well-draining potting mix for containers. Garden soil should be rich in organic matter. Most plants prefer slightly acidic to neutral pH (6.0-7.0). Test your soil pH and amend as needed. Add compost to improve soil structure and fertility. Sandy soil drains quickly, clay soil retains water longer."
                },
                'pests': {
                    'keywords': ['pest', 'insect', 'bug', 'disease', 'aphid', 'spider mite', 'mealybug', 'scale'],
                    'response': "Common plant pests include aphids, spider mites, mealybugs, and scale insects. Use neem oil or insecticidal soap for organic control. Remove affected leaves and isolate infected plants. Regular inspection helps catch problems early. Ladybugs and lacewings are natural predators. Keep plants healthy to prevent pest infestations."
                },
                'seeds': {
                    'keywords': ['seed', 'germination', 'planting', 'sow', 'seedling', 'sprout'],
                    'response': "Plant seeds at the recommended depth (usually 2-3 times the seed diameter). Keep soil moist but not soggy. Most seeds germinate in 7-14 days. Start seeds indoors 6-8 weeks before last frost for vegetables. Some seeds need light to germinate, others need darkness. Use seed starting mix for better results."
                },
                'pruning': {
                    'keywords': ['prune', 'trim', 'cut', 'deadhead', 'trimming', 'maintenance'],
                    'response': "Pruning promotes healthy growth and removes dead/damaged parts. Use clean, sharp tools. Prune flowering plants after they bloom. Remove dead or crossing branches. Don't prune more than 1/3 of the plant at once. Prune in late winter or early spring for most plants. Deadheading encourages more flowers."
                },
                'indoor_plants': {
                    'keywords': ['indoor', 'houseplant', 'room', 'apartment', 'office'],
                    'response': "Popular indoor plants include pothos, snake plant, peace lily, and spider plant. They prefer bright, indirect light and moderate humidity. Water when top soil is dry. Use well-draining pots and potting mix. Group plants together to increase humidity. Clean leaves regularly to remove dust. Most indoor plants prefer temperatures between 60-75°F."
                },
                'vegetables': {
                    'keywords': ['vegetable', 'tomato', 'carrot', 'lettuce', 'garden', 'herbs'],
                    'response': "Start with easy vegetables like tomatoes, lettuce, herbs, and peppers. Plant in well-draining soil with plenty of organic matter. Most vegetables need 6+ hours of sunlight. Water regularly and fertilize as needed. Companion planting can help deter pests. Rotate crops each year to prevent soil-borne diseases. Harvest regularly to encourage more production."
                },
                'organic': {
                    'keywords': ['organic', 'natural', 'chemical free', 'pesticide', 'sustainable'],
                    'response': "Organic gardening avoids synthetic chemicals. Use compost, manure, and organic fertilizers. Control pests with neem oil, companion planting, and beneficial insects. Build healthy soil for natural pest resistance. Crop rotation and diversity help prevent problems. Organic methods may take longer but are better for the environment and your health."
                },
                'seasonal': {
                    'keywords': ['season', 'spring', 'summer', 'fall', 'winter', 'planting time', 'growing season'],
                    'response': "Spring: Plant cool-season crops (lettuce, spinach, peas) and start warm-season seeds indoors. Summer: Plant heat-loving vegetables (tomatoes, peppers, cucumbers) and maintain regular watering. Fall: Plant cool-season crops again and prepare garden for winter. Winter: Plan next season, maintain indoor plants, and protect outdoor plants from frost."
                },
                'composting': {
                    'keywords': ['compost', 'composting', 'organic matter', 'decompose'],
                    'response': "Composting turns kitchen scraps and yard waste into nutrient-rich soil amendment. Use a mix of green materials (nitrogen-rich) and brown materials (carbon-rich). Turn the pile regularly to speed decomposition. Keep it moist but not soggy. Finished compost should be dark, crumbly, and smell earthy. Use compost to improve soil fertility and structure."
                },
                'propagation': {
                    'keywords': ['propagate', 'cuttings', 'division', 'layering', 'multiply'],
                    'response': "Plant propagation creates new plants from existing ones. Stem cuttings work for many plants - cut below a node and root in water or soil. Division works for plants that form clumps. Layering involves rooting stems while still attached to the parent plant. Some plants can be grown from leaf cuttings. Use rooting hormone to improve success rates."
                },
                'weather_protection': {
                    'keywords': ['frost', 'cold', 'heat', 'wind', 'weather', 'protection'],
                    'response': "Protect plants from extreme weather. Use frost cloth or blankets for cold protection. Mulch helps regulate soil temperature. Wind can damage plants - use windbreaks or stakes. Provide shade for heat-sensitive plants during hot weather. Move potted plants indoors during extreme conditions. Water deeply before expected frost to help plants survive."
                },
                # Weather and Climate Information for India
                'weather_india': {
                    'keywords': ['weather india', 'weather in india', 'india weather', 'temperature india', 'climate india', 'weather forecast india'],
                    'response': "India has diverse weather patterns across regions. North India: Hot summers (40-45°C), cold winters (5-15°C), monsoon rains (July-September). South India: Tropical climate, hot and humid year-round (25-35°C), two monsoon seasons. Central India: Hot summers (35-45°C), moderate winters (15-25°C), monsoon rains. Northeast: Heavy rainfall, humid subtropical climate. Northwest: Hot desert climate, minimal rainfall. Check local weather forecasts for specific regions and plan farming activities accordingly."
                },
                'monsoon_india': {
                    'keywords': ['monsoon', 'monsoon india', 'rainy season', 'rainfall india', 'southwest monsoon', 'northeast monsoon'],
                    'response': "India has two monsoon seasons: Southwest Monsoon (June-September) brings 70-90% of annual rainfall, crucial for kharif crops like rice, cotton, sugarcane. Northeast Monsoon (October-December) affects Tamil Nadu, Kerala, Andhra Pradesh. Monsoon timing and intensity significantly impact agricultural productivity. Farmers plan crop cycles around monsoon patterns. Delayed or deficient monsoons can affect crop yields and require irrigation support."
                },
                'seasonal_weather': {
                    'keywords': ['summer india', 'winter india', 'spring india', 'autumn india', 'seasonal weather', 'hot season', 'cold season'],
                    'response': "India has four main seasons: Summer (March-May): Hot and dry, temperatures 30-45°C, ideal for summer crops. Monsoon (June-September): Heavy rainfall, humid, kharif crop season. Post-monsoon (October-November): Moderate temperatures, rabi crop preparation. Winter (December-February): Cool to cold, temperatures 5-25°C, rabi crop season. Each season requires different farming practices and crop selection."
                },
                'weather_crops': {
                    'keywords': ['weather crops', 'weather farming', 'weather agriculture', 'crop weather', 'farming weather'],
                    'response': "Weather significantly impacts crop growth. Kharif crops (June-October): Rice, maize, cotton, sugarcane need monsoon rains. Rabi crops (November-April): Wheat, barley, peas, mustard need cool weather. Zaid crops (March-June): Cucumber, watermelon, bitter gourd need hot weather. Monitor weather forecasts for: Frost protection in winter, irrigation during dry spells, pest control during humid conditions, harvest timing during dry weather."
                },
                'weather_regions': {
                    'keywords': ['north india weather', 'south india weather', 'central india weather', 'northeast weather', 'west india weather', 'east india weather'],
                    'response': "North India: Extreme temperatures, hot summers (40-45°C), cold winters (0-15°C), monsoon rains. South India: Tropical climate, consistent warmth (25-35°C), two monsoon seasons, high humidity. Central India: Hot summers (35-45°C), moderate winters (15-25°C), monsoon dependent. Northeast: Heavy rainfall, humid subtropical, mild winters. West India: Hot desert climate, minimal rainfall, coastal humidity. East India: Tropical monsoon, hot summers, moderate winters, heavy rainfall."
                },
                'weather_forecast': {
                    'keywords': ['weather forecast', 'weather prediction', 'weather outlook', 'weather report', 'weather update'],
                    'response': "For accurate weather forecasts in India, check: India Meteorological Department (IMD) website, local weather apps, agricultural weather services. Key factors for farming: Temperature trends, rainfall probability, humidity levels, wind speed, frost warnings. Plan farming activities based on 7-10 day forecasts. Monitor weather alerts for extreme events like cyclones, heavy rainfall, or heatwaves that can damage crops."
                },
                'extreme_weather': {
                    'keywords': ['extreme weather', 'heatwave', 'cold wave', 'drought', 'flood', 'cyclone', 'storm'],
                    'response': "Extreme weather events in India: Heatwaves (March-June): Protect crops with shade, increase irrigation, avoid midday work. Cold waves (December-February): Use frost protection, cover sensitive crops, delay planting. Drought: Implement water conservation, choose drought-resistant crops, use mulching. Floods: Improve drainage, raise beds, choose flood-tolerant varieties. Cyclones: Secure structures, harvest early, protect livestock. Monitor weather alerts and have contingency plans."
                },
                'weather_planning': {
                    'keywords': ['weather planning', 'farming weather', 'agricultural weather', 'weather farming', 'weather crops'],
                    'response': "Weather-based farming planning: Monitor seasonal forecasts before planting. Choose crops suitable for expected weather patterns. Plan irrigation based on rainfall predictions. Schedule harvests during dry weather windows. Prepare for extreme weather events with protective measures. Use weather data for pest and disease management. Adjust farming practices based on real-time weather updates. Keep emergency plans for weather-related crop damage."
                }
            }
            
            # Check for matches
            best_match = None
            highest_score = 0
            
            for category, qa_data in agriculture_qa.items():
                for keyword in qa_data['keywords']:
                    if keyword in user_message:
                        score = len(keyword)  # Simple scoring based on keyword length
                        if score > highest_score:
                            highest_score = score
                            best_match = qa_data['response']
            
            # If no specific match, provide general help
            if not best_match:
                general_responses = [
                    "I can help with plant care, watering, fertilizing, pest control, weather information, and general gardening questions. What specific topic would you like to know about?",
                    "For agriculture questions, I can assist with plant care, soil management, pest control, seasonal gardening, and weather patterns across India. Please ask a specific question!",
                    "I'm here to help with your agriculture and gardening questions. Try asking about watering, fertilizing, plant care, pest management, or weather conditions in India.",
                    "I can provide advice on plant care, soil health, pest control, seasonal gardening, weather forecasts, and more. What would you like to learn about?"
                ]
                import random
                best_match = random.choice(general_responses)
            
            return JsonResponse({
                'success': True,
                'response': best_match,
                'user_message': user_message
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'response': 'Sorry, I couldn\'t understand your message. Please try again.'
            })
        except Exception as e:
            logger.error(f"Chatbot error: {str(e)}")
            return JsonResponse({
                'success': False,
                'response': 'Sorry, something went wrong. Please try again.'
            })
    
    return JsonResponse({
        'success': False,
        'response': 'Please send a POST request with your question.'
    })

def get_chat_history(request):
    """
    Retrieve chat history for logged-in users
    """
    if request.method == 'GET' and request.user.is_authenticated:
        try:
            # For now, return empty history since ChatMessage model is not available
            return JsonResponse({
                'success': True,
                'messages': []
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Failed to retrieve chat history'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'User not authenticated'
    })

def chatbot_test_page(request):
    """
    Simple test page to verify chatbot functionality
    """
    return render(request, 'htmldemo.net/chatbot_test.html')

def clear_chat_history(request):
    """
    Clear chat history for logged-in users
    """
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            # For now, just return success since ChatMessage model is not available
            return JsonResponse({
                'success': True,
                'message': 'Chat history cleared successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Failed to clear chat history'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'User not authenticated'
    })
