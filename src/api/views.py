import base64
from django.shortcuts import render
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import requests
from rest_framework import viewsets, permissions, status
from .models import CalorieLog, CustomUser, ChatMessage, ChatSession
from .serializers import CalorieLogSerializer, RegisterSerializer, ChatMessageSerializer, ChatSessionSerializer
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

# Create your views here.

class RegisterView(APIView):
    permission_classes = [] 
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            print(serializer.errors)
            return Response(RegisterSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        



class CalorieGoalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            "bmr": user.bmr,
            "maintenance_calories": user.maintenance_calories,
            "gain_calories": user.gain_calories,
            "loss_calories": user.loss_calories,
            "current_calorie_goal": user.current_calorie_goal,
            "maintenance_protein": user.maintenance_protein,
            "maintenance_fat": user.maintenance_fat,
            "maintenance_carbs": user.maintenance_carbs,
            "gain_protein": user.gain_protein,
            "gain_fat": user.gain_fat,
            "gain_carbs": user.gain_carbs,
            "loss_protein": user.loss_protein,
            "loss_fat": user.loss_fat,
            "loss_carbs": user.loss_carbs,
        }
        return Response(data)



class MacroFromImageView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({"error": "No image provided."}, status=400)

        image_bytes = image_file.read()
        base64_image = base64.b64encode(image_bytes).decode()

        payload = {
            "model": "meta-llama/Llama-Vision-Free",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        },
                        {
                            "type": "text",
                            "text": "What are the estimated macros (protein, carbs, fat) in grams for this meal?"
                        }
                    ]
                }
            ],
            "max_tokens": 512,
            "temperature": 0.5
        }

        headers = {
            "Authorization": f"Bearer {settings.TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            res = requests.post("https://api.together.xyz/v1/chat/completions", headers=headers, json=payload)
            res.raise_for_status()
            result = res.json()["choices"][0]["message"]["content"]
            return Response({"macros": result})
        except Exception as e:
            return Response({"error": "Failed to get response from Together AI", "details": str(e)}, status=500)

class AiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user_input = request.data.get("message")
        session_id = request.data.get("session_id")

        if not user_input:
            return Response({"error": "No message provided"}, status=status.HTTP_400_BAD_REQUEST)
            
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=user)
            except ChatSession.DoesNotExist:
                return Response({"error": "Session not found."}, status=404)
        else:
            session = ChatSession.objects.create(user=user, title=user_input)
            session_id = str(session.id)

        user_data = RegisterSerializer(user).data
        user_details = (
            f"User details: Name: {user_data.get('first_name', '')} {user_data.get('last_name', '')}, "
            f"Age: {user_data.get('age', '')}, Gender: {user_data.get('gender', '')}, "
            f"Height: {user_data.get('height_cm', '')} cm, Weight: {user_data.get('weight_kg', '')} kg, "
            f"Activity Level: {user_data.get('activity_level', '')}, "
            f"Current Calorie Goal: {user_data.get('current_calorie_goal', '')}, "
            f"BMR: {user_data.get('bmr', '')}, "
            f"Macros (protein/fat/carbs): {user_data.get('current_protein_goal', '')}/"
            f"{user_data.get('current_fat_goal', '')}/{user_data.get('current_carbs_goal', '')} grams."
        )
        messages = [{
            "role": "system",
            "content": f"You are a helpful nutritionist, don't think and these are user details: {user_details} Respond concisely and personally."
        }]
        for msg in ChatMessage.objects.filter(session=session).order_by('timestamp'):
            messages.append({
                "role": "user" if msg.is_user else "assistant",
                "content": msg.message
            })

        messages.append({"role": "user", "content": user_input})

        headers = {
            "Authorization": f"Bearer {settings.TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
            "messages": messages,
            "temperature": 0.5,
            "max_tokens": 1024
        }

        res = requests.post("https://api.together.xyz/v1/chat/completions", json=data, headers=headers)
        if res.status_code != 200:
            return Response({"error": "AI error", "detail": res.text}, status=500)

        ai_reply = res.json()["choices"][0]["message"]["content"]

        ChatMessage.objects.create(session=session, is_user=True, message=user_input)
        ChatMessage.objects.create(session=session, is_user=False, message=ai_reply)

        return Response({
            "reply": ai_reply,
            "session_id": session_id
        })

class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
            sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')
            serializer = ChatSessionSerializer(sessions, many=True)
            return Response(serializer.data)


class CalorieLogViewSet(viewsets.ModelViewSet):
    serializer_class = CalorieLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CalorieLog.objects.filter(user=self.request.user).order_by('-date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = RegisterSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        instance = request.user
        goal = request.data.get('calorie_goal_type', None)
        if goal:
            instance.calorie_goal_type = goal
            if goal == 'maintain':
                instance.current_calorie_goal = instance.maintenance_calories
            elif goal == 'gain':
                instance.current_calorie_goal = instance.gain_calories
            elif goal == 'lose':
                instance.current_calorie_goal = instance.loss_calories

        serializer = RegisterSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
