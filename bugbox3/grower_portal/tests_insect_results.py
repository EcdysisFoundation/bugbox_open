"""Tests for grower insect results from BugBox samples."""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from organizations.models import Organization

from bugbox3.grower_portal.constants import INSECT_GALLERY_MAX_PER_SITE
from bugbox3.grower_portal.models import GrowerSampleCodeMapping, SampleCode
from bugbox3.grower_portal.services.insect_display import display_family_for_grower
from bugbox3.grower_portal.services.insect_results import (
    build_insect_results_context,
    get_insect_available_years,
    grower_has_insect_data,
    group_gallery_images_by_site,
    select_gallery_images,
)
from bugbox3.grower_portal.services.insect_taxonomy import resolve_grower_taxonomy
from bugbox3.samples.export_metrics import (
    UNSPECIFIED_FAMILY,
    compute_sample_morpho_counts,
    richness_taxon_names,
)
from bugbox3.samples.models import (
    Experiment,
    Sample,
    Site,
    SiteVisit,
    Specimen,
    SpecimenImage,
)
from bugbox3.taxonomy.models import Morphospecies

User = get_user_model()

MINI_PNG = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00'
    b'\x01\x01\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
)


def _mini_image(name='test.png'):
    return SimpleUploadedFile(name, MINI_PNG, content_type='image/png')


def _add_grower_permission(user):
    ct = ContentType.objects.get(app_label='grower_portal', model='growerprofile')
    perm = Permission.objects.get(content_type=ct, codename='view_growerprofile')
    user.user_permissions.add(perm)


def _hierarchy_group(site_group, class_label, group_label):
    for class_node in site_group['classes']:
        if class_node['class_label'] == class_label:
            for group_node in class_node['groups']:
                if group_node['group_label'] == group_label:
                    return group_node
    return None


def _hierarchy_family_labels(site_group):
    labels = []
    for class_node in site_group['classes']:
        for group_node in class_node['groups']:
            for family_row in group_node['families']:
                labels.append(family_row['family'])
    return labels


class InsectResultsFixtureMixin:
    @classmethod
    def _create_bugbox_site(cls, site_name, visit_date, experiment=None):
        if experiment is None:
            experiment = cls.experiment
        site = Site.objects.create(
            experiment=experiment,
            site_name=site_name,
            habitat_type='field',
            treatment='control',
        )
        visit = SiteVisit.objects.create(site=site, visit_date=visit_date)
        sample = Sample.objects.create(
            site_visit=visit,
            sample_type='pitfall',
            name_no='1',
            completed=True,
        )
        return site, visit, sample

    @classmethod
    def _create_specimen_image(cls, specimen):
        return SpecimenImage.objects.create(
            specimen=specimen,
            image=_mini_image('full.png'),
            image_thumbnail_medium=_mini_image('medium.png'),
        )

    @classmethod
    def _create_specimen(cls, sample, morpho, *, confidence=None, human=True):
        kwargs = {
            'sample': sample,
            'partial_count': 0,
        }
        if human:
            kwargs['classification'] = morpho
            kwargs['confidence'] = confidence if confidence is not None else Decimal('50')
        else:
            kwargs['ai_classification'] = morpho
            kwargs['confidence'] = confidence if confidence is not None else Decimal('80')
        return Specimen.objects.create(**kwargs)

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user('admin', 'admin@test.com', 'pass')
        cls.grower = User.objects.create_user('grower', 'grower@test.com', 'pass')
        cls.other = User.objects.create_user('other', 'other@test.com', 'pass')
        _add_grower_permission(cls.grower)

        cls.org = Organization.objects.create(name='Test Org', slug='test-org-insects')
        cls.org.add_user(cls.admin, is_admin=True)

        cls.experiment = Experiment.objects.create(
            organization=cls.org,
            name='Grower Insect Test Exp',
            abbreviation='git',
            from_year=2025,
            to_year=2025,
            leader='Tester',
            no_sites=1,
            date_per_site=1,
        )

        cls.morpho_carab = Morphospecies.objects.create(
            name='TestCarab001',
            gbif_class='Insecta',
            gbif_family='Carabidae',
            gbif_order='Coleoptera',
        )
        cls.morpho_staph = Morphospecies.objects.create(
            name='TestStaph001',
            gbif_class='Insecta',
            gbif_family='Staphylinidae',
            gbif_order='Coleoptera',
        )

        cls.sample_code = SampleCode.objects.create(
            code='9001',
            project_type='avalanche',
            year=2025,
            created_by=cls.admin,
        )
        GrowerSampleCodeMapping.objects.create(
            grower=cls.grower,
            sample_code=cls.sample_code,
            year_sampled=2025,
        )

        cls.site, cls.visit, cls.sample = cls._create_bugbox_site('9001', date(2025, 6, 15))
        cls._create_specimen(cls.sample, cls.morpho_carab)
        cls._create_specimen(cls.sample, cls.morpho_carab)
        cls._create_specimen(cls.sample, cls.morpho_staph)

        cls.other_code = SampleCode.objects.create(
            code='9002',
            project_type='avalanche',
            year=2025,
            created_by=cls.admin,
        )
        GrowerSampleCodeMapping.objects.create(
            grower=cls.grower,
            sample_code=cls.other_code,
            year_sampled=2025,
        )
        cls.other_site, cls.other_visit, cls.other_sample = cls._create_bugbox_site('9002', date(2024, 6, 1))


