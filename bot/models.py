from django.db import models

# Create your models here.
class Grade(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name

class Language(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name
    
class Sphere(models.Model):
    name = models.CharField(max_length=100)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="spheres")

    def __str__(self):
        return f"{self.name} ({self.language.name})"
    
class Question(models.Model):
    question = models.TextField()
    correct_answer = models.TextField()
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    sphere = models.ForeignKey(Sphere, on_delete=models.CASCADE)

    def __str__(self):
        return self.question[:70]

class User(models.Model):
    user_id = models.BigIntegerField(unique=True)
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    sphere = models.ForeignKey(Sphere, on_delete=models.SET_NULL, null=True)


class User_Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.CharField(max_length=255)  
    answer = models.TextField()
    is_correct = models.BooleanField(default=False)
    confidence_score = models.FloatField(default=0.0)  # Оценка уверенности

    def __str__(self):
        return f"Ответ на {self.question} - {'✅' if self.is_correct else '❌'}"
    
