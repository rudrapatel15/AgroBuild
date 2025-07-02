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
from django.utils import timezone
from agrobuild.models import ChatMessage
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from datetime import datetime, timedelta
import logging
import requests
from agrobuild.models import ChatMessage

logger = logging.getLogger(__name__)

from agrobuild.models import ChatMessage

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
            # Clear expired OTP from session to prevent re-use
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

def chatbot_response(request):
    """
    Handle chatbot API requests and generate responses
    """
    print(f"Chatbot request received: {request.method}")
    print(f"Request headers: {request.headers}")
    
    if request.method == 'POST':
        try:
            print(f"Request body: {request.body}")
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            print(f"User message: {user_message}")
            
            if not user_message:
                return JsonResponse({'success': False, 'response': 'Please provide a message.'})
            
            # Generate bot response based on user message
            bot_response = generate_chatbot_response(user_message)
            print(f"Bot response: {bot_response}")
            
            # Save chat message if user is authenticated
            if request.user.is_authenticated:
                try:
                    ChatMessage.objects.create(
                        user=request.user,
                        message=user_message,
                        response=bot_response,
                        is_user_message=True
                    )
                    ChatMessage.objects.create(
                        user=request.user,
                        message=bot_response,
                        response=bot_response,
                        is_user_message=False
                    )
                    print("Chat messages saved successfully")
                except Exception as e:
                    print(f"Error saving chat messages: {e}")
            
            response_data = {
                'success': True,
                'response': bot_response
            }
            print(f"Returning response: {response_data}")
            return JsonResponse(response_data)
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return JsonResponse({'success': False, 'response': 'Invalid JSON data.'})
        except Exception as e:
            print(f"General error: {e}")
            return JsonResponse({'success': False, 'response': f'Error: {str(e)}'})
    
    print("Non-POST request received")
    return JsonResponse({'success': False, 'response': 'Only POST requests are allowed.'})

