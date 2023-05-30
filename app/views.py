from django.shortcuts import render

from app.models import Contest, Event, Group, Performance


def index(request):
    return render(request, "index.html.j2", context={"events": Event.objects.all()})


def event(request, event_id):
    event = Event.objects.get(id=event_id)
    return render(
        request,
        "event.html.j2",
        context={"contests": Contest.objects.filter(event=event).all(), "event": event},
    )


def contest(request, contest_id):
    contest = Contest.objects.get(id=contest_id)
    groups = (
        Performance.objects.filter(contest=contest)
        .values_list("group")
        .order_by()
        .distinct()
    )
    performances = []
    for group_id in groups:
        group = Group.objects.get(id=group_id[0])
        group_perfs = (
            Performance.objects.filter(contest=contest, group=group)
            .order_by("index")
            .all()
        )
        total = sum(
            [
                perf.music_score + perf.singing_score + perf.performance_score
                for perf in group_perfs
            ]
        )
        performances.append((group, group_perfs, total))
    return render(
        request,
        "contest.html.j2",
        context={
            "groups": groups,
            "performances": performances,
            "contest": contest,
        },
    )
