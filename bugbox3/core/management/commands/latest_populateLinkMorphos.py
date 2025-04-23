import os
import requests
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from bugbox3.taxonomy.models import GBIFImageRecord, Morphospecies

EXCEL_FILE_PATH = os.path.join(settings.BASE_DIR, "bugbox_app", "data", "GBIF_Fetch_List.xlsx")
GBIF_SPECIES_API = "https://api.gbif.org/v1/species/"
GBIF_OCCURRENCE_API = "https://api.gbif.org/v1/occurrence/search"

class Command(BaseCommand):
    help = "Populate GBIFImageRecord table and link/create Morphospecies based on Excel and GBIF API"

    def handle(self, *args, **kwargs):
        entries = self.load_taxon_keys(EXCEL_FILE_PATH)
        if not entries:
            self.stdout.write(self.style.ERROR("[DONE] No taxon keys found in Excel."))
            return

        self.stdout.write(self.style.SUCCESS(f"[DONE] Loaded {len(entries)} entries."))

        # Caching
        existing_urls = set(GBIFImageRecord.objects.values_list("image_url", flat=True))
        morpho_cache = {m.name.lower(): m for m in Morphospecies.objects.all()}
        species_info_cache = {}

        for entry in entries:
            taxon_key = entry["taxon_key"]
            morpho_name = entry["morpho_name"]

            self.stdout.write(self.style.NOTICE(f"📡 Fetching GBIF records for taxonKey: {taxon_key}"))

            params = {
                "taxonKey": taxon_key,
                "mediaType": "StillImage",
                "hasCoordinate": "true",
                "limit": 300
            }

            try:
                response = requests.get(GBIF_OCCURRENCE_API, params=params, timeout=10)
                response.raise_for_status()
                results = response.json().get("results", [])

                for record in results:
                    species_key = record.get("speciesKey")
                    genus_key = record.get("genusKey")

                    for media in record.get("media", []):
                        image_url = media.get("identifier")
                        if not image_url or image_url in existing_urls:
                            continue

                        morpho = None
                        if morpho_name:
                            morpho = morpho_cache.get(morpho_name.lower())
                        else:
                            key = species_key or genus_key or taxon_key
                            if key not in species_info_cache:
                                species_info_cache[key] = self.get_species_info(key)
                            gbif_info = species_info_cache[key]
                            canonical_name = gbif_info.get("canonicalName")

                            if canonical_name:
                                morpho, created = Morphospecies.objects.get_or_create(
                                    name=canonical_name,
                                    defaults={
                                        "gbif_key": key,
                                        "gbif_rank": gbif_info.get("rank", ""),
                                        "gbif_class": gbif_info.get("class", ""),
                                        "gbif_order": gbif_info.get("order", ""),
                                        "gbif_family": gbif_info.get("family", ""),
                                        "gbif_genus": gbif_info.get("genus", ""),
                                        "gbif_species": gbif_info.get("species", ""),
                                        "gbif_canonical_name": canonical_name,
                                        "gbif_scientific_name": gbif_info.get("scientificName", ""),
                                        "decimal_latitude": record.get("decimalLatitude"),
                                        "decimal_longitude": record.get("decimalLongitude"),
                                    }
                                )
                                if not created:
                                    updated = False
                                    if not morpho.gbif_key and key:
                                        morpho.gbif_key = key
                                        updated = True
                                    if not morpho.decimal_latitude and record.get("decimalLatitude"):
                                        morpho.decimal_latitude = record.get("decimalLatitude")
                                        updated = True
                                    if not morpho.decimal_longitude and record.get("decimalLongitude"):
                                        morpho.decimal_longitude = record.get("decimalLongitude")
                                        updated = True
                                    if updated:
                                        morpho.save()
                                        self.stdout.write(self.style.SUCCESS(f"[DONE] Updated morphospecies: {canonical_name}"))

                        GBIFImageRecord.objects.create(
                            gbif_taxon_key=species_key or genus_key or taxon_key,
                            scientific_name=record.get("scientificName"),
                            image_url=image_url,
                            media_type=media.get("type"),
                            license=media.get("license"),
                            morphospecies=morpho,
                            downloaded_image=False
                        )
                        existing_urls.add(image_url)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"[X] Failed for taxonKey {taxon_key}: {e}"))

    def load_taxon_keys(self, file_path):
        try:
            df = pd.read_excel(file_path)
            if "GBIF_taxon_key" not in df.columns or "Morphospecies_if_present" not in df.columns:
                self.stdout.write(self.style.ERROR("Excel must have 'GBIF_taxon_key' and 'Morphospecies_if_present' columns"))
                return []
            df = df.dropna(subset=["GBIF_taxon_key"])
            return [
                {
                    "taxon_key": int(row["GBIF_taxon_key"]),
                    "morpho_name": str(row["Morphospecies_if_present"]).strip() if pd.notna(row["Morphospecies_if_present"]) else ""
                }
                for _, row in df.iterrows()
            ]
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[X] Failed to read Excel file: {e}"))
            return []

    def get_species_info(self, species_key):
        try:
            r = requests.get(f"{GBIF_SPECIES_API}{species_key}", timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception:
            return {}
