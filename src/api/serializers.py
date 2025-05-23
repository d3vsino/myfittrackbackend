from rest_framework import serializers
from .models import CustomUser, CalorieLog, ChatSession, ChatMessage

def macro_split(calories, weight_kg, goal='maintain'):
    protein_factors = {
        'lose': 2.0,
        'maintain': 1.3,
        'gain': 1.8,
    }
    protein_factor = protein_factors.get(goal, 1.3)
    
    protein_g = round(weight_kg * protein_factor, 1)
    
    remaining_calories = calories - (protein_g * 4)
    if remaining_calories < 0:
        remaining_calories = 0
    
    fat_calories = remaining_calories * 0.25
    carb_calories = remaining_calories * 0.75
    
    fat_g = round(fat_calories / 9, 1)
    carb_g = round(carb_calories / 4, 1)
    
    return protein_g, fat_g, carb_g


class RegisterSerializer(serializers.ModelSerializer):
    calorie_goal_type = serializers.ChoiceField(
        choices=[('maintain', 'Maintain'), ('gain', 'Gain'), ('lose', 'Lose')],
        write_only=True
    )

    class Meta:
        model = CustomUser
        fields = [
            'email', 'username', 'password', 'first_name', 'last_name', 'is_premium',
            'age', 'gender', 'height_cm', 'weight_kg', 'activity_level',
            'bmr', 'maintenance_calories', 'gain_calories', 'loss_calories', 'current_calorie_goal',
            'maintenance_protein', 'maintenance_fat', 'maintenance_carbs',
            'gain_protein', 'gain_fat', 'gain_carbs',
            'loss_protein', 'loss_fat', 'loss_carbs',
            'current_protein_goal', 'current_fat_goal', 'current_carbs_goal',
            'calorie_goal_type',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'is_premium': {'read_only': True},
            'bmr': {'read_only': True},
            'maintenance_calories': {'read_only': True},
            'gain_calories': {'read_only': True},
            'loss_calories': {'read_only': True},
            'current_calorie_goal': {'read_only': True},
            'maintenance_protein': {'read_only': True},
            'maintenance_fat': {'read_only': True},
            'maintenance_carbs': {'read_only': True},
            'gain_protein': {'read_only': True},
            'gain_fat': {'read_only': True},
            'gain_carbs': {'read_only': True},
            'loss_protein': {'read_only': True},
            'loss_fat': {'read_only': True},
            'loss_carbs': {'read_only': True},
            'current_protein_goal': {'read_only': True},
            'current_fat_goal': {'read_only': True},
            'current_carbs_goal': {'read_only': True},
        }

    def create(self, validated_data):
        calorie_goal_type = validated_data.pop('calorie_goal_type')
        password = validated_data.pop('password')
    
        age = validated_data.get('age')
        gender = validated_data.get('gender')
        height = validated_data.get('height_cm')
        weight = validated_data.get('weight_kg')
        activity_level = validated_data.get('activity_level')
    
        bmr = 10 * weight + 6.25 * height - 5 * age + (5 if gender == 'male' else -161)
    
        activity_map = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'super': 1.9,
        }
        activity_multiplier = activity_map.get(activity_level, 1.2)
    
        maintenance = bmr * activity_multiplier
        gain = maintenance + 300
        loss = maintenance - 300
    
        macros = {
            'maintain': macro_split(maintenance, weight, 'maintain'),
            'gain': macro_split(gain, weight, 'gain'),
            'lose': macro_split(loss, weight, 'lose'),
        }
    
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.bmr = bmr
        user.maintenance_calories = maintenance
        user.gain_calories = gain
        user.loss_calories = loss
    
        user.current_calorie_goal = {
            'maintain': maintenance,
            'gain': gain,
            'lose': loss
        }[calorie_goal_type]
    
        macro_fields = {
            'maintain': 'maintenance',
            'gain': 'gain',
            'lose': 'loss',
        }
    
        for key, prefix in macro_fields.items():
            protein, fat, carbs = macros[key]
            setattr(user, f'{prefix}_protein', protein)
            setattr(user, f'{prefix}_fat', fat)
            setattr(user, f'{prefix}_carbs', carbs)
    
        current_macros = macros[calorie_goal_type]
        user.current_protein_goal, user.current_fat_goal, user.current_carbs_goal = current_macros
    
        user.profile_complete = all([
            validated_data.get('first_name'),
            validated_data.get('last_name'),
            age, gender, height, weight, activity_level
        ])
    
        user.save()
        return user



class CalorieLogSerializer(serializers.ModelSerializer):
    protein = serializers.FloatField(required=False)
    fat = serializers.FloatField(required=False)
    carbs = serializers.FloatField(required=False)
    class Meta:
        model = CalorieLog
        fields = ['id', 'date', 'calories', 'protein', 'fat', 'carbs', 'notes']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'age', 'gender', 'height_cm', 'weight_kg',
            'activity_level', 'current_calorie_goal',
            'bmr', 'maintenance_calories', 'gain_calories', 'loss_calories',
            'maintenance_protein', 'maintenance_fat', 'maintenance_carbs',
            'gain_protein', 'gain_fat', 'gain_carbs',
            'loss_protein', 'loss_fat', 'loss_carbs',
            'current_protein_goal', 'current_fat_goal', 'current_carbs_goal',
        ]

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['is_user', 'message', 'timestamp']

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'created_at', 'messages']
