import os
import sys
import django

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tgproject.settings")
django.setup()

from bot.models import Language, Sphere

data = {
    "Python": ["Web-разработка", "Data Science", "Машинное обучение", "Автоматизация"],
    "JavaScript": ["Frontend", "Backend", "Fullstack", "SPA"],
    "Java": ["Android", "Spring", "Enterprise"],
    "C++": ["Геймдев", "Финансы", "Алгоритмы", "Системное ПО"],
    "Go": ["Высоконагруженные системы", "Сетевое программирование", "DevOps"],
    "Rust": ["Блокчейн", "WebAssembly", "Безопасность"],
    "C#": [".NET", "Игры (Unity)", "Приложения для Windows"],
}

for lang_name, spheres in data.items():
    lang, _ = Language.objects.get_or_create(name=lang_name)
    for sphere_name in spheres:
        Sphere.objects.get_or_create(name=sphere_name, language=lang)

print("✅ Языки и сферы успешно добавлены!")