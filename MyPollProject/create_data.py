from django.contrib.auth.models import User
from django.utils import timezone
from polls.models import Question, Choice

# Test user oluştur
if not User.objects.filter(username='testuser').exists():
    User.objects.create_user('testuser', 'test@example.com', 'test123')
    print("✓ Test kullanıcısı oluşturuldu")

# Sample anket
try:
    q1 = Question.objects.create(
        question_text="Sevdiğiniz programlama dili?",
        pub_date=timezone.now()
    )
    Choice.objects.create(question=q1, choice_text="Python", votes=0)
    Choice.objects.create(question=q1, choice_text="JavaScript", votes=0)
    Choice.objects.create(question=q1, choice_text="Java", votes=0)
    print("✓ Test anketi oluşturuldu")
except:
    print("✓ Veri zaten var")
