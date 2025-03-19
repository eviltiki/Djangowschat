from dataclasses import dataclass
from django.contrib.auth.models import User

@dataclass
class UserCreator:
    id: int

    def get(self):
        if self.id:
            return User.objects.filter(is_active=True).filter(id=self.id).first()
