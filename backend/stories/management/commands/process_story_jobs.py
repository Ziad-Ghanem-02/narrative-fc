import time

from django.core.management.base import BaseCommand

from stories.services import process_next_story_job, requeue_stale_story_jobs


class Command(BaseCommand):
    help = "Process queued story generation jobs."

    def add_arguments(self, parser):
        parser.add_argument(
            "--once",
            action="store_true",
            help="Process at most one queued job, then exit.",
        )
        parser.add_argument(
            "--poll-interval",
            type=float,
            default=1.0,
            help="Seconds to wait before checking for another job.",
        )

    def handle(self, *args, **options):
        requeued = requeue_stale_story_jobs()
        if requeued:
            self.stdout.write(f"Requeued {requeued} stale story generation job(s).")

        while True:
            processed = process_next_story_job()
            if options["once"]:
                return
            if not processed:
                time.sleep(options["poll_interval"])
