import os
import shutil
from pathlib import Path
import requests
from concurrent.futures import ThreadPoolExecutor

from django.core.management.base import BaseCommand
from bugbox3.taxonomy.models import Morphospecies, GBIFImageRecord
from bugbox3.samples.models import SpecimenImage
from bugbox3.samples.constants import ACCEPTANCE_PENDING


class Command(BaseCommand):
    help = (
        "Build a training dataset by collecting Ecdysis and GBIF images for morphospecies "
        "with gbif_rank == 'SPECIES'. Stores them in ecdysis_images/ and gbif_images/ folders."
        "You can run this command with the following command:\n"
        "docker compose -f local.yml run django python manage.py buildTrainingGBIF --output-dir /app/media/"
    )

    MIN_IMAGES = 40
    MAX_IMAGES = 500

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            required=True,
            help="Output directory to store ecdysis_images/ and gbif_images/"
        )

    def handle(self, *args, **options):
        output_dir = Path(options['output_dir'])
        ecdysis_dir = output_dir / 'ecdysis_images'
        gbif_dir = output_dir / 'gbif_images'

        ecdysis_dir.mkdir(parents=True, exist_ok=True)
        gbif_dir.mkdir(parents=True, exist_ok=True)

        species_morphos = Morphospecies.objects.filter(gbif_rank__iexact="species")

        total_processed = 0

        for morpho in species_morphos:
            self.stdout.write(f"[+] Checking Morphospecies: {morpho.name} (ID: {morpho.id})")

            ecdysis_images = SpecimenImage.objects.filter(
                specimen__classification_id=morpho.id,
                downloaded_image=True
            ).exclude(
                specimen__acceptance=ACCEPTANCE_PENDING
            ).order_by('-id')

            ecdysis_count = ecdysis_images.count()

            gbif_images = GBIFImageRecord.objects.filter(
                morphospecies=morpho,
                
            ).order_by('-id')

            gbif_count = gbif_images.count()

            total_available = min(ecdysis_count, gbif_count) * 2

            if ecdysis_count > 0 and gbif_count > 0 and (ecdysis_count + gbif_count) >= self.MIN_IMAGES:
                total_to_use = min(total_available, self.MAX_IMAGES)
                per_source = total_to_use // 2
                ecdysis_images = ecdysis_images[:per_source]
                gbif_images = gbif_images[:per_source]

                total_processed += 1
                self.stdout.write(self.style.SUCCESS(
                    f"Using {per_source * 2} images for {morpho.name} — {per_source} from Ecdysis, {per_source} from GBIF"
                ))

                for img in ecdysis_images:
                    try:
                        filename = os.path.basename(img.image.name)
                        dest_path = ecdysis_dir / f"{morpho.name}_{filename}"
                        if not dest_path.exists():
                            response = requests.get(img.image.url, timeout=10)
                            response.raise_for_status()
                            with open(dest_path, 'wb') as f:
                                f.write(response.content)

                    except Exception as e:
                        self.stderr.write(f"[Ecdysis ERROR] {morpho.name}: {e}")
                
                downloaded_gbif = []

                def download_gbif_image(gbif_img, idx):
                    try:
                        filename = f"{morpho.name}_gbif_{idx}.jpg"
                        dest_path = gbif_dir / filename
                        if not dest_path.exists():
                            response = requests.get(gbif_img.image_url, timeout=10)
                            response.raise_for_status()
                            with open(dest_path, 'wb') as f:
                                f.write(response.content)
                        gbif_img.downloaded_image = True
                        downloaded_gbif.append(gbif_img)
                    except Exception as e:
                        print(f"[GBIF ERROR] {gbif_img.image_url}: {e}")
                with ThreadPoolExecutor(max_workers=10) as executor:
                    for idx, gbif_img in enumerate(gbif_images):
                        executor.submit(download_gbif_image, gbif_img, idx)

                if downloaded_gbif:
                    GBIFImageRecord.objects.bulk_update(downloaded_gbif, ['downloaded_image'])


            else:
                self.stdout.write(self.style.WARNING(
                    f"[X] Skipping {morpho.name}: {ecdysis_count} Ecdysis, {gbif_count} GBIF"
                ))
        self.stdout.write(self.style.SUCCESS(f"\n[DONE] Total Morphospecies processed: {total_processed}"))