def generate_chatbot_response(user_message):
    """
    Generate appropriate responses for agriculture and weather-related queries
    """
    try:
        print(f"Processing message: '{user_message}'")
        message_lower = user_message.lower()
        print(f"Lowercase message: '{message_lower}'")
        
        # Weather queries (simplified)
        if 'weather' in message_lower:
            print("Matched weather query")
            return """Weather and Agriculture:

Weather's Impact on Farming:
• Temperature affects crop growth and development
• Rainfall determines irrigation needs
• Humidity influences disease pressure
• Wind can damage crops and affect pollination

Seasonal Weather Patterns:
• Spring: Moderate temperatures, good for planting
• Summer: Hot weather, increased watering needs
• Autumn: Cooling temperatures, harvest season
• Winter: Cold weather, protect sensitive crops

Weather Monitoring Tips:
• Check daily weather forecasts
• Monitor temperature extremes
• Watch for severe weather warnings
• Adjust farming activities accordingly

Weather-Based Farming Decisions:
• Plant timing based on weather predictions
• Irrigation scheduling
• Pest control timing
• Harvest planning

For specific weather information about India, ask me about "weather in India" or "monsoon patterns"."""
        
        # Farming queries
        elif any(word in message_lower for word in ['farming', 'farm', 'agriculture', 'agricultural']):
            print("Matched farming query")
            return """Farming and Agriculture in India:

Traditional Farming:
• Crop farming: Rice, wheat, pulses, oilseeds
• Dairy farming: Milk production and cattle rearing
• Poultry farming: Egg and meat production
• Horticulture: Fruits, vegetables, flowers

Modern Farming Techniques:
• Precision agriculture using GPS and sensors
• Hydroponics and vertical farming
• Organic farming methods
• Integrated pest management

Key Farming Seasons in India:
• Kharif (June-October): Rice, maize, cotton
• Rabi (October-March): Wheat, barley, mustard
• Zaid (March-June): Vegetables, fruits

Farming Challenges:
• Climate change impact
• Water scarcity
• Soil degradation
• Market price fluctuations

Government Support:
• Subsidies for seeds and fertilizers
• Crop insurance schemes
• Minimum support prices
• Agricultural extension services"""
        
        # Watering queries
        elif any(word in message_lower for word in ['water', 'watering', 'hydrate']):
            print("Matched watering query")
            return """Watering Guidelines for Plants:

Watering Frequency:
• Check soil moisture with your finger (top 1-2 inches)
• Water when soil feels dry to touch
• Avoid overwatering - it's better to underwater than overwater
• Most plants prefer deep, infrequent watering

Best Times to Water:
• Early morning (6-10 AM): Best time, allows water to soak in before heat
• Late afternoon (4-6 PM): Good alternative if you miss morning
• Avoid evening watering: Can promote fungal diseases
• Avoid midday: Water evaporates quickly in hot sun

Watering Tips:
• Water at the base of plants, not leaves
• Use room temperature water
• Ensure proper drainage to prevent root rot
• Adjust frequency based on season and plant type"""
        
        # Fertilizer queries
        elif any(word in message_lower for word in ['fertilizer', 'fertilize', 'nutrient', 'feed']):
            print("Matched fertilizer query")
            return """Fertilizing Guidelines for Healthy Plants:

Fertilizer Types:
• Use balanced fertilizer (10-10-10 or 20-20-20)
• Frequency: Every 2-4 weeks during growing season
• Amount: Follow package instructions - less is better than more
• Method: Apply to moist soil, avoid direct contact with stems

Organic Options:
• Compost: Excellent natural fertilizer
• Manure: Well-aged cow or chicken manure
• Fish emulsion: Good for leafy growth
• Bone meal: High in phosphorus for flowering

Signs of Over-fertilization:
• Brown leaf tips
• Wilting despite moist soil
• Salt buildup on soil surface"""
        
        # Pest control queries
        elif any(word in message_lower for word in ['pest', 'insect', 'bug', 'disease']):
            print("Matched pest control query")
            return """Pest Control and Disease Prevention:

Common Garden Pests:
• Aphids: Wash off with water, use neem oil
• Spider mites: Increase humidity, use insecticidal soap
• Whiteflies: Yellow sticky traps, neem oil
• Mealybugs: Remove with cotton swab dipped in alcohol
• Scale: Scrape off, treat with horticultural oil

Natural Pest Control:
• Neem oil: Effective against many pests, safe for plants
• Soap solution: Mix 1 tsp dish soap with 1 liter water
• Garlic spray: Blend garlic with water, strain and spray
• Companion planting: Marigolds repel many insects
• Beneficial insects: Ladybugs eat aphids

Disease Prevention:
• Avoid overhead watering
• Ensure good air circulation
• Remove dead leaves and debris
• Use disease-resistant varieties
• Keep plants healthy - pests target weak plants"""
        
        # Plant care queries
        elif any(word in message_lower for word in ['care', 'maintain', 'grow', 'plant']):
            print("Matched plant care query")
            return """General Plant Care Tips:

Basic Requirements:
• Light: Most plants need 6-8 hours of sunlight
• Water: Check soil moisture regularly
• Soil: Use well-draining, nutrient-rich soil
• Temperature: Most plants prefer 15-30°C
• Humidity: Tropical plants need higher humidity

Seasonal Care:
• Spring: Start fertilizing, repot if needed
• Summer: Increase watering, provide shade
• Autumn: Reduce watering, prepare for winter
• Winter: Reduce watering, protect from cold"""
        
        # Default response
        else:
            print("No specific query matched, returning default response")
            return """I'm AgriBot, your agriculture assistant! I can help you with:
• Plant care and watering schedules
• Fertilizing and soil management
• Pest control and disease prevention
• Weather information and farming tips
• Seasonal gardening advice
• Farming techniques and agricultural practices

Please ask me about any of these topics or any other agriculture-related questions!"""
    
    except Exception as e:
        print(f"Error in generate_chatbot_response: {e}")
        import traceback
        traceback.print_exc()
        return "I'm sorry, I encountered an error processing your request. Please try asking your question again."

def get_chat_history(request):
    """
    Retrieve chat history for authenticated users
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required'})
    
    try:
        messages = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
        chat_data = []
        
        for msg in messages:
            chat_data.append({
                'message': msg.message,
                'response': msg.response,
                'is_user_message': msg.is_user_message,
                'timestamp': msg.timestamp.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'messages': chat_data
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

def clear_chat_history(request):
    """
    Clear chat history for authenticated users
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required'})
    
    if request.method == 'POST':
        try:
            ChatMessage.objects.filter(user=request.user).delete()
            return JsonResponse({'success': True, 'message': 'Chat history cleared successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Only POST requests allowed'})

