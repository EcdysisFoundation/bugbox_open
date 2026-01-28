"""
import previous years data from the Grower_Archive.xlsx file.
"""
import re
from pathlib import Path

import pandas as pd
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from bugbox3.grower_portal.constants import PHONE_MAX_LENGTH
from bugbox3.grower_portal.models import GrowerProfile, GrowerSampleCodeMapping, SampleCode
from bugbox3.grower_portal.utils import state_name_to_abbreviation
from bugbox3.grower_portal.views.grower.profile import grant_full_grower_permissions

User = get_user_model()


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the CSV/Excel file (Grower_Archive)'
        )
        parser.add_argument(
            '--sheet',
            type=str,
            default='2025',
            help='Sheet name to read from... default 2025'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
        )

    def handle(self, *args, **options):
        file_path = Path(options['file_path'])
        sheet_name = options['sheet']
        dry_run = options['dry_run']

        if not file_path.exists():
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved'))

        stats = {
            'rows_processed': 0,
            'rows_skipped_amish': 0,
            'users_created': 0,
            'users_updated': 0,
            'profiles_created': 0,
            'profiles_updated': 0,
            'sample_codes_created': 0,
            'mappings_created': 0,
            'errors': []
        }

        try:
            self.stdout.write(f'Reading file: {file_path} (sheet: {sheet_name})')
            self.stdout.write('Reading headers from row 2 ...')
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=1)
            self.stdout.write(f'Found {len(df)} rows')

            df.columns = df.columns.str.strip()

            COL = {
                'Email': self._get_exact_column(df.columns, 'Email'),
                'Phone': self._get_exact_column(df.columns, 'Phone'),
                'State/ Province': self._get_exact_column(df.columns, 'State/ Province'),
                'Country': self._get_exact_column(df.columns, 'Country'),
                'County': self._get_exact_column(df.columns, 'County'),
                'City': self._get_exact_column(df.columns, 'City'),
                'Site Code': self._get_exact_column(df.columns, 'Site Code'),
                'Alt Site Code': self._get_exact_column(df.columns, 'Alt Site Code'),
            }

            self.stdout.write(f'Available columns: {", ".join(df.columns.tolist())}\n')

            if COL['Email'] is None:
                self.stdout.write(self.style.ERROR(
                    'ERROR: Column "Email" not found. Check the exact header in your file.'
                ))
                return
            self.stdout.write('Using column: "Email"\n')

            for idx, row in df.iterrows():
                stats['rows_processed'] += 1

                try:
                    row_str = ' '.join([str(val) for val in row.values if pd.notna(val)]).lower()
                    if 'amish' in row_str:
                        stats['rows_skipped_amish'] += 1
                        self.stdout.write(f'  Row {idx + 2}: Skipped (contains "amish")')
                        continue

                    emails_str = str(row.get(COL['Email'], '') or '').strip()
                    if not emails_str or emails_str.lower() in ['nan', 'none', '']:
                        stats['errors'].append(f'Row {idx + 2}: No email provided')
                        continue

                    emails = self._parse_emails(emails_str)
                    if not emails:
                        stats['errors'].append(f'Row {idx + 2}: Could not parse emails from: {emails_str}')
                        continue

                    v = row.get(COL['Phone'], '') if COL['Phone'] else ''
                    is_nan = v is None or (isinstance(v, float) and (v != v)) or str(v).strip().lower() == 'nan'
                    v = '' if is_nan else v
                    phone_raw = str(v).strip() if v else ''

                    state = str(row.get(COL['State/ Province'], '') or '').strip() if COL['State/ Province'] else ''
                    state = state_name_to_abbreviation(state) if state else ''

                    country = str(row.get(COL['Country'], '') or '').strip() if COL['Country'] else ''
                    county = str(row.get(COL['County'], '') or '').strip() if COL['County'] else ''
                    city = str(row.get(COL['City'], '') or '').strip() if COL['City'] else ''

                    site_codes_str = (
                        str(row.get(COL['Site Code'], '') or '').strip() if COL['Site Code'] else ''
                    )
                    alt_site_codes_str = (
                        str(row.get(COL['Alt Site Code'], '') or '').strip()
                        if COL['Alt Site Code'] else ''
                    )

                    for email_idx, email in enumerate(emails):
                        if not self._is_valid_email(email):
                            stats['errors'].append(f'Row {idx + 2}, Email {email_idx + 1}: Invalid email: {email}')
                            continue

                        phone = self._parse_phone_number(phone_raw, None) if phone_raw else ''

                        if dry_run:
                            try:
                                user = User.objects.get(email=email)
                                stats['users_updated'] += 1
                                self.stdout.write(f'  Row {idx + 2}: Would update user: {email}')
                            except User.DoesNotExist:
                                stats['users_created'] += 1
                                self.stdout.write(
                                    f'  Row {idx + 2}: Would create user: {email} '
                                    '(password will be set to unusable - user must reset)'
                                )
                                user = User(email=email, username=email, name='Grower')
                        else:
                            with transaction.atomic():
                                user, user_created = User.objects.get_or_create(
                                    email=email,
                                    defaults={'username': email, 'name': 'Grower'}
                                )
                                if not user_created:
                                    if user.name != 'Grower':
                                        user.name = 'Grower'
                                        user.save()
                                    stats['users_updated'] += 1
                                else:
                                    user.set_unusable_password()
                                    user.save()
                                    stats['users_created'] += 1

                        if dry_run:
                            try:
                                existing_user = User.objects.get(email=user.email)
                                try:
                                    GrowerProfile.objects.get(user=existing_user)
                                    stats['profiles_updated'] += 1
                                except GrowerProfile.DoesNotExist:
                                    stats['profiles_created'] += 1
                            except User.DoesNotExist:
                                stats['profiles_created'] += 1
                        else:
                            profile, profile_created = GrowerProfile.objects.get_or_create(user=user)

                            profile.phone = phone if phone else None
                            if state:
                                profile.state = state
                            if city:
                                profile.city = city
                            if county:
                                profile.county = county
                            if country:
                                profile.country = country
                            profile.save()

                            if profile_created:
                                stats['profiles_created'] += 1
                            else:
                                stats['profiles_updated'] += 1

                            grant_full_grower_permissions(user)

                        if site_codes_str:
                            site_codes = self._parse_codes(site_codes_str)
                            for code in site_codes:
                                if not code:
                                    continue

                                numeric_match = re.search(r'\d+', code)
                                site_code_numeric = int(numeric_match.group()) if numeric_match else None

                                if dry_run:
                                    try:
                                        sample_code = SampleCode.objects.get(code=code)
                                        if sample_code.project_type != 'ignite':
                                            warning_msg = (
                                                f'    WARNING: Sample code {code} already exists '
                                                f'with project_type={sample_code.project_type}, expected ignite'
                                            )
                                            stats['errors'].append(f'Row {idx + 2}: {warning_msg}')
                                            self.stdout.write(self.style.WARNING(warning_msg))
                                    except SampleCode.DoesNotExist:
                                        stats['sample_codes_created'] += 1
                                        self.stdout.write(f'    Would create Ignite sample code: {code}')
                                        sample_code = None
                                else:
                                    try:
                                        sample_code = SampleCode.objects.get(code=code)
                                        if sample_code.project_type != 'ignite':
                                            warning_msg = (
                                                f'Sample code {code} already exists with '
                                                f'project_type={sample_code.project_type}, expected ignite'
                                            )
                                            stats['errors'].append(f'Row {idx + 2}: {warning_msg}')
                                            self.stdout.write(self.style.WARNING(f'    WARNING: {warning_msg}'))
                                    except SampleCode.DoesNotExist:
                                        sample_code = SampleCode.objects.create(
                                            code=code,
                                            project_type='ignite',
                                            site_code_numeric=site_code_numeric,
                                            created_by=user
                                        )
                                        stats['sample_codes_created'] += 1

                                if dry_run:
                                    try:
                                        existing_user = User.objects.get(email=user.email)
                                        try:
                                            GrowerSampleCodeMapping.objects.get(
                                                grower=existing_user, sample_code__code=code
                                            )
                                        except GrowerSampleCodeMapping.DoesNotExist:
                                            stats['mappings_created'] += 1
                                            self.stdout.write(f'    Would create mapping: {user.email} -> {code}')
                                    except User.DoesNotExist:
                                        stats['mappings_created'] += 1
                                        self.stdout.write(f'    Would create mapping: {user.email} -> {code}')
                                else:
                                    mapping, mapping_created = GrowerSampleCodeMapping.objects.get_or_create(
                                        grower=user,
                                        sample_code=sample_code
                                    )
                                    if mapping_created:
                                        stats['mappings_created'] += 1

                        if alt_site_codes_str:
                            alt_site_codes = self._parse_codes(alt_site_codes_str)
                            for code in alt_site_codes:
                                if not code:
                                    continue

                                if dry_run:
                                    try:
                                        sample_code = SampleCode.objects.get(code=code)
                                        if sample_code.project_type != 'avalanche':
                                            warning_msg = (
                                                f'    WARNING: Sample code {code} already exists '
                                                f'with project_type={sample_code.project_type}, expected avalanche'
                                            )
                                            stats['errors'].append(f'Row {idx + 2}: {warning_msg}')
                                            self.stdout.write(self.style.WARNING(warning_msg))
                                    except SampleCode.DoesNotExist:
                                        stats['sample_codes_created'] += 1
                                        self.stdout.write(f'    Would create Avalanche sample code: {code}')
                                        sample_code = None
                                else:
                                    try:
                                        sample_code = SampleCode.objects.get(code=code)
                                        if sample_code.project_type != 'avalanche':
                                            warning_msg = (
                                                f'Sample code {code} already exists with '
                                                f'project_type={sample_code.project_type}, expected avalanche'
                                            )
                                            stats['errors'].append(f'Row {idx + 2}: {warning_msg}')
                                            self.stdout.write(self.style.WARNING(f'    WARNING: {warning_msg}'))
                                    except SampleCode.DoesNotExist:
                                        sample_code = SampleCode.objects.create(
                                            code=code,
                                            project_type='avalanche',
                                            created_by=user
                                        )
                                        stats['sample_codes_created'] += 1

                                if dry_run:
                                    if sample_code is not None:
                                        try:
                                            existing_user = User.objects.get(email=user.email)
                                            try:
                                                GrowerSampleCodeMapping.objects.get(
                                                    grower=existing_user, sample_code__code=code
                                                )
                                            except GrowerSampleCodeMapping.DoesNotExist:
                                                stats['mappings_created'] += 1
                                                self.stdout.write(f'    Would create mapping: {user.email} -> {code}')
                                        except User.DoesNotExist:
                                            stats['mappings_created'] += 1
                                            self.stdout.write(f'    Would create mapping: {user.email} -> {code}')
                                    else:
                                        stats['mappings_created'] += 1
                                        self.stdout.write(f'    Would create mapping: {user.email} -> {code}')
                                else:
                                    mapping, mapping_created = GrowerSampleCodeMapping.objects.get_or_create(
                                        grower=user,
                                        sample_code=sample_code
                                    )
                                    if mapping_created:
                                        stats['mappings_created'] += 1

                except Exception as e:
                    stats['errors'].append(f'Row {idx + 2}: {str(e)}')
                    self.stdout.write(self.style.ERROR(f'  Row {idx + 2}: Error - {str(e)}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading file: {str(e)}'))
            return

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('IMPORT SUMMARY')
        self.stdout.write('=' * 60)
        self.stdout.write(f"Rows processed: {stats['rows_processed']}")
        self.stdout.write(f"Rows skipped (amish): {stats['rows_skipped_amish']}")
        self.stdout.write(f"Users created: {stats['users_created']}")
        self.stdout.write(f"Users updated: {stats['users_updated']}")
        self.stdout.write(f"Profiles created: {stats['profiles_created']}")
        self.stdout.write(f"Profiles updated: {stats['profiles_updated']}")
        self.stdout.write(f"Sample codes created: {stats['sample_codes_created']}")
        self.stdout.write(f"Mappings created: {stats['mappings_created']}")
        self.stdout.write(
            'Imported growers are in the is_grower group and can access grower_portal '
            'after resetting their password.'
        )

        if stats['errors']:
            self.stdout.write(self.style.WARNING(f"\nErrors ({len(stats['errors'])}):"))
            for error in stats['errors'][:10]:
                self.stdout.write(f"  - {error}")
            if len(stats['errors']) > 10:
                self.stdout.write(f"  ... and {len(stats['errors']) - 10} more errors")

        if dry_run:
            self.stdout.write(self.style.WARNING(
                '\nDRY RUN - No changes were saved. Growers would be added to the '
                'is_grower group.'
            ))

    def _get_exact_column(self, columns, exact_name):
        """Return the column whose header exactly matches exact_name."""
        if not exact_name:
            return None
        want = str(exact_name).strip().lower()
        for c in columns:
            if (c or '').strip().lower() == want:
                return c
        return None

    def _parse_emails(self, emails_str):
        """Parse emails from a string"""
        if not emails_str or str(emails_str).lower() in ['nan', 'none', '']:
            return []

        emails = re.split(r'[,;\s]+', str(emails_str))
        emails = [email.strip() for email in emails if email.strip()]
        return emails

    def _parse_codes(self, codes_str):
        """Parse codes from a string"""
        if not codes_str or str(codes_str).lower() in ['nan', 'none', '']:
            return []

        codes = re.split(r'[,;\s]+', str(codes_str))
        codes = [code.strip() for code in codes if code.strip()]
        return codes

    def _parse_phone_number(self, phone_str, grower_name=None):
        """Parse phone number from different formats."""
        if not phone_str:
            return ''

        phone_str = str(phone_str).strip()

        if phone_str.lower() in ['n/a', 'na', 'none', 'nan', '']:
            return ''

        matches = []
        parts = re.split(r'[;/]|,\s*(?=[A-Z])', phone_str)

        for part in parts:
            part = part.strip()
            if not part:
                continue

            if not re.search(r'\d', part):
                continue

            name_phone_match = re.match(r'^([A-Za-z\s]+?)[:]\s*(.+)$', part)
            if name_phone_match:
                name = name_phone_match.group(1).strip()
                phone = name_phone_match.group(2).strip()
                matches.append((name, phone))
                continue

            paren_match = re.match(r'^([A-Za-z\s]+?)\s*\(([^)]+)\)(.+)$', part)
            if paren_match:
                name = paren_match.group(1).strip()
                phone_part1 = paren_match.group(2).strip()
                phone_part2 = paren_match.group(3).strip()
                phone = phone_part1 + phone_part2
                matches.append((name, phone))
                continue

            paren_match2 = re.match(r'^([A-Za-z\s]+?)\s*\(([^)]+)\)$', part)
            if paren_match2:
                name = paren_match2.group(1).strip()
                phone = paren_match2.group(2).strip()
                if re.search(r'\d', phone) and len(re.sub(r'\D', '', phone)) >= 7:
                    matches.append((name, phone))
                    continue

            phone_only = re.sub(r'[^\d\-\(\)\s]', '', part).strip()
            if phone_only and re.search(r'\d', phone_only):
                matches.append((None, phone_only))

        if not matches:
            cleaned = re.sub(r'[^\d\-\(\)\s]', '', phone_str).strip()
            if cleaned and re.search(r'\d', cleaned):
                digits_only = re.sub(r'\D', '', cleaned)
                if len(digits_only) >= 7:
                    matches.append((None, cleaned))

        if not matches:
            return ''

        if grower_name and len(matches) > 1:
            grower_name_lower = grower_name.lower().strip()
            for name, phone in matches:
                if name:
                    name_lower = name.lower().strip()
                    if name_lower in grower_name_lower or grower_name_lower in name_lower:
                        return self._clean_phone_number(phone)

        _, phone = matches[0]
        return self._clean_phone_number(phone)

    def _clean_phone_number(self, phone_str):
        """Format phone number & truncate if too long"""
        if not phone_str:
            return ''

        cleaned = re.sub(r'[^\d\-\(\)\s]', '', str(phone_str))
        cleaned = cleaned.replace('(', '').replace(')', '').replace(' ', '')
        digits_only = re.sub(r'\D', '', cleaned)

        if len(digits_only) < 7:
            return ''

        if len(cleaned) > PHONE_MAX_LENGTH:
            if len(digits_only) > 10:
                digits_only = digits_only[-10:]
            if len(digits_only) == 10:
                cleaned = f"{digits_only[:3]}-{digits_only[3:6]}-{digits_only[6:]}"
            else:
                cleaned = digits_only[:PHONE_MAX_LENGTH]
        else:
            if cleaned.replace('-', '').isdigit() and len(cleaned.replace('-', '')) == 10:
                digits = cleaned.replace('-', '')
                cleaned = f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"

        if len(cleaned) > PHONE_MAX_LENGTH:
            cleaned = cleaned[:PHONE_MAX_LENGTH]

        return cleaned

    def _is_valid_email(self, email):
        """email validation"""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
