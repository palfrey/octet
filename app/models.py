from django.db import models


class Organiser(models.Model):
    name = models.TextField(unique=True)


class Event(models.Model):
    name = models.TextField(unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    organiser = models.ForeignKey(Organiser, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="event_organiser_name",
                fields=["organiser", "name"],
            )
        ]


class Contest(models.Model):
    name = models.TextField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="contest_event_name",
                fields=["event", "name"],
            )
        ]


class Group(models.Model):
    name = models.TextField(unique=True)
    director = models.TextField()
    member_count = models.IntegerField()


class Performance(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    song_name = models.TextField()
    singing_score = models.IntegerField()
    performance_score = models.IntegerField()
    music_score = models.IntegerField()
    index = models.IntegerField()


class Meta:
    constraints = [
        models.UniqueConstraint(
            name="performance_group",
            fields=["group", "contest", "index"],
        )
    ]