def agriculture_news_page(request):
    """
    Render the agriculture news page
    """
    context = {
        'title': 'Agriculture News - AgroBuild',
        'current_date': timezone.now().strftime('%B %d, %Y')
    }
    return render(request, 'htmldemo.net/news.html', context)

def fetch_agriculture_news(request):
    """
    Fetch agriculture news from external API or generate mock data
    """
    try:
        # Mock agriculture news data for demonstration
        mock_news = [
            {
                'title': 'New Agricultural Technology Boosts Crop Yields by 30%',
                'description': 'Innovative farming techniques and smart irrigation systems are revolutionizing agriculture in India.',
                'url': '#',
                'urlToImage': '/static/img/blog/blog-big1.jpg',
                'publishedAt': timezone.now().isoformat(),
                'source': {'name': 'AgroBuild News'},
                'category': 'Agricultural Technology',
                'relevance_score': 9,
                'matched_keywords': ['technology', 'crop yields', 'farming']
            },
            {
                'title': 'Government Announces New Subsidies for Small Farmers',
                'description': 'The government has introduced new subsidy schemes to support small and marginal farmers across the country.',
                'url': '#',
                'urlToImage': '/static/img/blog/blog-big2.jpg',
                'publishedAt': (timezone.now() - timezone.timedelta(hours=2)).isoformat(),
                'source': {'name': 'Agricultural Policy'},
                'category': 'Agricultural Policy',
                'relevance_score': 8,
                'matched_keywords': ['government', 'subsidies', 'farmers']
            },
            {
                'title': 'Weather Forecast: Favorable Conditions for Rabi Crops',
                'description': 'Meteorological department predicts ideal weather conditions for wheat and other rabi crops this season.',
                'url': '#',
                'urlToImage': '/static/img/blog/blog-big3.jpg',
                'publishedAt': (timezone.now() - timezone.timedelta(hours=4)).isoformat(),
                'source': {'name': 'Weather Updates'},
                'category': 'Weather & Climate',
                'relevance_score': 7,
                'matched_keywords': ['weather', 'rabi crops', 'wheat']
            },
            {
                'title': 'Organic Farming Gains Popularity Among Urban Consumers',
                'description': 'Growing health consciousness is driving demand for organic produce, creating new opportunities for farmers.',
                'url': '#',
                'urlToImage': '/static/img/product/BACF.webp',
                'publishedAt': (timezone.now() - timezone.timedelta(hours=6)).isoformat(),
                'source': {'name': 'Market Trends'},
                'category': 'Agricultural Markets',
                'relevance_score': 6,
                'matched_keywords': ['organic', 'farming', 'consumers']
            },
            {
                'title': 'Sustainable Farming Practices Reduce Environmental Impact',
                'description': 'Farmers adopting eco-friendly practices are seeing both environmental and economic benefits.',
                'url': '#',
                'urlToImage': '/static/img/service/services1.jpg',
                'publishedAt': (timezone.now() - timezone.timedelta(hours=8)).isoformat(),
                'source': {'name': 'Sustainability News'},
                'category': 'Sustainable Farming',
                'relevance_score': 8,
                'matched_keywords': ['sustainable', 'farming', 'environmental']
            },
            {
                'title': 'New Crop Varieties Resistant to Climate Change',
                'description': 'Agricultural research institutes are developing crop varieties that can withstand extreme weather conditions.',
                'url': '#',
                'urlToImage': '/static/img/service/services2.jpg',
                'publishedAt': (timezone.now() - timezone.timedelta(hours=10)).isoformat(),
                'source': {'name': 'Research Updates'},
                'category': 'Agricultural Technology',
                'relevance_score': 9,
                'matched_keywords': ['crop varieties', 'climate change', 'research']
            }
        ]
        
        return JsonResponse({
            'success': True,
            'articles': mock_news,
            'total': len(mock_news),
            'queries_searched': 10
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Failed to fetch news: {str(e)}'
        })

