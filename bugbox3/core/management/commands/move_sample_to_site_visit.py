from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from bugbox3.samples.models import Sample, SiteVisit


class Command(BaseCommand):
    help = 'Move a sample from one site visit to another site visit (within same site or different sites)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sample-id',
            type=int,
            help='Sample ID to move'
        )
        parser.add_argument(
            '--source-site-visit-id',
            type=int,
            help='Source site visit ID where the sample currently is'
        )
        parser.add_argument(
            '--target-site-visit-id',
            type=int,
            help='Target site visit ID where you want to move the sample'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be moved without actually moving it'
        )

    def handle(self, *args, **options):
        sample_id = options['sample_id']
        source_site_visit_id = options['source_site_visit_id']
        target_site_visit_id = options['target_site_visit_id']
        dry_run = options['dry_run']

        if not any([sample_id, source_site_visit_id, target_site_visit_id]):
            raise CommandError("You must provide at least one identifying parameter")

        try:
            if sample_id:
                sample = Sample.objects.select_related(
                    'site_visit__site'
                ).get(id=sample_id)
            elif source_site_visit_id:
                samples = Sample.objects.select_related(
                    'site_visit__site'
                ).filter(site_visit_id=source_site_visit_id)
                
                if samples.count() == 0:
                    raise CommandError(f"No samples found in site visit {source_site_visit_id}")
                elif samples.count() == 1:
                    sample = samples.first()
                else:
                    self.stdout.write(f"Found {samples.count()} samples in site visit {source_site_visit_id}:")
                    for s in samples:
                        self.stdout.write(f"  Sample ID: {s.id}, Name: {s.name_no}, Type: {s.sample_type}, Specimens: {s.specimen_set.count()}")
                    raise CommandError("Multiple samples found. Please specify --sample-id to choose which one to move")
            else:
                raise CommandError("Must provide either --sample-id or --source-site-visit-id")

            self.stdout.write(f"Found sample: {sample.name_no} (ID: {sample.id})")
            self.stdout.write(f"Current site: {sample.site_visit.site.site_name}")
            self.stdout.write(f"Current site visit ID: {sample.site_visit.id}")
            self.stdout.write(f"Current visit date: {sample.site_visit.visit_date}")
            self.stdout.write(f"Specimens count: {sample.specimen_set.count()}")

            # Find the target site visit
            target_site_visit = SiteVisit.objects.select_related('site').get(
                id=target_site_visit_id
            )

            self.stdout.write(f"Target site: {target_site_visit.site.site_name}")
            self.stdout.write(f"Target site visit ID: {target_site_visit.id}")
            self.stdout.write(f"Target visit date: {target_site_visit.visit_date}")
            self.stdout.write(f"Target experiment: {target_site_visit.site.experiment.name}")

            if dry_run:
                self.stdout.write(self.style.WARNING("DRY RUN - No changes made"))
                self.stdout.write(f"Would move sample '{sample.name_no}' (ID: {sample.id}) from:")
                self.stdout.write(f"  Site: {sample.site_visit.site.site_name}")
                self.stdout.write(f"  Site Visit ID: {sample.site_visit.id}")
                self.stdout.write(f"  Visit Date: {sample.site_visit.visit_date}")
                self.stdout.write(f"To:")
                self.stdout.write(f"  Site: {target_site_visit.site.site_name}")
                self.stdout.write(f"  Site Visit ID: {target_site_visit.id}")
                self.stdout.write(f"  Visit Date: {target_site_visit.visit_date}")
                return

            with transaction.atomic():
                old_site_visit = sample.site_visit
                sample.site_visit = target_site_visit
                sample.save()

                remaining_samples = Sample.objects.filter(site_visit=old_site_visit).count()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully moved sample '{sample.name_no}' (ID: {sample.id}) to site visit {target_site_visit.id}"
                    )
                )
                
                if remaining_samples == 0:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Old site visit {old_site_visit.id} ({old_site_visit.site.site_name} - {old_site_visit.visit_date}) "
                            f"now has no samples. You may want to delete it."
                        )
                    )
                else:
                    self.stdout.write(f"Old site visit {old_site_visit.id} still has {remaining_samples} samples.")

        except Sample.DoesNotExist:
            raise CommandError(f"Sample with ID {sample_id} not found")
        except SiteVisit.DoesNotExist:
            raise CommandError(f"Target site visit with ID {target_site_visit_id} not found")
        except Exception as e:
            raise CommandError(f"Error: {str(e)}")
