#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Q

from .models import SportCenter, Reservation, MyUser, UserStats, Score, Messages
from .forms import CreateReservationForm, SignUpForm, ScoreForm, EditProfileForm, SearchRoomForm, AcceptScoreForm

# Create your views here.
from django.views import View
from django.views.generic import FormView, DetailView


class HomeView(View):
    def get(self, request):
        return render(request, 'index.html', {})


class SignUpView(View):
    def get(self, request):
        form = SignUpForm()
        return render(request, 'signup.html', {'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
        else:
            return HttpResponse(str(form.errors))


class ShowProfileView(View):
    def get(self, request, user_id):
        user = MyUser.objects.get(pk=user_id)
        games = user.reservation.all()
        user_stat = UserStats.objects.get_or_create(user_id=user_id)
        return render(request, 'show_profile.html', {"user": user,
                                                     "games": games,
                                                     "user_stat": user_stat})


class CreateReservationView(LoginRequiredMixin, View):
    def get(self, request):
        form = CreateReservationForm()
        return render(request, 'create_reservation.html', {'form': form})

    def post(self, request):
        form = CreateReservationForm(request.POST)
        if form.is_valid():
            location = form.cleaned_data['location']
            date = form.cleaned_data['date']
            time_start = form.cleaned_data['time_start'] + ':00'
            time_end = form.cleaned_data['time_end'] + ':00'
            parsed_time = datetime.datetime.strptime(time_start, '%H:%M').time()
            date_to_check = datetime.datetime.combine(date, parsed_time)
            now = datetime.datetime.now()
            if date_to_check < now:
                message = 'Wybierz datę z przyszłości.'
                return render(request, 'create_reservation.html', {'message': message,
                                                                   'form': form,})
            Reservation.objects.create(user_main=request.user,
                                       location=location,
                                       date=date,
                                       time_start=time_start,
                                       time_end=time_end)
            return redirect(reverse('user_reservations'))


class SportCenterListView(View):
    def get(self, request):
        sport_centres = SportCenter.objects.all()
        return render(request, 'sport_centres_list.html', {'sport_centres': sport_centres})


class SportCenterDetailView(DetailView):
    queryset = SportCenter.objects.all()

    def get_context_data(self, **kwargs):
        print(self.kwargs)
        context = super(SportCenterDetailView, self).get_context_data(**kwargs)
        print(context)
        return context


class JoinRoomView(LoginRequiredMixin, View):
    def get(self, request):
        form = SearchRoomForm()
        rooms = Reservation.objects.filter(user_partner__isnull=True,
                                           date__gte=datetime.datetime.today(),
                                           user_main__skill=request.user.skill).exclude(user_main=request.user).order_by('date')

        return render(request, 'reservations_list.html', {'rooms': rooms,
                                                          'form': form})

    def post(self, request):
        form = SearchRoomForm(request.POST)
        if form.is_valid():
            date_start = form.cleaned_data['date_start']
            date_end = form.cleaned_data['date_end']
            location = form.cleaned_data['location']
            opponent_skill = form.cleaned_data['opponent_skill']
            queryset = Reservation.objects.filter(date__gte=date_start,
                                                  date__lte=date_end,
                                                  location=location,
                                                  user_main__skill=opponent_skill).exclude(Q(user_main=request.user) |
                                                                                           Q(user_partner=request.user))
            return render(request, 'room_list.html', {'queryset': queryset,
                                                      'form': form})


class ReservationDetailView(View):
    def get(self, request, room_id):

        reservation = Reservation.objects.get(pk=room_id)
        past = False
        try:
            score = Score.objects.get(room_id=room_id)
        except Score.DoesNotExist:
            score = None

        # reservation date
        reservation_date = datetime.datetime.combine(reservation.date, reservation.time_end)
        now = datetime.datetime.now()
        if now > reservation_date:
            past = True

        # check if display score form
        score_form = None
        if past:
            if not score:
                if reservation.user_partner:
                    score_form = ScoreForm(prefix='score', 
                                           initial={'user_main_score'    : 0,
                                                    'user_partner_score' : 0})
                    score_form.fields['user_main_score'].label = reservation.user_main
                    score_form.fields['user_partner_score'].label = reservation.user_partner

        # cancel reservation button
        cancel_reservation = False
        if request.user.id == reservation.user_main_id or reservation.user_partner_id:
            if not score:
                if not past:
                    cancel_reservation = True

        print(reservation.user_main_id)
        print(self.request.user.id)

        context = {'room'               : reservation,
                   'score_form'         : score_form,
                   'score'              : score,
                   'cancel_reservation' : cancel_reservation
                   }

        return render(request, 'reservation_detail.html', context)

    def post(self, request, room_id):
        room = Reservation.objects.get(pk=room_id)
        if room.user_partner_id is None:
            room.user_partner_id = request.user.id
            room.save()
            message = "Pomyślnie dołączyłeś do rezerwacji %s" % room.user_main
            private_message = "%s dołączył do Twojej rezerwacji" % room.user_partner
            Messages.objects.create(user=room.user_main, content=private_message)
            return redirect('/reservations_list/%s' % room_id)
        else:
            form = ScoreForm(request.POST, prefix='score')
            if 'score-user_main_score' and 'score-user_partner_score' in request.POST:
                if form.is_valid():
                    score = form.save(commit=False)
                    score.room = room
                    score.save()
                return redirect('/reservations_list/%s' % room_id)
            elif 'accept_score' in request.POST:
                room.score.is_confirmed_by_user_partner = True
                    # user_main_stats, _ = UserStats.objects.get_or_create(user_id=room.user_main_id)
                    # user_partner_stats, _ = UserStats.objects.get_or_create(user_id=room.user_partner_id)


                        # if score.user_main_score > score.user_partner_score:
                        #     UserStats.objects.add_winner_stats(user_main_stats, score)
                        #     UserStats.objects.add_looser_stats(user_partner_stats, score)
                        # else:
                        #     UserStats.objects.add_winner_stats(user_partner_stats, score)
                        #     UserStats.objects.add_looser_stats(user_main_stats, score)


                return redirect('/reservations_list/%s' % room_id)


class DeleteRoom(View):
    def get(self, request, room_id):
        room = Reservation.objects.get(pk=room_id)
        room.delete()
        return redirect('/profile/%s' % request.user.id)


class UserReservationsView(View):
    def get(self, request):
        rooms = request.user.reservation.filter(date__gt=datetime.datetime.now()).order_by('date')
        return render(request, 'user_reservations.html', {'rooms': rooms})


class UserHistoryView(View):
    def get(self, request):
        rooms = Reservation.objects.filter(Q(user_main=request.user) | Q(user_partner=request.user),
                                           date__lt=datetime.datetime.today()).order_by('date')
        return render(request, 'user_history.html', {'rooms': rooms})


class UserFutureGamesView(View):
    def get(self, request):
        games = Reservation.objects.filter(Q(user_main=request.user) | Q(user_partner=request.user),
                                           Q(user_main__isnull=False), Q(user_partner__isnull=False),
                                           date__gt=datetime.datetime.today())
        return render(request, 'user_games.html', {'games': games})


class EditProfileView(View):
    def get(self, request):
        form = EditProfileForm(instance=request.user)
        return render(request, 'edit_profile.html', {'form': form})

    def post(self, request):
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return render(request, 'show_profile.html', {'form': form})


class MessagesView(View):
    def get(self, request):
        messages = Messages.objects.filter(user=request.user)
        return render(request, 'kalendar.html', {'messages': messages})