def fetch_category_news(request, category):
    """
    Fetch category-specific agriculture news
    """
    try:
        # Mock category-specific news data
        category_news = {
            'crop-news': [
                {
                    'title': 'Rice Production Expected to Increase This Season',
                    'description': 'Favorable monsoon conditions are expected to boost rice production across major growing regions.',
                    'url': '#',
                    'urlToImage': '/static/img/product/beetrootseeds.webp',
                    'publishedAt': timezone.now().isoformat(),
                    'source': {'name': 'Crop News'},
                    'category': 'Crop News',
                    'relevance_score': 8,
                    'matched_keywords': ['rice', 'production', 'monsoon']
                }
            ],
            'market-updates': [
                {
                    'title': 'Agricultural Commodity Prices Show Upward Trend',
                    'description': 'Prices of major agricultural commodities have shown positive movement in recent weeks.',
                    'url': '#',
                    'urlToImage': '/static/img/product/bottlegourdseeds.webp',
                    'publishedAt': timezone.now().isoformat(),
                    'source': {'name': 'Market Updates'},
                    'category': 'Market Updates',
                    'relevance_score': 7,
                    'matched_keywords': ['prices', 'commodities', 'market']
                }
            ],
            'technology-agri': [
                {
                    'title': 'AI-Powered Drones Revolutionize Crop Monitoring',
                    'description': 'Advanced drone technology is helping farmers monitor crop health and optimize irrigation.',
                    'url': '#',
                    'urlToImage': '/static/img/s-product/Drip_Irrigation_kit.jpg',
                    'publishedAt': timezone.now().isoformat(),
                    'source': {'name': 'Tech News'},
                    'category': 'Agricultural Technology',
                    'relevance_score': 9,
                    'matched_keywords': ['AI', 'drones', 'monitoring']
                }
            ],
            'weather-climate': [
                {
                    'title': 'El Niño Effect on Indian Agriculture',
                    'description': 'Meteorologists predict El Niño conditions that may affect rainfall patterns and crop production.',
                    'url': '#',
                    'urlToImage': '/static/img/service/services3.jpg',
                    'publishedAt': timezone.now().isoformat(),
                    'source': {'name': 'Weather News'},
                    'category': 'Weather & Climate',
                    'relevance_score': 8,
                    'matched_keywords': ['El Niño', 'rainfall', 'crops']
                }
            ],
            'government-policies': [
                {
                    'title': 'New Agricultural Policy Focuses on Digital Farming',
                    'description': 'The government has announced a comprehensive policy to promote digital agriculture and smart farming.',
                    'url': '#',
                    'urlToImage': '/static/img/about/About_icon1.png',
                    'publishedAt': timezone.now().isoformat(),
                    'source': {'name': 'Policy News'},
                    'category': 'Government Policies',
                    'relevance_score': 9,
                    'matched_keywords': ['policy', 'digital', 'farming']
                }
            ],
            'expert-insights': [
                {
                    'title': 'Expert Tips for Monsoon Season Farming',
                    'description': 'Agricultural experts share valuable insights on preparing for and managing monsoon season farming.',
                    'url': '#',
                    'urlToImage': '/static/img/about/About_icon2.png',
                    'publishedAt': timezone.now().isoformat(),
                    'source': {'name': 'Expert Insights'},
                    'category': 'Expert Insights',
                    'relevance_score': 8,
                    'matched_keywords': ['expert', 'monsoon', 'farming']
                }
            ],
            'sustainable-farming': [
                {
                    'title': 'Zero-Budget Natural Farming Gains Traction',
                    'description': 'More farmers are adopting zero-budget natural farming methods to reduce costs and improve sustainability.',
                    'url': '#',
                    'urlToImage': '/static/img/about/About_icon3.png',
                    'publishedAt': timezone.now().isoformat(),
                    'source': {'name': 'Sustainability News'},
                    'category': 'Sustainable Farming',
                    'relevance_score': 8,
                    'matched_keywords': ['zero-budget', 'natural', 'farming']
                }
            ]
        }
        
        articles = category_news.get(category, [])
        
        return JsonResponse({
            'success': True,
            'articles': articles,
            'total': len(articles),
            'queries_searched': 5
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Failed to fetch category news: {str(e)}'
        })
        logger.error(f"Unexpected error: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred', 'articles': []})
    
def chatbot_response(request):
    """
    Handle chatbot API requests and generate responses
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            if not user_message:
                return JsonResponse({'success': False, 'response': 'Please provide a message.'})
            
            # Generate bot response based on user message
            bot_response = generate_chatbot_response(user_message)
            
            # Save chat message if user is authenticated
            if request.user.is_authenticated:
                ChatMessage.objects.create(
                    user=request.user,
                    message=user_message,
                    response=bot_response,
                    is_user_message=True
                )
                ChatMessage.objects.create(
                    user=request.user,
                    message=bot_response,
                    response=bot_response,
                    is_user_message=False
                )
            
            return JsonResponse({
                'success': True,
                'response': bot_response
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'response': 'Invalid JSON data.'})
        except Exception as e:
            return JsonResponse({'success': False, 'response': f'Error: {str(e)}'})
    
    return JsonResponse({'success': False, 'response': 'Only POST requests are allowed.'})

def generate_chatbot_response(user_message):
    """
    Generate appropriate responses for agriculture and weather-related queries
    """
    try:
        message_lower = user_message.lower()
        
        # Farming related queries
        if any(word in message_lower for word in ['farming', 'farm', 'agriculture', 'agricultural']):
            return """Farming and Agriculture in India:

Traditional Farming:
• Crop farming: Rice, wheat, pulses, oilseeds
• Dairy farming: Milk production and cattle rearing
• Poultry farming: Egg and meat production
• Horticulture: Fruits, vegetables, flowers

Modern Farming Techniques:
• Precision agriculture using GPS and sensors
• Hydroponics and vertical farming
• Organic farming methods
• Integrated pest management

Key Farming Seasons in India:
• Kharif (June-October): Rice, maize, cotton
• Rabi (October-March): Wheat, barley, mustard
• Zaid (March-June): Vegetables, fruits

Farming Challenges:
• Climate change impact
• Water scarcity
• Soil degradation
• Market price fluctuations

Government Support:
• Subsidies for seeds and fertilizers
• Crop insurance schemes
• Minimum support prices
• Agricultural extension services"""
        
        # Watering related queries
        elif any(word in message_lower for word in ['water', 'watering', 'hydrate']):
            if 'how often' in message_lower or 'frequency' in message_lower:
                return """Watering frequency depends on several factors:
• Plant type: Succulents need less water, tropical plants need more
• Season: More frequent in summer, less in winter
• Soil type: Sandy soil dries faster than clay
• Container size: Smaller pots dry out faster

General guidelines:
• Check soil moisture with your finger (top 1-2 inches)
• Water when soil feels dry to touch
• Avoid overwatering - it's better to underwater than overwater
• Most plants prefer deep, infrequent watering over shallow, frequent watering"""
            
            elif 'when' in message_lower:
                return """Best times to water plants:
• Early morning (6-10 AM): Best time, allows water to soak in before heat
• Late afternoon (4-6 PM): Good alternative if you miss morning
• Avoid evening watering: Can promote fungal diseases
• Avoid midday: Water evaporates quickly in hot sun

Tips:
• Water at the base of plants, not leaves
• Use room temperature water
• Ensure proper drainage to prevent root rot"""
        
        # Fertilizer related queries
        elif any(word in message_lower for word in ['fertilizer', 'fertilize', 'nutrient', 'feed']):
            return """Fertilizing guidelines for healthy plants:
• Type: Use balanced fertilizer (10-10-10 or 20-20-20)
• Frequency: Every 2-4 weeks during growing season (spring/summer)
• Amount: Follow package instructions - less is better than more
• Method: Apply to moist soil, avoid direct contact with stems

Organic options:
• Compost: Excellent natural fertilizer
• Manure: Well-aged cow or chicken manure
• Fish emulsion: Good for leafy growth
• Bone meal: High in phosphorus for flowering

Signs of over-fertilization:
• Brown leaf tips
• Wilting despite moist soil
• Salt buildup on soil surface"""
        
        # Pest control queries
        elif any(word in message_lower for word in ['pest', 'insect', 'bug', 'disease']):
            if 'natural' in message_lower or 'organic' in message_lower:
                return """Natural pest control methods:
• Neem oil: Effective against many pests, safe for plants
• Soap solution: Mix 1 tsp dish soap with 1 liter water
• Garlic spray: Blend garlic with water, strain and spray
• Companion planting: Marigolds repel many insects
• Beneficial insects: Ladybugs eat aphids

Prevention tips:
• Keep plants healthy - pests target weak plants
• Regular inspection of leaves and stems
• Proper spacing for good air circulation
• Clean garden tools regularly
• Remove infected plant parts immediately"""
            else:
                return """Common garden pests and solutions:
• Aphids: Wash off with water, use neem oil
• Spider mites: Increase humidity, use insecticidal soap
• Whiteflies: Yellow sticky traps, neem oil
• Mealybugs: Remove with cotton swab dipped in alcohol
• Scale: Scrape off, treat with horticultural oil

Disease prevention:
• Avoid overhead watering
• Ensure good air circulation
• Remove dead leaves and debris
• Use disease-resistant varieties"""
        
        # Weather related queries
        elif any(word in message_lower for word in ['weather', 'climate', 'temperature']):
            if 'weather' in message_lower:
                return """Weather patterns in India:
• Monsoon (June-September): Heavy rainfall, high humidity
• Winter (December-February): Cool to cold, dry
• Summer (March-May): Hot, dry
• Post-monsoon (October-November): Moderate temperatures

Farming considerations:
• Monsoon: Best for rice, pulses, vegetables
• Winter: Wheat, mustard, peas
• Summer: Millets, cotton, groundnut
• Plan irrigation based on seasonal patterns"""
            
            elif 'forecast' in message_lower:
                return """Weather forecasting for farming:
• Check local weather reports daily
• Monitor temperature trends
• Watch for extreme weather warnings
• Plan activities around weather conditions

Weather-based farming tips:
• Plant before expected rains
• Protect crops from frost in winter
• Provide shade during heat waves
• Adjust irrigation based on rainfall"""
            
            elif 'monsoon' in message_lower:
                return """Monsoon in India:
• Duration: June to September
• Characteristics: Heavy rainfall, high humidity
• Impact on farming: Critical for agriculture

Monsoon farming tips:
• Prepare soil before monsoon
• Plant crops that thrive in wet conditions
• Ensure proper drainage
• Protect crops from waterlogging
• Monitor for fungal diseases"""
        
        # General plant care
        elif any(word in message_lower for word in ['care', 'maintain', 'grow', 'plant']):
            return """General plant care tips:
• Light: Most plants need 6-8 hours of sunlight
• Water: Check soil moisture regularly
• Soil: Use well-draining, nutrient-rich soil
• Temperature: Most plants prefer 15-30°C
• Humidity: Tropical plants need higher humidity

Seasonal care:
• Spring: Start fertilizing, repot if needed
• Summer: Increase watering, provide shade
• Autumn: Reduce watering, prepare for winter
• Winter: Reduce watering, protect from cold"""
        
        # Indoor vs outdoor plants
        elif any(word in message_lower for word in ['indoor', 'outdoor', 'houseplant']):
            return """Indoor vs Outdoor Plant Care:

Indoor Plants:
• Lower light requirements
• Consistent temperature
• Less watering needed
• Watch for pests (spider mites, mealybugs)
• Good air circulation important

Outdoor Plants:
• Full or partial sunlight
• Temperature fluctuations
• More watering needed
• Natural pest control
• Seasonal care required"""
        
        # Default response
        else:
            return """I'm AgriBot, your agriculture assistant! I can help you with:
• Plant care and watering schedules
• Fertilizing and soil management
• Pest control and disease prevention
• Weather information and farming tips
• Seasonal gardening advice
• Farming techniques and agricultural practices

Please ask me about any of these topics or any other agriculture-related questions!"""

    
    except Exception as e:
        print(f"Error in generate_chatbot_response: {e}")
        return "I'm sorry, I encountered an error processing your request. Please try asking your question again."

def get_chat_history(request):
    """
    Retrieve chat history for authenticated users
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required'})
    
    try:
        messages = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
        chat_data = []
        
        for msg in messages:
            chat_data.append({
                'message': msg.message,
                'response': msg.response,
                'is_user_message': msg.is_user_message,
                'timestamp': msg.timestamp.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'messages': chat_data
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

def clear_chat_history(request):
    """
    Clear chat history for authenticated users
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required'})
    
    if request.method == 'POST':
        try:
            ChatMessage.objects.filter(user=request.user).delete()
            return JsonResponse({'success': True, 'message': 'Chat history cleared successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Only POST requests allowed'})

def chatbot_test_page(request):
    """
    Render the chatbot test page
    """
    return render(request, 'htmldemo.net/chatbot_test.html')

def test_chatbot(request):
    return render(request, 'htmldemo.net/chatbot_test.html')

def debug_weather(request):
    from django.http import HttpResponse
    return HttpResponse("Debug weather endpoint is under construction.")