class InsectResultsScopingTests(InsectResultsFixtureMixin, TestCase):
    def test_grower_sees_only_mapped_site_codes(self):
        ctx = build_insect_results_context(self.grower, 2025)
        site_codes = {row['site_code'] for row in ctx['summary_by_site'] if row['has_bugbox_data']}
        self.assertEqual(site_codes, {'9001'})

    def test_other_grower_does_not_see_sites(self):
        ctx = build_insect_results_context(self.other, 2025)
        self.assertEqual(ctx['summary_combined']['site_count'], 0)

    def test_year_filter_excludes_other_years(self):
        ctx = build_insect_results_context(self.grower, 2024)
        site_codes = {row['site_code'] for row in ctx['summary_by_site'] if row['has_bugbox_data']}
        self.assertEqual(site_codes, {'9002'})


class InsectResultsMetricsTests(InsectResultsFixtureMixin, TestCase):
    def test_abundance_counts_every_specimen_row(self):
        raw_abundance = sum(
            1 + (s.partial_count or 0) for s in self.sample.specimen_set.all()
        )
        ctx = build_insect_results_context(self.grower, 2025)
        site_row = next(r for r in ctx['summary_by_site'] if r['site_code'] == '9001')
        self.assertEqual(site_row['abundance_total'], raw_abundance)

    def test_richness_uses_export_exclusions(self):
        morpho_metrics = compute_sample_morpho_counts(self.sample, level='morphospecies')
        ctx = build_insect_results_context(self.grower, 2025)
        site_row = next(r for r in ctx['summary_by_site'] if r['site_code'] == '9001')
        self.assertEqual(site_row['species_richness'], len(richness_taxon_names(morpho_metrics)))
        self.assertEqual(site_row['species_richness'], morpho_metrics['species_richness'])

    def test_human_skip_morpho_included_in_abundance_excluded_from_richness(self):
        morpho_thrips = Morphospecies.objects.create(
            name='ThysanopteraTest4291',
            gbif_class='Insecta',
            gbif_order='Thysanoptera',
        )
        self._create_specimen(self.sample, morpho_thrips, human=True)
        export_metrics = compute_sample_morpho_counts(self.sample, level='morphospecies')
        raw_abundance = sum(
            1 + (s.partial_count or 0) for s in self.sample.specimen_set.all()
        )
        ctx = build_insect_results_context(self.grower, 2025)
        site_row = next(r for r in ctx['summary_by_site'] if r['site_code'] == '9001')
        self.assertEqual(site_row['abundance_total'], raw_abundance)
        self.assertEqual(export_metrics['abundance'], raw_abundance - 1)
        self.assertNotIn('ThysanopteraTest4291', richness_taxon_names(export_metrics))
        self.assertEqual(site_row['species_richness'], len(richness_taxon_names(export_metrics)))

    def test_combined_species_richness_is_union_not_sum(self):
        ctx = build_insect_results_context(self.grower, 2025)
        self.assertEqual(ctx['summary_combined']['species_richness'], 2)
        self.assertEqual(ctx['summary_combined']['abundance_total'], 3)

    def test_species_richness_can_exceed_family_row_count(self):
        """Many morphospecies can sit under one display family (e.g. Carabidae)."""
        ctx = build_insect_results_context(self.grower, 2025)
        site_row = next(r for r in ctx['summary_by_site'] if r['site_code'] == '9001')
        family_rows = [r for r in ctx['families_by_site'] if r['site_code'] == '9001']
        self.assertEqual(len(family_rows), 2)
        self.assertEqual(site_row['species_richness'], 2)

    def test_families_table_sorted_by_count_desc(self):
        ctx = build_insect_results_context(self.grower, 2025)
        families = ctx['families_by_site']
        self.assertEqual(len(families), 2)
        self.assertEqual(families[0]['family'], 'Carabidae')
        self.assertEqual(families[0]['total_count'], 2)

    def test_families_grouped_by_site(self):
        ctx = build_insect_results_context(self.grower, 2025)
        grouped = ctx['families_grouped_by_site']
        self.assertEqual(len(grouped), 1)
        self.assertEqual(grouped[0]['site_code'], '9001')
        self.assertEqual(grouped[0]['family_count'], 2)
        coleoptera = _hierarchy_group(grouped[0], 'Insecta', 'Coleoptera')
        self.assertIsNotNone(coleoptera)
        self.assertEqual(coleoptera['group_rank'], 'order')
        self.assertEqual(coleoptera['families'][0]['family'], 'Carabidae')
        self.assertEqual(coleoptera['families'][0]['total_count'], 2)

    def test_two_visits_same_code_same_year_merge(self):
        _, _visit2, sample2 = self._create_bugbox_site('9001', date(2025, 6, 16))
        self._create_specimen(sample2, self.morpho_carab)
        ctx = build_insect_results_context(self.grower, 2025)
        site_rows = [r for r in ctx['summary_by_site'] if r['site_code'] == '9001']
        self.assertEqual(len(site_rows), 1)
        self.assertEqual(site_rows[0]['abundance_total'], 4)
        self.assertIn('2 visits', site_rows[0]['visit_dates_hint'])


