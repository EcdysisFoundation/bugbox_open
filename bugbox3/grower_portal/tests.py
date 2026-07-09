from decimal import Decimal

from django.test import SimpleTestCase, TestCase

from bugbox3.grower_portal.constants import (
    AREA_SAMPLED_HA_MAX,
    AREA_UNIT_ACRES,
    AREA_UNIT_HECTARES,
    AVERAGE_WEIGHT_KG_MAX,
    DEPTH_UNIT_CM,
    DEPTH_UNIT_INCHES,
    WEIGHT_UNIT_KG,
    WEIGHT_UNIT_LBS,
)
from bugbox3.grower_portal.forms.grower.forms import GrazingEventAnimalForm
from bugbox3.grower_portal.measurement_capture import (
    capture_area_measurement,
    capture_depth_measurement,
    capture_weight_measurement,
)
from bugbox3.grower_portal.measurement_units import (
    from_cm,
    from_hectares,
    from_kg,
    to_cm,
    to_hectares,
    to_kg,
)


class MeasurementConversionTests(SimpleTestCase):
    def test_acres_hectares_round_trip(self):
        acres = Decimal('10')
        hectares = to_hectares(acres, AREA_UNIT_ACRES)
        self.assertEqual(hectares, Decimal('4.05'))
        round_trip = from_hectares(hectares, AREA_UNIT_ACRES)
        self.assertLessEqual(abs(round_trip - acres), Decimal('0.02'))

    def test_hectares_identity(self):
        value = Decimal('25.5')
        self.assertEqual(to_hectares(value, AREA_UNIT_HECTARES), value)
        self.assertEqual(from_hectares(value, AREA_UNIT_HECTARES), value)

    def test_inches_cm_round_trip(self):
        inches = Decimal('12')
        cm = to_cm(inches, DEPTH_UNIT_INCHES)
        self.assertEqual(cm, Decimal('30.48'))
        self.assertEqual(from_cm(cm, DEPTH_UNIT_INCHES), inches)

    def test_cm_identity(self):
        value = Decimal('15.25')
        self.assertEqual(to_cm(value, DEPTH_UNIT_CM), value)
        self.assertEqual(from_cm(value, DEPTH_UNIT_CM), value)

    def test_lbs_kg_round_trip(self):
        lbs = Decimal('100')
        kg = to_kg(lbs, WEIGHT_UNIT_LBS)
        self.assertEqual(kg, Decimal('45.36'))
        self.assertEqual(from_kg(kg, WEIGHT_UNIT_LBS), lbs)

    def test_kg_identity(self):
        value = Decimal('500')
        self.assertEqual(to_kg(value, WEIGHT_UNIT_KG), value)
        self.assertEqual(from_kg(value, WEIGHT_UNIT_KG), value)


class MeasurementCaptureTests(SimpleTestCase):
    def test_capture_area_measurement_acres_to_hectares(self):
        cleaned = {
            'area_sampled': Decimal('10'),
            'area_sampled_unit': AREA_UNIT_ACRES,
        }
        capture_area_measurement(
            cleaned,
            value_key='area_sampled',
            unit_key='area_sampled_unit',
            entered_key='area_sampled_entered',
            canonical_key='area_sampled_ha',
        )
        self.assertEqual(cleaned['area_sampled_entered'], Decimal('10.00'))
        self.assertEqual(cleaned['area_sampled_ha'], Decimal('4.05'))

    def test_capture_depth_measurement_inches_to_cm(self):
        cleaned = {
            'tillage_depth': Decimal('6'),
            'tillage_depth_unit': DEPTH_UNIT_INCHES,
        }
        capture_depth_measurement(
            cleaned,
            value_key='tillage_depth',
            unit_key='tillage_depth_unit',
            entered_key='tillage_depth_entered',
            canonical_key='tillage_depth_cm',
        )
        self.assertEqual(cleaned['tillage_depth_cm'], Decimal('15.24'))

    def test_capture_weight_measurement_lbs_to_kg(self):
        cleaned = {
            'average_weight': Decimal('1200'),
            'average_weight_unit': WEIGHT_UNIT_LBS,
        }
        capture_weight_measurement(
            cleaned,
            value_key='average_weight',
            unit_key='average_weight_unit',
            entered_key='average_weight_entered',
            canonical_key='average_weight_kg',
        )
        self.assertEqual(cleaned['average_weight_kg'], Decimal('544.31'))


class GrazingEventAnimalFormValidationTests(TestCase):
    def test_average_weight_exceeds_metric_max(self):
        form = GrazingEventAnimalForm(
            data={
                'class_of_animal': 'cow',
                'number_of_animals': 10,
                'average_weight': '6000',
                'average_weight_unit': WEIGHT_UNIT_LBS,
                'duration_days': '5',
                'duration_unit': 'days',
                'rest_period_days': '10',
                'rest_period_unit': 'days',
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('average_weight', form.errors)

    def test_average_weight_within_metric_bounds(self):
        form = GrazingEventAnimalForm(
            data={
                'class_of_animal': 'cow',
                'number_of_animals': 10,
                'average_weight': '1200',
                'average_weight_unit': WEIGHT_UNIT_LBS,
                'duration_days': '5',
                'duration_unit': 'days',
                'rest_period_days': '10',
                'rest_period_unit': 'days',
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertLessEqual(form.cleaned_data['average_weight_kg'], AVERAGE_WEIGHT_KG_MAX)

    def test_area_sampled_ha_bounds_constant(self):
        self.assertLess(AREA_SAMPLED_HA_MAX, Decimal('5000'))
