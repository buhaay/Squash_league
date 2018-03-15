from django.conf.global_settings import MEDIA_ROOT
from django.contrib.auth.models import AbstractUser
from django.db import models



SKILLS = (
    (1, "Szturmowiec"),
    (2, "Padawan"),
    (3, "Rycerz Jedi"),
    (4, "Mistrz Joda"),
)


class MyUser(AbstractUser):
    skill = models.IntegerField(choices=SKILLS, null=True)
    avatar = models.ImageField(null=True, blank=True, upload_to=MEDIA_ROOT)


class SportCenter(models.Model):
    name = models.CharField(max_length=64)
    address = models.CharField(max_length=256)
    phone_number = models.PositiveIntegerField()
    domain = models.URLField()
    slug = models.SlugField(blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def title(self):
        return self.name


class Rooms(models.Model):
    room_number = models.IntegerField()
    sport_center = models.ForeignKey(SportCenter)
    availability = models.BooleanField(default=True)

    def __str__(self):
        return "%s %s" % (self.sport_center, self.room_number)


class SquashCourt(models.Model):
    sport_center = models.ForeignKey(SportCenter)
    room_number = models.IntegerField()


class Reservation(models.Model):
    user_main = models.ForeignKey(MyUser, related_name='reservation')
    user_partner = models.ForeignKey(MyUser, related_name='user_partner', null=True)
    date = models.DateField(auto_now=False, auto_now_add=False, verbose_name='Wybierz dzień')
    time_start = models.TimeField(auto_now=False, auto_now_add=False, verbose_name='Początek rezerwacji')
    time_end = models.TimeField(auto_now=False, auto_now_add=False, verbose_name='Koniec rezerwacji')
    location = models.ForeignKey(SportCenter, verbose_name='Wybierz lokalizację')
    comment = models.CharField(max_length=256, null=True)


class Score(models.Model):
    room = models.OneToOneField(Reservation)
    user_main_score = models.IntegerField()
    user_partner_score = models.IntegerField()

    def __str__(self):
        return "%s : %s" % (self.user_main_score, self.user_partner_score)


class UserStats(models.Model):
    user = models.ForeignKey(MyUser, related_name='stats')
    games_played = models.IntegerField(default=0)
    games_won = models.IntegerField(default=0)
    games_lost = models.IntegerField(default=0)
    sets_won = models.IntegerField(default=0)
    sets_lost = models.IntegerField(default=0)
    ranking = models.IntegerField(null=True)



