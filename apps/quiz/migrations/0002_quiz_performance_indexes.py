from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='studysession',
            index=models.Index(fields=['user', 'set', 'is_completed'], name='quiz_session_active_idx'),
        ),
        migrations.AddIndex(
            model_name='studysession',
            index=models.Index(fields=['user', 'created_at'], name='quiz_session_user_date_idx'),
        ),
        migrations.AddIndex(
            model_name='studyanswer',
            index=models.Index(fields=['session', 'correct'], name='quiz_answer_result_idx'),
        ),
        migrations.AddIndex(
            model_name='studyanswer',
            index=models.Index(fields=['flashcard', 'correct'], name='quiz_answer_card_idx'),
        ),
    ]