class InsectResultsFallbackTests(InsectResultsFixtureMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.fallback_code = SampleCode.objects.create(
            code='9010',
            project_type='avalanche',
            year=2025,
            created_by=cls.admin,
        )
        GrowerSampleCodeMapping.objects.create(
            grower=cls.grower,
            sample_code=cls.fallback_code,
            year_sampled=2025,
        )

    def test_fallback_code_without_visit_shows_empty_metrics(self):
        ctx = build_insect_results_context(self.grower, 2025)
        row = next(r for r in ctx['summary_by_site'] if r['site_code'] == '9010')
        self.assertFalse(row['has_bugbox_data'])
        self.assertIsNone(row['abundance_total'])
        self.assertIsNone(row['species_richness'])

    def test_available_years_includes_fallback_mapping(self):
        years = get_insect_available_years(self.grower)
        self.assertIn(2025, years)
        self.assertIn(2024, years)


class GallerySelectionTests(InsectResultsFixtureMixin, TestCase):
    def test_round_robin_respects_per_site_cap(self):
        pools = {
            f'Family{i}': [{'url': f'u{i}{j}', 'family': f'Family{i}', 'site_code': '9001'} for j in range(5)]
            for i in range(15)
        }
        order = [f'Family{i}' for i in range(15)]
        selected = select_gallery_images(pools, order, max_total=INSECT_GALLERY_MAX_PER_SITE)
        self.assertEqual(len(selected), INSECT_GALLERY_MAX_PER_SITE)
        counts = {}
        for item in selected:
            counts[item['family']] = counts.get(item['family'], 0) + 1
        self.assertEqual(len(counts), 12)
        self.assertTrue(all(c == 1 for c in counts.values()))

    def test_single_family_can_fill_site_cap(self):
        pools = {
            'Carabidae': [
                {'url': f'u{j}', 'family': 'Carabidae', 'site_code': '9001'} for j in range(20)
            ],
        }
        selected = select_gallery_images(pools, ['Carabidae'])
        self.assertEqual(len(selected), INSECT_GALLERY_MAX_PER_SITE)
        self.assertTrue(all(item['family'] == 'Carabidae' for item in selected))

    def test_two_families_fill_site_cap_with_round_robin(self):
        pools = {
            'Carabidae': [{'url': f'c{j}', 'family': 'Carabidae', 'site_code': '9001'} for j in range(10)],
            'Staphylinidae': [{'url': f's{j}', 'family': 'Staphylinidae', 'site_code': '9001'} for j in range(10)],
        }
        selected = select_gallery_images(pools, ['Carabidae', 'Staphylinidae'])
        self.assertEqual(len(selected), INSECT_GALLERY_MAX_PER_SITE)
        counts = {f: sum(1 for i in selected if i['family'] == f) for f in pools}
        self.assertEqual(counts['Carabidae'], 6)
        self.assertEqual(counts['Staphylinidae'], 6)

    def test_each_site_gets_independent_gallery_cap(self):
        order = [f'F{i}' for i in range(10)]
        pools_a = {
            f'F{i}': [{'url': f'a{i}{j}', 'family': f'F{i}', 'site_code': '9001'} for j in range(5)]
            for i in range(10)
        }
        pools_b = {
            f'F{i}': [{'url': f'b{i}{j}', 'family': f'F{i}', 'site_code': '9002'} for j in range(5)]
            for i in range(10)
        }
        site_a = select_gallery_images(pools_a, order, max_total=INSECT_GALLERY_MAX_PER_SITE)
        site_b = select_gallery_images(pools_b, order, max_total=INSECT_GALLERY_MAX_PER_SITE)
        self.assertEqual(len(site_a), INSECT_GALLERY_MAX_PER_SITE)
        self.assertEqual(len(site_b), INSECT_GALLERY_MAX_PER_SITE)
        self.assertTrue(all(img['site_code'] == '9001' for img in site_a))
        self.assertTrue(all(img['site_code'] == '9002' for img in site_b))

    def test_gallery_excludes_ai_only_below_ai_floor(self):
        specimen = self._create_specimen(
            self.sample,
            self.morpho_carab,
            human=False,
            confidence=Decimal('4'),
        )
        self._create_specimen_image(specimen)
        eligible = self._create_specimen(
            self.sample,
            self.morpho_staph,
            human=False,
            confidence=Decimal('85'),
        )
        self._create_specimen_image(eligible)
        ctx = build_insect_results_context(self.grower, 2025)
        families_in_gallery = {img['family'] for img in ctx['gallery_images']}
        self.assertIn('Staphylinidae', families_in_gallery)
        self.assertNotIn('Carabidae', families_in_gallery)

    def test_human_reviewed_included_below_ai_floor(self):
        specimen = self._create_specimen(self.sample, self.morpho_carab, human=True)
        self._create_specimen_image(specimen)
        ctx = build_insect_results_context(self.grower, 2025)
        families_in_gallery = {img['family'] for img in ctx['gallery_images']}
        self.assertIn('Carabidae', families_in_gallery)

    def test_human_reviewed_included_when_confidence_meets_threshold(self):
        specimen = self._create_specimen(
            self.sample,
            self.morpho_carab,
            human=True,
            confidence=Decimal('85'),
        )
        self._create_specimen_image(specimen)
        ctx = build_insect_results_context(self.grower, 2025)
        families_in_gallery = {img['family'] for img in ctx['gallery_images']}
        self.assertIn('Carabidae', families_in_gallery)

    def test_gallery_prefers_human_reviewed_over_ai_in_pick_order(self):
        from bugbox3.libs.utilities import get_media_url

        ai_specimen = self._create_specimen(
            self.sample,
            self.morpho_carab,
            human=False,
            confidence=Decimal('95'),
        )
        ai_image = self._create_specimen_image(ai_specimen)
        human_specimen = self._create_specimen(
            self.sample,
            self.morpho_carab,
            human=True,
            confidence=Decimal('85'),
        )
        human_image = self._create_specimen_image(human_specimen)
        ctx = build_insect_results_context(self.grower, 2025)
        carab_urls = [img['url'] for img in ctx['gallery_images'] if img['family'] == 'Carabidae']
        human_url = get_media_url(human_image.image_thumbnail_medium, human_image.public_image)
        ai_url = get_media_url(ai_image.image_thumbnail_medium, ai_image.public_image)
        self.assertGreaterEqual(len(carab_urls), 2)
        self.assertEqual(carab_urls[0], human_url)
        self.assertIn(ai_url, carab_urls[1:])

    def test_gallery_prefers_higher_confidence_ai_within_family(self):
        from bugbox3.libs.utilities import get_media_url

        low_ai = self._create_specimen(
            self.sample,
            self.morpho_carab,
            human=False,
            confidence=Decimal('60'),
        )
        low_image = self._create_specimen_image(low_ai)
        high_ai = self._create_specimen(
            self.sample,
            self.morpho_carab,
            human=False,
            confidence=Decimal('95'),
        )
        high_image = self._create_specimen_image(high_ai)
        ctx = build_insect_results_context(self.grower, 2025)
        carab_urls = [img['url'] for img in ctx['gallery_images'] if img['family'] == 'Carabidae']
        high_url = get_media_url(high_image.image_thumbnail_medium, high_image.public_image)
        low_url = get_media_url(low_image.image_thumbnail_medium, low_image.public_image)
        self.assertGreaterEqual(len(carab_urls), 2)
        self.assertEqual(carab_urls[0], high_url)
        self.assertIn(low_url, carab_urls[1:])

    def test_families_without_images_not_in_gallery(self):
        ctx = build_insect_results_context(self.grower, 2025)
        self.assertEqual(ctx['gallery_images'], [])
        self.assertEqual(ctx['gallery_grouped_by_site'], [])

    def test_gallery_grouped_by_site_preserves_images(self):
        specimen = self._create_specimen(
            self.sample,
            self.morpho_staph,
            human=True,
            confidence=Decimal('85'),
        )
        self._create_specimen_image(specimen)
        ctx = build_insect_results_context(self.grower, 2025)
        flat = ctx['gallery_images']
        grouped = ctx['gallery_grouped_by_site']
        self.assertEqual(sum(len(g['images']) for g in grouped), len(flat))
        self.assertEqual(grouped[0]['site_code'], '9001')
        self.assertEqual(grouped[0]['images'][0]['family'], 'Staphylinidae')

    def test_group_gallery_images_by_site_helper(self):
        images = [
            {'site_code': '9002', 'family': 'A'},
            {'site_code': '9001', 'family': 'B'},
            {'site_code': '9002', 'family': 'C'},
        ]
        grouped = group_gallery_images_by_site(images)
        self.assertEqual([g['site_code'] for g in grouped], ['9002', '9001'])
        self.assertEqual([img['family'] for img in grouped[0]['images']], ['A', 'C'])

    def test_grower_has_insect_data(self):
        self.assertTrue(grower_has_insect_data(self.grower, 2025))
        self.assertFalse(grower_has_insect_data(self.other, 2025))


class GrowerFamilyDisplayTests(InsectResultsFixtureMixin, TestCase):
    def test_display_family_aliases_for_blank_gbif_family(self):
        morpho_acari, _ = Morphospecies.objects.get_or_create(
            name='Acari',
            defaults={'gbif_family': '', 'gbif_class': 'Arachnida'},
        )
        morpho_arach, _ = Morphospecies.objects.get_or_create(
            name='Arachnida',
            defaults={'gbif_family': '', 'gbif_class': 'Arachnida'},
        )
        morpho_worm, _ = Morphospecies.objects.get_or_create(
            name='Earthworms',
            defaults={'gbif_family': '', 'gbif_order': 'Opisthopora', 'gbif_class': 'Clitellata'},
        )
        self.assertEqual(display_family_for_grower(morpho_acari), 'Mites')
        self.assertEqual(display_family_for_grower(morpho_arach), 'Unidentified arachnids')
        self.assertEqual(display_family_for_grower(morpho_worm), 'Earthworms')

    def test_grower_counts_use_display_labels_not_unspecified(self):
        morpho_acari, _ = Morphospecies.objects.get_or_create(
            name='Acari',
            defaults={'gbif_family': '', 'gbif_class': 'Arachnida'},
        )
        self._create_specimen(self.sample, morpho_acari, human=True)
        metrics_grower = compute_sample_morpho_counts(
            self.sample,
            level='family',
            family_name_fn=display_family_for_grower,
        )
        metrics_export = compute_sample_morpho_counts(self.sample, level='family')
        metrics_morpho = compute_sample_morpho_counts(self.sample, level='morphospecies')
        self.assertIn('Mites', metrics_grower['taxon_counts'])
        self.assertNotIn(UNSPECIFIED_FAMILY, metrics_grower['taxon_counts'])
        self.assertIn(UNSPECIFIED_FAMILY, metrics_export['taxon_counts'])
        self.assertIn('Acari', richness_taxon_names(metrics_morpho))

    def test_mites_and_arachnida_morphos_separate_family_labels(self):
        morpho_acari, _ = Morphospecies.objects.get_or_create(
            name='Acari',
            defaults={'gbif_family': '', 'gbif_class': 'Arachnida'},
        )
        morpho_arach, _ = Morphospecies.objects.get_or_create(
            name='Arachnida',
            defaults={'gbif_family': '', 'gbif_class': 'Arachnida'},
        )
        self._create_specimen(self.sample, morpho_acari, human=True)
        self._create_specimen(self.sample, morpho_arach, human=True)
        ctx = build_insect_results_context(self.grower, 2025)
        site_row = next(r for r in ctx['summary_by_site'] if r['site_code'] == '9001')
        family_labels = {
            r['family']: r['total_count']
            for r in ctx['families_by_site']
            if r['site_code'] == '9001'
        }
        self.assertEqual(family_labels.get('Mites'), 1)
        self.assertEqual(family_labels.get('Unidentified arachnids'), 1)
        self.assertGreaterEqual(site_row['species_richness'], 2)

        grouped = ctx['families_grouped_by_site'][0]
        acari_group = _hierarchy_group(grouped, 'Arachnida', 'Acari')
        self.assertIsNotNone(acari_group)
        self.assertEqual(acari_group['group_rank'], 'subclass')
        self.assertEqual(acari_group['families'][0]['family'], 'Mites')
        unid_group = _hierarchy_group(grouped, 'Arachnida', 'Unspecified order')
        self.assertIsNotNone(unid_group)
        self.assertEqual(unid_group['families'][0]['family'], 'Unidentified arachnids')

    def test_unknown_morpho_name_uses_other_fallback(self):
        morpho = Morphospecies.objects.create(name='TestUnknownMorpho999', gbif_family='')
        self.assertEqual(display_family_for_grower(morpho), 'Other')


class ExportMetricsTests(InsectResultsFixtureMixin, TestCase):
    def test_family_level_counts(self):
        metrics = compute_sample_morpho_counts(self.sample, level='family')
        self.assertEqual(metrics['abundance'], 3)
        self.assertEqual(metrics['species_richness'], 2)
        self.assertEqual(metrics['taxon_counts']['Carabidae'], 2)
        self.assertEqual(metrics['taxon_counts']['Staphylinidae'], 1)


class InsectTaxonomyHierarchyTests(InsectResultsFixtureMixin, TestCase):
    def test_resolve_acari_morpho_subclass_placement(self):
        morpho, _ = Morphospecies.objects.get_or_create(
            name='Acari',
            defaults={'gbif_family': '', 'gbif_class': 'Arachnida'},
        )
        placement = resolve_grower_taxonomy(morpho)
        self.assertEqual(placement.class_label, 'Arachnida')
        self.assertEqual(placement.group_label, 'Acari')
        self.assertEqual(placement.group_rank, 'subclass')
        self.assertEqual(placement.family_label, 'Mites')

    def test_resolve_mite_family_under_subclass_acari(self):
        morpho = Morphospecies.objects.create(
            name='TestAcaridae001',
            gbif_class='Arachnida',
            gbif_order='Astigmata',
            gbif_family='Acaridae',
        )
        placement = resolve_grower_taxonomy(morpho)
        self.assertEqual(placement.group_label, 'Acari')
        self.assertEqual(placement.group_rank, 'subclass')
        self.assertEqual(placement.family_label, 'Acaridae')

    def test_resolve_arachnida_morpho_not_under_subclass_acari(self):
        morpho, _ = Morphospecies.objects.get_or_create(
            name='Arachnida',
            defaults={'gbif_family': '', 'gbif_class': 'Arachnida'},
        )
        placement = resolve_grower_taxonomy(morpho)
        self.assertEqual(placement.group_label, 'Unspecified order')
        self.assertEqual(placement.group_rank, 'order')
        self.assertEqual(placement.family_label, 'Unidentified arachnids')

    def test_hierarchy_leaf_counts_match_flat_family_totals(self):
        ctx = build_insect_results_context(self.grower, 2025)
        site_row = next(r for r in ctx['summary_by_site'] if r['site_code'] == '9001')
        flat_total = sum(r['total_count'] for r in ctx['families_by_site'] if r['site_code'] == '9001')
        grouped = ctx['families_grouped_by_site'][0]
        hierarchy_total = sum(
            family_row['total_count']
            for class_node in grouped['classes']
            for group_node in class_node['groups']
            for family_row in group_node['families']
        )
        self.assertEqual(hierarchy_total, flat_total)
        self.assertEqual(hierarchy_total, site_row['abundance_total'])

    def test_acari_morpho_and_mite_family_share_subclass_group(self):
        morpho_acari, _ = Morphospecies.objects.get_or_create(
            name='Acari',
            defaults={'gbif_family': '', 'gbif_class': 'Arachnida'},
        )
        morpho_mite = Morphospecies.objects.create(
            name='TestAcaridaeHierarchy',
            gbif_class='Arachnida',
            gbif_order='Astigmata',
            gbif_family='Acaridae',
        )
        self._create_specimen(self.sample, morpho_acari, human=True)
        self._create_specimen(self.sample, morpho_mite, human=True)
        ctx = build_insect_results_context(self.grower, 2025)
        grouped = ctx['families_grouped_by_site'][0]
        acari_group = _hierarchy_group(grouped, 'Arachnida', 'Acari')
        self.assertIsNotNone(acari_group)
        families = {row['family']: row['total_count'] for row in acari_group['families']}
        self.assertEqual(families.get('Mites'), 1)
        self.assertEqual(families.get('Acaridae'), 1)

    def test_blank_gbif_class_uses_unspecified_class(self):
        morpho = Morphospecies.objects.create(name='TestNoClassMorpho', gbif_family='SomeFamily')
        placement = resolve_grower_taxonomy(morpho)
        self.assertEqual(placement.class_label, 'Unspecified class')
