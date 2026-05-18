
from django.core.management.base import BaseCommand
from django.db import transaction

from bugbox3.grower_portal.models import LabelGeneration
from bugbox3.grower_portal.services.label_generation_repair import prepare_label_generation_retry
from bugbox3.grower_portal.tasks import generate_labels_async


class Command(BaseCommand):
    help = 'Mark completed label generations as ready and/or re-queue stuck rows.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mark-ready-with-file',
            action='store_true',
            help='Set status=ready when label_file exists but status is not ready.',
        )
        parser.add_argument(
            '--requeue-stuck',
            action='store_true',
            help='Re-queue rows that are queued/processing/failed without a file (or mark ready if file exists).',
        )
        parser.add_argument('--cluster', type=str, help='Filter by cluster number (e.g. 83)')
        parser.add_argument('--year', type=int, help='Filter by year (e.g. 2026)')
        parser.add_argument('--project-type', type=str, choices=['avalanche', 'ignite'])
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print actions without saving or enqueueing Celery tasks.',
        )

    def handle(self, *args, **options):
        if not options['mark_ready_with_file'] and not options['requeue_stuck']:
            raise SystemExit(
                'Specify at least one of --mark-ready-with-file or --requeue-stuck.'
            )

        qs = LabelGeneration.objects.all().order_by('id')
        if options['cluster']:
            qs = qs.filter(cluster_number=options['cluster'])
        if options['year']:
            qs = qs.filter(year=options['year'])
        if options['project_type']:
            qs = qs.filter(project_type=options['project_type'])

        marked = 0
        requeued = 0
        skipped = 0

        if options['mark_ready_with_file']:
            file_qs = qs.exclude(label_file='').exclude(status='ready')
            for gen in file_qs.iterator():
                if options['dry_run']:
                    self.stdout.write(
                        f'[dry-run] Would mark ready: id={gen.id} '
                        f'{gen.project_type} {gen.cluster_number} {gen.year}'
                    )
                    marked += 1
                    continue
                gen.status = 'ready'
                gen.error_message = ''
                gen.save(update_fields=['status', 'error_message'])
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Marked ready: id={gen.id} {gen.project_type} '
                        f'{gen.cluster_number} {gen.year}'
                    )
                )
                marked += 1

        if options['requeue_stuck']:
            stuck_qs = qs.filter(status__in=['queued', 'processing', 'failed'])
            for gen in stuck_qs.iterator():
                if gen.label_file and gen.status != 'ready':
                    if options['dry_run']:
                        self.stdout.write(
                            f'[dry-run] Would mark ready (has file): id={gen.id}'
                        )
                        marked += 1
                        continue
                    gen.status = 'ready'
                    gen.error_message = ''
                    gen.save(update_fields=['status', 'error_message'])
                    self.stdout.write(self.style.SUCCESS(f'Marked ready: id={gen.id}'))
                    marked += 1
                    continue

                if options['dry_run']:
                    self.stdout.write(
                        f'[dry-run] Would re-queue: id={gen.id} '
                        f'{gen.project_type} {gen.cluster_number} {gen.year} status={gen.status}'
                    )
                    requeued += 1
                    continue

                try:
                    with transaction.atomic():
                        locked = LabelGeneration.objects.select_for_update().get(pk=gen.pk)
                        action, detail = prepare_label_generation_retry(locked)
                except ValueError as e:
                    self.stdout.write(
                        self.style.WARNING(f'Skip id={gen.id}: {e}')
                    )
                    skipped += 1
                    continue

                if action == 'requeue':
                    task = generate_labels_async.delay(locked.pk)
                    LabelGeneration.objects.filter(pk=locked.pk).update(task_id=task.id)
                    self.stdout.write(
                        self.style.SUCCESS(f'Re-queued id={locked.pk}: {detail} (task {task.id})')
                    )
                    requeued += 1
                else:
                    self.stdout.write(self.style.SUCCESS(f'id={locked.pk}: {detail}'))
                    marked += 1

        self.stdout.write(
            self.style.NOTICE(
                f'Done. marked_ready={marked} requeued={requeued} skipped={skipped} dry_run={options["dry_run"]}'
            )
        )
