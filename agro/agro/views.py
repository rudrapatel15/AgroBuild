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
    message_lower = user_message.lower()
    
    # Watering related queries
    if any(word in message_lower for word in ['water', 'watering', 'hydrate']):
        if 'how often' in message_lower or 'frequency' in message_lower:
            return """Watering frequency depends on several factors:
* Plant type: Succulents need less water, tropical plants need more
* Season: More frequent in summer, less in winter
* Soil type: Sandy soil dries faster than clay
* Container size: Smaller pots dry out faster

General guidelines:
* Check soil moisture with your finger (top 1-2 inches)
* Water when soil feels dry to touch
* Avoid overwatering - it's better to underwater than overwater
* Most plants prefer deep, infrequent watering over shallow, frequent watering"""
        
        elif 'when' in message_lower:
            return """Best times to water plants:
* Early morning (6-10 AM): Best time, allows water to soak in before heat
* Late afternoon (4-6 PM): Good alternative if you miss morning
* Avoid evening watering: Can promote fungal diseases
* Avoid midday: Water evaporates quickly in hot sun

Tips:
* Water at the base of plants, not leaves
* Use room temperature water
* Ensure proper drainage to prevent root rot"""
    
    # Fertilizer related queries
    elif any(word in message_lower for word in ['fertilizer', 'fertilize', 'nutrient', 'feed']):
        return """Fertilizing guidelines for healthy plants:
* Type: Use balanced fertilizer (10-10-10 or 20-20-20)
* Frequency: Every 2-4 weeks during growing season (spring/summer)
* Amount: Follow package instructions - less is better than more
* Method: Apply to moist soil, avoid direct contact with stems

Organic options:
* Compost: Excellent natural fertilizer
* Manure: Well-aged cow or chicken manure
* Fish emulsion: Good for leafy growth
* Bone meal: High in phosphorus for flowering

Signs of over-fertilization:
* Brown leaf tips
* Wilting despite moist soil
* Salt buildup on soil surface"""
    
    # Pest control queries
    elif any(word in message_lower for word in ['pest', 'insect', 'bug', 'disease']):
        if 'natural' in message_lower or 'organic' in message_lower:
            return """Natural pest control methods:
* Neem oil: Effective against many pests, safe for plants
* Soap solution: Mix 1 tsp dish soap with 1 liter water
* Garlic spray: Blend garlic with water, strain and spray
* Companion planting: Marigolds repel many insects
* Beneficial insects: Ladybugs eat aphids

Prevention tips:
* Keep plants healthy - pests target weak plants
* Regular inspection of leaves and stems
* Proper spacing for good air circulation
* Clean garden tools regularly
* Remove infected plant parts immediately"""
        else:
            return """Common garden pests and solutions:
* Aphids: Wash off with water, use neem oil
* Spider mites: Increase humidity, use insecticidal soap
* Whiteflies: Yellow sticky traps, neem oil
* Mealybugs: Remove with cotton swab dipped in alcohol
* Scale: Scrape off, treat with horticultural oil

Disease prevention:
* Avoid overhead watering
* Ensure good air circulation
* Remove dead leaves and debris
* Use disease-resistant varieties"""
    
    # Weather related queries
    elif any(word in message_lower for word in ['weather', 'climate', 'temperature']):
        if 'weather' in message_lower:
            return """Weather patterns in India:
* Monsoon (June-September): Heavy rainfall, high humidity
* Winter (December-February): Cool to cold, dry
* Summer (March-May): Hot, dry
* Post-monsoon (October-November): Moderate temperatures

Farming considerations:
* Monsoon: Best for rice, pulses, vegetables
* Winter: Wheat, mustard, peas
* Summer: Millets, cotton, groundnut
* Plan irrigation based on seasonal patterns"""
        
        elif 'forecast' in message_lower:
            return """Weather forecasting for farming:
* Check local weather reports daily
* Monitor temperature trends
* Watch for extreme weather warnings
* Plan activities around weather conditions

Weather-based farming tips:
* Plant before expected rains
* Protect crops from frost in winter
* Provide shade during heat waves
* Adjust irrigation based on rainfall"""
        
        elif 'monsoon' in message_lower:
            return """Monsoon in India:
* Duration: June to September
* Characteristics: Heavy rainfall, high humidity
* Impact on farming: Critical for agriculture

Monsoon farming tips:
* Prepare soil before monsoon
* Plant crops that thrive in wet conditions
* Ensure proper drainage
* Protect crops from waterlogging
* Monitor for fungal diseases"""
    
    # General plant care
    elif any(word in message_lower for word in ['care', 'maintain', 'grow', 'plant']):
        return """General plant care tips:
* Light: Most plants need 6-8 hours of sunlight
* Water: Check soil moisture regularly
* Soil: Use well-draining, nutrient-rich soil
* Temperature: Most plants prefer 15-30°C
* Humidity: Tropical plants need higher humidity

Seasonal care:
* Spring: Start fertilizing, repot if needed
* Summer: Increase watering, provide shade
* Autumn: Reduce watering, prepare for winter
* Winter: Reduce watering, protect from cold
    Please ask me about any of these topics or any other agriculture-related questions!"""

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

def chatbot_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '').lower()

        if "weather" in user_message or "extreme weather" in user_message or "crop" in user_message:
            response = "Here's some information about weather and crops..."
            return JsonResponse({'success': True, 'response': response})
        # ... other logic ...
        else:
            return JsonResponse({'success': False})