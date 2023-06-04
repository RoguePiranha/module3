from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile, FriendRequest
from feed.models import Post
import random

User = get_user_model()


@login_required
def users_list(request):
    users = Profile.objects.exclude(username=request.user.username)
    sent_friend_requests = FriendRequest.objects.filter(from_user=request.user.profile)
    sent_to = []
    friends = []
    for user in users:
        friend = user.friends.all()
        for f in friend:
            if f in friends:
                friend = friend.exclude(username=f.username)
        friends += friend
    my_friends = request.user.profile.friends.all()
    for i in my_friends:
        if i in friends:
            friends.remove(i)
    if request.user.profile in friends:
        friends.remove(request.user.profile)
    random_list = random.sample(list(users), min(len(list(users)), 10))
    for r in random_list:
        if r in friends:
            random_list.remove(r)
    friends += random_list
    for i in my_friends:
        if i in friends:
            friends.remove(i)
    for se in sent_friend_requests:
        sent_to.append(se.to_user)
    context = {"users": friends, "sent": sent_to}
    return render(request, "users/users_list.html", context)


def friends_list(request):
    p = request.user.profile
    friends = p.friends.all()
    context = {"friends": friends}
    return render(request, "users/friends_list.html", context)


@login_required
def send_friend_request(request, id):
    user = get_object_or_404(Profile, id=id)
    frequest, created = FriendRequest.objects.get_or_create(
        from_user=request.user.profile, to_user=user
    )
    return HttpResponseRedirect("/users/" + str(user.slug))


@login_required
def cancel_friend_request(request, id):
    user = get_object_or_404(Profile, id=id)
    frequest = FriendRequest.objects.filter(
        from_user=request.user.profile, to_user=user
    ).first()
    frequest.delete()
    return HttpResponseRedirect("/users/" + str(user.slug))


@login_required
def accept_friend_request(request, id):
    from_user = get_object_or_404(Profile, id=id)
    frequest = FriendRequest.objects.filter(
        from_user=from_user, to_user=request.user.profile
    ).first()
    user1 = frequest.to_user
    user2 = from_user
    user1.friends.add(user2)
    user2.friends.add(user1)
    if FriendRequest.objects.filter(
        from_user=request.user.profile, to_user=from_user
    ).first():
        request_rev = FriendRequest.objects.filter(
            from_user=request.user.profile, to_user=from_user
        ).first()
        request_rev.delete()
    frequest.delete()
    return HttpResponseRedirect("/users/" + str(request.user.profile.slug))


@login_required
def delete_friend_request(request, id):
    from_user = get_object_or_404(Profile, id=id)
    frequest = FriendRequest.objects.filter(
        from_user=from_user, to_user=request.user.profile
    ).first()
    frequest.delete()
    return HttpResponseRedirect("/users/" + str(request.user.profile.slug))


def delete_friend(request, id):
    user_profile = request.user.profile
    friend_profile = get_object_or_404(Profile, id=id)
    user_profile.friends.remove(friend_profile)
    friend_profile.friends.remove(user_profile)
    return HttpResponseRedirect("/users/" + str(friend_profile.slug))


@login_required
def profile_view(request, slug):
    p = Profile.objects.filter(slug=slug).first()
    u = p.username
    sent_friend_requests = FriendRequest.objects.filter(from_user=p)
    rec_friend_requests = FriendRequest.objects.filter(to_user=p)
    user_posts = Post.objects.filter(user_name=u).order_by("-created")

    friends = p.friends.all()

    # is this user our friend
    button_status = "none"
    if p not in request.user.profile.friends.all():
        button_status = "not_friend"

        # if we have sent them a friend request
        if (
            len(
                FriendRequest.objects.filter(from_user=request.user.profile).filter(
                    to_user=p
                )
            )
            == 1
        ):
            button_status = "friend_request_sent"

        # if we have received a friend request
        if (
            len(
                FriendRequest.objects.filter(from_user=p).filter(
                    to_user=request.user.profile
                )
            )
            == 1
        ):
            button_status = "friend_request_received"
    context = {
        "u": u,
        "p": p,
        "button_status": button_status,
        "sent_friend_requests": sent_friend_requests,
        "rec_friend_requests": rec_friend_requests,
        "friends": friends,
        "post_count": user_posts.count(),
        "posts": user_posts,
    }
    return render(request, "users/profile.html", context)


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # save the form
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(
                request, f"Your account has been created! You are now able to login."
            )
            return redirect("login")
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {"form": form})


@login_required
def edit_profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        if u_form.is_valid() and p_form.is_valid():
            # save the form
            u_form.save()
            p_form.save()
            messages.success(request, f"Your account has been updated!")
            return redirect("profile-detail", slug=request.user.profile.slug)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    context = {"u_form": u_form, "p_form": p_form}
    return render(request, "users/edit_profile.html", context)


@login_required
def my_profile(request):
    p = request.user.profile
    you = p.username
    sent_friend_requests = FriendRequest.objects.filter(from_user=p)
    rec_friend_requests = FriendRequest.objects.filter(to_user=p)
    user_posts = Post.objects.filter(user_name=you).order_by("-created")
    friends = p.friends.all()

    # is this user our friend
    button_status = "none"
    if p not in request.user.profile.friends.all():
        button_status = "not_friend"

        # if we have sent them a friend request
        if (
            len(
                FriendRequest.objects.filter(from_user=request.user.profile).filter(
                    to_user=p
                )
            )
            == 1
        ):
            button_status = "friend_request_sent"

        # if we have received a friend request
        if (
            len(
                FriendRequest.objects.filter(from_user=p).filter(
                    to_user=request.user.profile
                )
            )
            == 1
        ):
            button_status = "friend_request_received"

            #  if we have sent them a friend request
            if (
                len(
                    FriendRequest.objects.filter(from_user=request.user.profile).filter(
                        to_user=p
                    )
                )
                == 1
            ):
                button_status = "friend_request_sent"

            if (
                len(
                    FriendRequest.objects.filter(from_user=p).filter(
                        to_user=request.user.profile
                    )
                )
                == 1
            ):
                button_status = "friend_request_received"

    context = {
        "u": you,
        "p": p,
        "button_status": button_status,
        "sent_friend_requests": sent_friend_requests,
        "rec_friend_requests": rec_friend_requests,
        "friends": friends,
        "post_count": user_posts.count(),
    }
    return render(request, "users/my_profile.html", context)


@login_required
def search_users(request):
    query = request.GET.get("q")
    object_list = Profile.objects.filter(username__icontains=query)
    context = {"users": object_list}
    return render(request, "users/search_users.html", context)


@login_required
def friend_requests(request):
    p = request.user.profile
    sent_friend_requests = FriendRequest.objects.filter(from_user=p)
    rec_friend_requests = FriendRequest.objects.filter(to_user=p)
    context = {
        "sent_friend_requests": sent_friend_requests,
        "rec_friend_requests": rec_friend_requests,
    }
    return render(request, "users/friend_requests.html", context)
