from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from bugbox3.samples.models import (
    Experiment, Site, SiteVisit, Sample, Specimen, SpecimenImage, SamplePlan,
    MultiSpecimenImage, TimelineEvent
)
from bugbox3.samples.views_demo import get_demo_organization
from bugbox3.samples import constants


class Command(BaseCommand):
    help = 'Copy specific site and samples from "DEMO: 1000 Farms" experiment to demo organization'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Delete existing demo data before copying',
        )
        parser.add_argument(
            '--skip-images',
            action='store_true',
            help='Skip copying specimen images (faster, but specimens will have no images)',
        )

    def handle(self, *args, **options):
        clear_existing = options['clear_existing']
        skip_images = options['skip_images']

        source_org_id = constants.ECDYSIS_ORGANIZATION_ID
        demo_org = get_demo_organization()

        with transaction.atomic():
            self.stdout.write(self.style.SUCCESS(f'Using demo organization: {demo_org.name} (ID: {demo_org.id})'))

            if clear_existing:
                self.stdout.write(self.style.WARNING('Clearing existing demo data...'))
                Experiment.objects.filter(organization=demo_org).delete()
                self.stdout.write(self.style.SUCCESS('Cleared existing demo data'))

            quads_experiment = Experiment.objects.filter(
                organization_id=source_org_id,
                name='1000 Farms Quads'
            ).first()

            sweeps_experiment = Experiment.objects.filter(
                organization_id=source_org_id,
                name='1000 Farms Sweeps'
            ).first()

            if not quads_experiment:
                self.stdout.write(
                    self.style.ERROR('Experiment "1000 Farms Quads" not found in source organization (ID=1).')
                )
                return

            if not sweeps_experiment:
                self.stdout.write(
                    self.style.ERROR('Experiment "1000 Farms Sweeps" not found in source organization (ID=1).')
                )
                return

            self.stdout.write(
                self.style.SUCCESS(
                    f'Found experiments:\n'
                    f'  - {quads_experiment.name} (ID: {quads_experiment.id})\n'
                    f'  - {sweeps_experiment.name} (ID: {sweeps_experiment.id})'
                )
            )

            quads_site = Site.objects.filter(
                experiment=quads_experiment,
                site_name='4189'
            ).first()

            sweeps_site = Site.objects.filter(
                experiment=sweeps_experiment,
                site_name='4189'
            ).first()

            if not quads_site:
                self.stdout.write(
                    self.style.ERROR('Site "4189" not found in experiment "1000 Farms Quads".')
                )
                return

            if not sweeps_site:
                self.stdout.write(
                    self.style.ERROR('Site "4189" not found in experiment "1000 Farms Sweeps".')
                )
                return

            self.stdout.write(
                self.style.SUCCESS(
                    f'\nFound site "4189" in both experiments:\n'
                    f'  - {quads_site.site_name} (ID: {quads_site.id}) in {quads_experiment.name}\n'
                    f'  - {sweeps_site.site_name} (ID: {sweeps_site.id}) in {sweeps_experiment.name}'
                )
            )

            quadrat_samples_qs = Sample.objects.filter(
                site_visit__site=quads_site,
                sample_type__in=['quadrat'],
                name_no__in=['T3', 'T4']
            ).select_related('site_visit', 'site_visit__site__experiment').annotate(
                specimen_count=Count('specimen')
            ).order_by('name_no', '-specimen_count', '-id')

            sweep_samples_qs = Sample.objects.filter(
                site_visit__site=sweeps_site,
                sample_type__in=['vegetation_sweep', 'vegetation sweep'],
                name_no__in=['T3', 'T4']
            ).select_related('site_visit', 'site_visit__site__experiment').annotate(
                specimen_count=Count('specimen')
            ).order_by('name_no', '-specimen_count', '-id')

            all_samples_list = []
            seen_keys = set()
            
            for sample in list(quadrat_samples_qs) + list(sweep_samples_qs):
                sample_type_normalized = sample.sample_type.lower().replace(' ', '_')
                key = (sample_type_normalized, sample.name_no)
                
                if key not in seen_keys:
                    seen_keys.add(key)
                    all_samples_list.append(sample)
                    self.stdout.write(
                        f'  Selected: {sample.sample_type} {sample.name_no} '
                        f'({sample.specimen_count} specimens)'
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  Skipping duplicate: {sample.sample_type} {sample.name_no} '
                            f'({sample.specimen_count} specimens) - already selected one with more data'
                        )
                    )

            self.stdout.write(f'\nProcessing samples from site "4189":')
            
            source_samples = all_samples_list

            expected_samples = [
                ('quadrat', 'T3'),
                ('quadrat', 'T4'),
                ('vegetation_sweep', 'T3'),
                ('vegetation_sweep', 'T4'),
            ]

            found_samples = {(s.sample_type.lower().replace(' ', '_'), s.name_no) for s in source_samples}
            normalized_expected = {(t.lower().replace(' ', '_'), n) for t, n in expected_samples}
            missing_samples = [s for s in normalized_expected if s not in found_samples]

            if missing_samples:
                missing_list = ", ".join([f"{t.replace('_', ' ').title()} {n}" for t, n in missing_samples])
                self.stdout.write(
                    self.style.WARNING(
                        f'\n⚠ Missing samples: {missing_list}'
                    )
                )
                self.stdout.write(
                    self.style.WARNING(
                        'These samples may not exist in the source database or may be on a different visit date.'
                    )
                )

            if not source_samples:
                self.stdout.write(
                    self.style.ERROR('No matching samples found. Expected: Quadrat T3/T4, Vegetation sweep T3/T4')
                )
                return

            self.stdout.write(f'\nFound {len(source_samples)} matching samples to copy:')
            for s in source_samples:
                self.stdout.write(f'  - {s.sample_type} {s.name_no} (from {s.site_visit.site.experiment.name})')

            copied_experiment = self.create_demo_experiment(quads_experiment, demo_org)
            
            for exp in [quads_experiment, sweeps_experiment]:
                self.copy_sample_plans(exp, copied_experiment)
            
            copied_site = self.copy_site(quads_site, copied_experiment)

            visit_mapping = {}
            sample_mapping = {}
            total_specimens = 0
            total_images = 0

            for source_sample in source_samples:
                source_visit = source_sample.site_visit

                if source_visit.id not in visit_mapping:
                    copied_visit = self.copy_site_visit(source_visit, copied_site, sample_with_plan=False)
                    visit_mapping[source_visit.id] = copied_visit
                    self.stdout.write(
                        f'  Created site visit: {copied_visit.visit_date.strftime("%d-%b-%Y")}'
                    )

                copied_visit = visit_mapping[source_visit.id]
                copied_sample = self.copy_sample(source_sample, copied_visit)
                sample_mapping[source_sample.id] = copied_sample

                self.stdout.write(
                    f'  Copied sample: {source_sample.sample_type} {source_sample.name_no}'
                )

                self.copy_multi_specimen_images(source_sample, copied_sample)

                source_specimens = Specimen.objects.filter(sample=source_sample)
                for source_specimen in source_specimens:
                    copied_specimen = self.copy_specimen(source_specimen, copied_sample)
                    total_specimens += 1

                    if not skip_images:
                        images_count = self.copy_specimen_images_for_specimen(
                            source_specimen, copied_specimen
                        )
                        total_images += images_count

                    self.copy_timeline_events(source_specimen, copied_specimen)

            self.stdout.write(
                self.style.SUCCESS(
                    f'\nDemo data copied successfully!\n'
                    f'  - Experiment: {copied_experiment.name} (ID: {copied_experiment.id})\n'
                    f'  - Site: {copied_site.site_name} (ID: {copied_site.id})\n'
                    f'  - Site Visits: {len(visit_mapping)}\n'
                    f'  - Samples: {len(sample_mapping)}\n'
                    f'  - Specimens: {total_specimens}\n'
                    f'  - Specimen Images: {total_images}'
                )
            )

    def create_demo_experiment(self, source_experiment, demo_org):
        """Create the "DEMO: 1000 Farms" experiment in demo org."""
        experiment, created = Experiment.objects.get_or_create(
            organization=demo_org,
            abbreviation='demo-1000-farms',
            defaults={
                'name': 'DEMO: 1000 Farms',
                'from_year': source_experiment.from_year if source_experiment else 2025,
                'to_year': source_experiment.to_year if source_experiment else 2025,
                'leader': source_experiment.leader if source_experiment else 'Demo Leader',
                'no_sites': 1,
                'date_per_site': source_experiment.date_per_site if source_experiment else 1,
                'completed': False,
                'summary': 'Demo experiment showcasing the Bugbox research workflow with selected samples from the 1000 Farms study.',
                'archived': '',
            }
        )
        if created:
            self.stdout.write(f'Created experiment: {experiment.name}')
        else:
            self.stdout.write(f'Using existing experiment: {experiment.name}')
        return experiment

    def copy_sample_plans(self, source_experiment, target_experiment):
        source_plans = SamplePlan.objects.filter(experiment=source_experiment)
        copied_plans = []

        for source_plan in source_plans:
            plan, created = SamplePlan.objects.get_or_create(
                experiment=target_experiment,
                sample_type=source_plan.sample_type,
                defaults={
                    'no_per_date': source_plan.no_per_date,
                    'name_no_per_type': source_plan.name_no_per_type,
                }
            )
            copied_plans.append(plan)
            if created:
                self.stdout.write(f'  Created sample plan: {source_plan.sample_type}')

        return copied_plans

    def copy_site(self, source_site, target_experiment):
        site, created = Site.objects.get_or_create(
            experiment=target_experiment,
            site_name=source_site.site_name,
            defaults={
                'habitat_type': source_site.habitat_type,
                'treatment': source_site.treatment,
                'gis_point': source_site.gis_point,
                'country': source_site.country,
                'state_region': source_site.state_region,
                'county_region': source_site.county_region,
                'us_state_county_fips': source_site.us_state_county_fips,
                'longitude': source_site.longitude,
                'latitude': source_site.latitude,
                'archived': source_site.archived,
            }
        )
        if created:
            self.stdout.write(f'Created site: {site.site_name}')
        return site

    def copy_site_visit(self, source_visit, target_site, sample_with_plan=None):
        if sample_with_plan is None:
            sample_with_plan = source_visit.sample_with_plan
        
        visit, created = SiteVisit.objects.get_or_create(
            site=target_site,
            visit_date=source_visit.visit_date,
            defaults={
                'sample_with_plan': sample_with_plan,
                'notes': source_visit.notes,
                'created_by_user': None,
            }
        )
        if not created:
            visit.sample_with_plan = sample_with_plan
            visit.notes = source_visit.notes
            visit.save()
        return visit

    def copy_sample(self, source_sample, target_visit):
        sample = Sample.objects.create(
            site_visit=target_visit,
            sample_type=source_sample.sample_type,
            name_no=source_sample.name_no,
            notes=source_sample.notes,
            completed=source_sample.completed,
            created_by_user=None,
        )

        if source_sample.image:
            try:
                if default_storage.exists(source_sample.image.name):
                    with default_storage.open(source_sample.image.name, 'rb') as f:
                        sample.image.save(
                            source_sample.image.name,
                            ContentFile(f.read()),
                            save=False
                        )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'  Could not copy sample image: {e}')
                )

        if source_sample.image_thumbnail:
            try:
                if default_storage.exists(source_sample.image_thumbnail.name):
                    with default_storage.open(source_sample.image_thumbnail.name, 'rb') as f:
                        sample.image_thumbnail.save(
                            source_sample.image_thumbnail.name,
                            ContentFile(f.read()),
                            save=False
                        )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'  Could not copy sample thumbnail: {e}')
                )

        sample.save()
        return sample

    def copy_specimen(self, source_specimen, target_sample):
        specimen = Specimen.objects.create(
            sample=target_sample,
            classification=source_specimen.classification,
            ai_classification=source_specimen.ai_classification,
            ai_model_name=source_specimen.ai_model_name,
            reviewer_user=source_specimen.reviewer_user,
            created_by_user=None,
            partial_count=source_specimen.partial_count,
            confidence=source_specimen.confidence,
            optional_pred_one=source_specimen.optional_pred_one,
            optional_pred_two=source_specimen.optional_pred_two,
            tags=source_specimen.tags,
            acceptance=source_specimen.acceptance,
            archival_identifier=source_specimen.archival_identifier,
            archival_preservation=source_specimen.archival_preservation,
            archival_stored=source_specimen.archival_stored,
            object_det_train=source_specimen.object_det_train,
        )
        return specimen

    def copy_specimen_images_for_specimen(self, source_specimen, target_specimen):
        source_images = SpecimenImage.objects.filter(specimen=source_specimen)
        copied_count = 0

        for source_image in source_images:
            image = SpecimenImage(
                specimen=target_specimen,
                multispecimen_image_uuid=source_image.multispecimen_image_uuid,
                multispecimen_image_index=source_image.multispecimen_image_index,
                primary_image=source_image.primary_image,
                public_image=source_image.public_image,
                downloaded_image=source_image.downloaded_image,
                image_notfound=source_image.image_notfound,
                uploaded_by_user=source_image.uploaded_by_user,
                image_width=source_image.image_width,
                image_height=source_image.image_height,
                image_thumbnail_large_width=source_image.image_thumbnail_large_width,
                image_thumbnail_large_height=source_image.image_thumbnail_large_height,
                object_det_sent=source_image.object_det_sent,
                object_det_label=source_image.object_det_label,
                object_det_model_version=source_image.object_det_model_version,
                object_det_annotation_id=source_image.object_det_annotation_id,
                object_det_id=source_image.object_det_id,
                object_det_updated_at=source_image.object_det_updated_at,
            )

            main_image_exists = False
            
            source_main_image = getattr(source_image, 'image', None)
            if source_main_image and source_main_image.name:
                try:
                    if default_storage.exists(source_main_image.name):
                        image.image.name = source_main_image.name
                        main_image_exists = True
                        self.stdout.write(f'    Referenced main image: {image.image.name}')
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'  Main image file not found in storage: {source_main_image.name}')
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'  Could not reference main image: {e}')
                    )
            
            for field_name in ['image_thumbnail', 'image_thumbnail_medium', 'image_thumbnail_large']:
                source_field = getattr(source_image, field_name, None)
                if source_field and source_field.name:
                    try:
                        if default_storage.exists(source_field.name):
                            image_field = getattr(image, field_name)
                            image_field.name = source_field.name
                            self.stdout.write(f'    Referenced {field_name}: {image_field.name}')
                        else:
                            self.stdout.write(
                                self.style.WARNING(f'  {field_name} file not found in storage: {source_field.name}')
                            )
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'  Could not reference {field_name}: {e}')
                        )

            if main_image_exists:
                image.save()
                copied_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f'  Skipping specimen image - main image file not found')
                )

        return copied_count

    def copy_multi_specimen_images(self, source_sample, target_sample):
        """Copy MultiSpecimenImage objects associated with the sample."""
        source_multi_images = MultiSpecimenImage.objects.filter(sample=source_sample)
        
        for source_multi in source_multi_images:
            multi_image = MultiSpecimenImage(
                sample=target_sample,
                panorama_filename=source_multi.panorama_filename,
                upload_dir_name=source_multi.upload_dir_name,
                annotations=source_multi.annotations,
                annotations_updated_at=source_multi.annotations_updated_at,
                predictions=source_multi.predictions,
                predictions_timestamp=source_multi.predictions_timestamp,
                image_grid=source_multi.image_grid,
                cropped_to_specimen=source_multi.cropped_to_specimen,
                uploaded_by_user=source_multi.uploaded_by_user,
            )

            multi_image_fields = ['image', 'image_thumbnail', 'label_image', 'label_image_thumbnail']
            for field_name in multi_image_fields:
                source_field = getattr(source_multi, field_name, None)
                if source_field and source_field.name:
                    try:
                        if default_storage.exists(source_field.name):
                            with default_storage.open(source_field.name, 'rb') as f:
                                file_content = f.read()
                                image_field = getattr(multi_image, field_name)
                                filename = source_field.name.split('/')[-1]
                                image_field.save(
                                    filename,
                                    ContentFile(file_content),
                                    save=True
                                )
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'  Could not copy multi-image {field_name}: {e}')
                        )

            if multi_image.image or any(getattr(multi_image, f) for f in ['image_thumbnail', 'label_image', 'label_image_thumbnail'] if getattr(multi_image, f)):
                multi_image.save()
            else:
                self.stdout.write(
                    self.style.WARNING(f'  Skipping multi-specimen image with no image files')
                )

    def copy_timeline_events(self, source_specimen, target_specimen):
        """Copy TimelineEvent objects associated with the specimen."""
        source_events = TimelineEvent.objects.filter(specimen=source_specimen)
        
        for source_event in source_events:
            TimelineEvent.objects.create(
                specimen=target_specimen,
                event_title=source_event.event_title,
                body=source_event.body,
                by_user=None,
            )

