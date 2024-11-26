from django.apps import AppConfig


class SchedulejobConfig(AppConfig):
    name = 'schedulejob'

    def ready(self):
        import execute_cron
        execute_cron.start()

