from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.urls import path, include
from downloads import views as downloads_views
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, authenticate, login
from django.contrib.auth.forms import PasswordChangeForm
from .forums import UpdateEmailForm, ChangePasswordForm, DeleteAccountForm
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
def home(request):
    return render(request, 'downloads/home.html')

def downloads(request):
    return render(request, 'downloads/downloads.html')

@login_required
def forums(request):
    return render(request, 'forums/forums_home.html')


def create_account(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        email_confirm = request.POST.get('email_confirm')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        # Validate that emails match
        if email != email_confirm:
            messages.error(request, "Emails do not match.")
            return render(request, 'downloads/create_account.html', {
                'username': username,
                'email': email,
            })

        # Validate the email format
        email_validator = EmailValidator()
        try:
            email_validator(email)
        except ValidationError:
            messages.error(request, "Invalid email format.")
            return render(request, 'downloads/create_account.html', {
                'username': username,
                'email': email,
            })

        # Validate that passwords match
        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'downloads/create_account.html', {
                'username': username,
                'email': email,
            })

        # Validate the password
        try:
            validate_password(password)
        except ValidationError as e:
            for error in e:
                messages.error(request, error)
            return render(request, 'downloads/create_account.html', {
                'username': username,
                'email': email,
            })

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'downloads/create_account.html', {
                'username': username,
                'email': email,
            })

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, 'downloads/create_account.html', {
                'username': username,
                'email': email,
            })

        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')

    return render(request, 'downloads/create_account.html')

@login_required
def account_page(request):
    return render(request, 'downloads/account.html', {'user': request.user})

@login_required
def update_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        email_confirm = request.POST.get('email_confirm')

        # Validate that emails match
        if email != email_confirm:
            messages.error(request, "Emails do not match.")
            return render(request, 'downloads/update_email.html', {
                'email': email,
            })

        # Validate the email format
        email_validator = EmailValidator()
        try:
            email_validator(email)
        except ValidationError:
            messages.error(request, "Invalid email format.")
            return render(request, 'downloads/update_email.html', {
                'email': email,
            })

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, 'downloads/update_email.html', {
                'email': email,
            })

        # Update the email
        user = request.user
        user.email = email
        user.save()

        messages.success(request, "Email updated successfully!")
        return redirect('account')
    
    # Render form with initial data
    return render(request, 'downloads/update_email.html', {
        'email': request.user.email,
    })

@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important: Keeps the user logged in
            messages.success(request, "Password changed successfully!")
            return redirect('account')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ChangePasswordForm(request.user)
    return render(request, 'downloads/change_password.html', {'form': form})

@login_required
def delete_account(request):
    if request.method == 'POST':
        form = DeleteAccountForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            user = authenticate(username=request.user.username, password=password)
            if user:
                user.delete()
                messages.success(request, "Your account has been deleted.")
                return redirect('/')
            else:
                messages.error(request, "Incorrect password.")
    else:
        form = DeleteAccountForm()
    return render(request, 'downloads/delete_account.html', {'form': form})

import os
import zipfile
import tempfile
from django.conf import settings
from django.http import HttpResponse

def create_and_download_zip(request):
    # Define the directory to zip and the excluded directory
    jarvis_dir = settings.JARVIS_DIR  # Adjust path as needed
    exclude_dir = os.path.join(jarvis_dir, 'jarvis_website')
    
     # Content of setup.sh
    setup_script_content = """#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Setting up Jarvis environment..."

# Change to the Jarvis directory
echo "Changing to Jarvis directory..."
cd "Jarvis"

# Create a virtual environment
echo "Creating a virtual environment..."
python3 -m venv venv

# Activate the virtual environment
echo "Activating the virtual environment..."
source venv/bin/activate

# Install virtualenv inside the virtual environment
echo "Installing virtualenv..."
pip install --upgrade pip
pip install virtualenv

# Run the installer
echo "Running the installer..."
python3 installer

echo "Setup completed successfully!"
echo "Now call Jarvis by running jarvis or ./jarvis"
"""

    # Content of setup.txt
    setup_txt_content = """Welcome! You have successfully downloaded JarvisCLI.

Pre-reqs:
1. Python3
2. Unix system

Setting up this version:
1. Run chmod +x on the setup script in the bin directory:
    - chmod +x bin/setup.sh
2. Run the script:
    - ./bin/setup.sh
"""

    # Create a ZIP archive in memory
    zip_file_path = 'jarvis_CLI.zip'
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add jarvis directory contents
        for root, dirs, files in os.walk(jarvis_dir):
            # Skip the excluded directory
            if root.startswith(exclude_dir):
                continue
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.join('Jarvis', os.path.relpath(file_path, jarvis_dir))
                zipf.write(file_path, arcname)
        
        # Add the bin folder and setup.sh script at the root level
        bin_folder = 'bin'
        setup_script_path = os.path.join(bin_folder, 'setup.sh')
        
        # Add the folder structure
        zipf.writestr(os.path.join(bin_folder, ''), '')
        # Add the setup.sh file
        zipf.writestr(setup_script_path, setup_script_content)

        # Add setup.txt at the root level
        zipf.writestr('setup.txt', setup_txt_content)
    
    # Serve the file for download
    response = HttpResponse(open(zip_file_path, 'rb'), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{zip_file_path}"'
    
    # Optionally clean up the ZIP file after serving
    os.remove(zip_file_path)
    
    return response
