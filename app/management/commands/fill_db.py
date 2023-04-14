from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app import models
from lorem_text import lorem
import names
import time
import random


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def handle(self, *args, **options):
        ratio = options['ratio']
        profiles = []
        tags = []
        questions = []
        answers = []
        for i in range(ratio):
            name = names.get_first_name()
            profiles.append(
                models.Profile(

                    user=User.objects.create_user(
                        username=name + str(
                            time.time()).split(".")[1],
                        email=name + "@test.ru")))
            tags.append(
                models.Tag(
                    name=(lorem.words(1) + "t" +
                          str(time.time()).split(".")[1])[:12] + str(i),
                    color=(str(random.choice(range(0, 255, 1))) + ", " + str(random.choice(range(0, 255, 1))) + ", " + str(random.choice(range(0, 255, 1))))))
        profiles = models.Profile.objects.bulk_create(profiles)
        tags = models.Tag.objects.bulk_create(tags)

        print("profiles OK")

        for i in range(ratio * 10):
            question = models.Question.objects.create(
                author=random.choice(profiles),
                title=lorem.words(3) + str(i) + "?",
                text=lorem.words(
                    random.choice(
                        range(
                            20,
                            50))),
                rating=0,
                answers_count=0)
            tags_id = random.choices(range(len(tags)),
                                     k=random.choice(range(1, 5)))

            for id in tags_id:
                tags[id].count += 1
                question.tags.add(tags[id])
            questions.append(question)

            print(str(i) + "question OK")
        models.Tag.objects.bulk_update(tags, ['count'])

        for i in range(ratio * 100):
            question_id = random.choice(range(len(questions)))
            questions[question_id].answers_count += 1
            answer = models.Answer.objects.create(
                author=random.choice(profiles),
                question=questions[question_id],
                text=lorem.words(
                    random.choice(
                        range(
                            20,
                            50))),
                rating=0)
            answers.append(answer)
            print(str(i) + "answer OK")
        models.Question.objects.bulk_update(questions, ['answers_count'])

        print("answers OK")

        for i in range(ratio * 400):
            x = bool(random.getrandbits(1))
            if (i % 2 == 0):
                question_id = random.choice(range(len(questions)))
                if x:
                    questions[question_id].rating += 1
                else:
                    questions[question_id].rating -= 1
                models.QuestionGrade.objects.create(user=random.choice(profiles),
                                                    question=questions[question_id],
                                                    value=x)

            else:
                answer_id = random.choice(range(len(answers)))
                if x:
                    answers[answer_id].rating += 1
                else:
                    answers[answer_id].rating -= 1
                models.AnswerGrade.objects.create(user=random.choice(profiles),
                                                  answer=answers[answer_id],
                                                  value=x)
                print(str(i) + " grade")
        models.Question.objects.bulk_update(questions, ['rating'])
        models.Answer.objects.bulk_update(answers, ['rating'])
        print("Askme is filled")
