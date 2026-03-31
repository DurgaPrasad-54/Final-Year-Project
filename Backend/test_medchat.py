#!/usr/bin/env python3
"""
Test script for MedChat authentication and medical QA
Run this AFTER starting the backend server: python start_server.py
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "test_medchat_2026@gmail.com"
TEST_PASSWORD = "TestPass123!"
TEST_NAME = "MedChat Tester"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_status(message, status="info"):
    """Print colored status messages"""
    if status == "success":
        print(f"{GREEN}✓ {message}{RESET}")
    elif status == "error":
        print(f"{RED}✗ {message}{RESET}")
    elif status == "warning":
        print(f"{YELLOW}⚠ {message}{RESET}")
    else:
        print(f"{BLUE}ℹ {message}{RESET}")

def test_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_status("Backend is running", "success")
            return True
    except Exception as e:
        print_status(f"Backend is NOT running: {e}", "error")
        return False

def test_register():
    """Test user registration"""
    print(f"\n{BLUE}=== Testing Registration ==={RESET}")
    
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": TEST_NAME
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=payload, timeout=10)
        
        if response.status_code == 201:
            data = response.json()
            print_status(f"Registration successful - User ID: {data.get('userId')}", "success")
            return True
        elif response.status_code == 409:
            print_status("User already exists (that's OK for testing)", "warning")
            return True
        else:
            print_status(f"Registration failed: {response.text}", "error")
            return False
            
    except Exception as e:
        print_status(f"Registration request failed: {e}", "error")
        return False

def test_login():
    """Test user login"""
    print(f"\n{BLUE}=== Testing Login ==={RESET}")
    
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            user_id = data.get('userId')
            print_status(f"Login successful! User ID: {user_id}", "success")
            print_status(f"Token received: {token[:20]}...", "info")
            return token, user_id
        else:
            print_status(f"Login failed with status {response.status_code}", "error")
            print_status(f"Response: {response.text}", "error")
            return None, None
            
    except Exception as e:
        print_status(f"Login request failed: {e}", "error")
        return None, None

def test_create_chat(token):
    """Test creating a new chat"""
    print(f"\n{BLUE}=== Testing Chat Creation ==={RESET}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat/new", headers=headers, timeout=10)
        
        if response.status_code == 201:
            data = response.json()
            chat_id = data.get('chatId')
            print_status(f"Chat created successfully! Chat ID: {chat_id}", "success")
            return chat_id
        else:
            print_status(f"Chat creation failed: {response.text}", "error")
            return None
            
    except Exception as e:
        print_status(f"Chat creation request failed: {e}", "error")
        return None

def test_medical_question(token, chat_id):
    """Test asking a medical question"""
    print(f"\n{BLUE}=== Testing Medical Question ==={RESET}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    question = "What are the symptoms of diabetes?"
    
    payload = {
        "question": question,
        "chatId": chat_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat/ask", json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('answer', '')
            context_used = data.get('contextUsed', False)
            
            print_status(f"Question answered successfully!", "success")
            print_status(f"RAG Context used: {context_used}", "info")
            print(f"\nQuestion: {question}")
            print(f"\nAnswer preview:")
            print(f"{answer[:200]}..." if len(answer) > 200 else answer)
            return True
        else:
            print_status(f"Question failed: {response.text}", "error")
            return False
            
    except Exception as e:
        print_status(f"Question request failed: {e}", "error")
        return False

def test_greeting(token, chat_id):
    """Test greeting/non-medical question"""
    print(f"\n{BLUE}=== Testing Greeting ==={RESET}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    question = "Hello, how are you?"
    
    payload = {
        "question": question,
        "chatId": chat_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat/ask", json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('answer', '')
            intent = data.get('questionType', '')
            
            print_status(f"Greeting processed successfully!", "success")
            print_status(f"Intent detected: {intent}", "info")
            print(f"\nAnswer:\n{answer}")
            return True
        else:
            print_status(f"Greeting failed: {response.text}", "error")
            return False
            
    except Exception as e:
        print_status(f"Greeting request failed: {e}", "error")
        return False

def main():
    """Run all tests"""
    print(f"\n{'='*60}")
    print(f"{BLUE}MedChat - Comprehensive Test Suite{RESET}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Test 1: Health check
    if not test_health():
        print_status("Please start the backend server first!", "error")
        sys.exit(1)
    
    # Test 2: Registration
    if not test_register():
        print_status("Registration test failed!", "warning")
    
    # Test 3: Login
    token, user_id = test_login()
    if not token:
        print_status("Cannot proceed without login token!", "error")
        sys.exit(1)
    
    # Test 4: Create chat
    chat_id = test_create_chat(token)
    if not chat_id:
        print_status("Cannot proceed without chat ID!", "error")
        sys.exit(1)
    
    # Test 5: Medical question
    test_medical_question(token, chat_id)
    
    # Test 6: Greeting
    test_greeting(token, chat_id)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"{GREEN}All tests completed!{RESET}")
    print(f"Test finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
