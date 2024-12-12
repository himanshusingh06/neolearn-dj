from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.mail import EmailMessage 
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password



from .models import UserDefinedCourse
import requests
import google.generativeai as gemini

def home(request):
    user = request.user if request.user.is_authenticated else None
    return render(request, 'landing.html', {'user': user})

def send_mail_to_admin(user_name, user_email, mobile_number, subject, enquiry, user_message):
    # Update the message body to include the enquiry field
    message_body = (
        f"Form filled by {user_name}--- with the email {user_email}.\n\n"
        f"Mobile number -- {mobile_number}\n\n"
        f"Selected Enquiry: {enquiry}\n\n"
        f"The Message provided is:\n{user_message}"
    )

    # Create and send the email
    message = EmailMessage(
        subject=f"New form filled by {user_name}--- with subject {subject}",
        body=message_body,
        from_email=settings.EMAIL_HOST_USER,
        to=['himanshusinghwork365@gmail.com']
    )
    message.send()


def contact(request):
    if request.method == 'POST':
        user_name = request.POST.get('name')
        user_email = request.POST.get('email')
        mobile_number = request.POST.get('mobile_number')
        subject = request.POST.get('subject')
        enquiry =request.POST.get('enquiry')
        user_message = request.POST.get('message')
        
        
        send_mail_to_admin(user_name, user_email, mobile_number, subject, enquiry, user_message)
        return redirect('home')
    else:
        return render(request, 'contact.html')



# Register view
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

def register(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('f_name')
        last_name = request.POST.get('l_name')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        # Check if username or email already exists
        if User.objects.filter(username=uname).exists():
            messages.error(request, "Username already exists!")
            return redirect('register')
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('register')
        elif pass1 != pass2:
            messages.error(request, "Your password and confirm password are not the same!")
            return redirect('register')

        # Validate password strength
        try:
            validate_password(pass1)  # This will raise a ValidationError if the password is weak
        except ValidationError as e:
            # Add error messages for weak password
            for error in e:
                messages.error(request, error)
            return redirect('register')

        # Create new user
        my_user = User(username=uname, email=email, first_name=first_name, last_name=last_name)
        my_user.set_password(pass1)  # Use set_password() to properly hash the password
        my_user.save()
        messages.success(request, "Your account has been created successfully!")
        return redirect('login')
    else:
        return render(request, 'signup.html')

        

# Login view
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('pass')
        # Authenticate user
        user = authenticate(request, username=username, password=password)

        # Check if user exists
        if user is None:
            messages.error(request, "Invalid UserName or Password.")
        else:
            # User exists, check password
            if user.check_password(password):
                # Password is correct, log in user
                auth.login(request, user)
                return redirect('home')
            else:
                # Incorrect password
                messages.error(request, "Invalid UserName or Password.")


    return render(request, 'login.html')

# Logout view
def logout(request):
    auth.logout(request)
    return redirect('home')



# Set up the Gemini API key
gemini.configure(api_key='AIzaSyDkS1WQkQaqgUOA-NoY2YbRbEX4c16_Ads')

# Create the model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize the generative model
model = gemini.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction=(
        "You are a personalized learning assistant. Provide users with comprehensive study materials, "
        "documentation, and video lectures to help them learn and improve their skills."
    ),
)

@login_required(login_url='login')
def profile_view(request):
    courses = UserDefinedCourse.objects.filter(user=request.user)

    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        details = request.POST.get('details')

        # Use Gemini API to get resources
        resources = "No resources available yet."
        try:
            # Start a new chat session for this request
            chat_session = model.start_chat(history=[])
            response = chat_session.send_message(
                f"Provide detailed resources, study materials, and video lectures for the course '{course_name}' "
                f"with the following details: {details}."
            )
            resources = response.text
        except Exception as e:
            resources = f"Error fetching resources: {str(e)}"

        # Save the new course
        UserDefinedCourse.objects.create(
            user=request.user,
            course_name=course_name,
            details=details,
            resources=resources
        )
        return redirect('profile')

    return render(request, 'profile.html', {'courses': courses})

@login_required(login_url='login')
def course_detail_view(request, course_id):
    course = get_object_or_404(UserDefinedCourse, id=course_id, user=request.user)
    return render(request, 'course_detail.html', {'course': course, 'user': request.user})
