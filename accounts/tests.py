"""
Comprehensive automated test suite for CRPify Patient Healthcare Portal.
Validates authentication, the five primary sections, bookings, authorization, and security.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from datetime import timedelta
from consultations.models import Doctor, Consultation
from blood_collection.models import BloodCollectionBooking
from reports.models import MedicalReport

UserModel = get_user_model()


class UrlResolutionTests(TestCase):
    """Requirement: All five primary section named URL patterns resolve correctly."""

    def test_five_primary_portal_routes_resolve(self):
        # Exactly five primary sections
        self.assertEqual(reverse('dashboard:home'), '/dashboard/')
        self.assertEqual(reverse('consultations:list'), '/consultation/')
        self.assertEqual(reverse('blood_collection:list'), '/blood-collection/')
        self.assertEqual(reverse('reports:list'), '/reports/')
        self.assertEqual(reverse('history'), '/history/')

        # Direct shortcuts
        self.assertEqual(reverse('dashboard_direct'), '/dashboard/')
        self.assertEqual(reverse('consultation_direct'), '/consultation/')
        self.assertEqual(reverse('blood_collection_direct'), '/blood-collection/')
        self.assertEqual(reverse('reports_direct'), '/reports/')
        self.assertEqual(reverse('history'), '/history/')

    def test_auth_and_root_urls_resolve(self):
        self.assertEqual(reverse('root'), '/')
        self.assertEqual(reverse('accounts:login'), '/login/')
        self.assertEqual(reverse('accounts:signup'), '/signup/')
        self.assertEqual(reverse('accounts:logout'), '/logout/')


class PortalAccessGuardsTests(TestCase):
    """Requirement: Unauthenticated users are redirected to login for all portal sections."""

    def setUp(self):
        self.client = Client()

    def test_unauthenticated_redirects_on_all_five_sections(self):
        sections = [
            (reverse('dashboard:home'), '/dashboard/'),
            (reverse('consultations:list'), '/consultation/'),
            (reverse('blood_collection:list'), '/blood-collection/'),
            (reverse('reports:list'), '/reports/'),
            (reverse('history'), '/history/'),
        ]
        for url, path in sections:
            response = self.client.get(url)
            self.assertRedirects(response, f"/login/?next={path}")

    def test_root_redirects_guest_to_login(self):
        response = self.client.get(reverse('root'))
        self.assertRedirects(response, reverse('accounts:login'))


class PatientPortalRenderingTests(TestCase):
    """Requirement: All five primary sections render successfully with correct active state."""

    def setUp(self):
        self.client = Client()
        self.patient = UserModel.objects.create_user(
            username='jane_doe',
            email='jane@example.com',
            password='SecurePassword2026!',
            first_name='Jane',
            last_name='Doe'
        )
        self.client.force_login(self.patient)

    def test_section_one_home_renders(self):
        """Section 1: Home (/dashboard/)"""
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/home.html')
        self.assertContains(response, 'Welcome back, Jane Doe!')
        self.assertContains(response, 'CRPify')
        self.assertContains(response, 'C-reactive protein (CRP) is a biomarker associated with inflammation.')
        self.assertContains(response, 'Doctor Consultation')
        self.assertContains(response, 'Blood Collection')
        self.assertContains(response, 'Reports')
        self.assertContains(response, 'History')

    def test_section_two_consultation_renders(self):
        """Section 2: Doctor Consultation (/consultation/)"""
        response = self.client.get(reverse('consultations:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'consultations/consultation_list.html')
        self.assertContains(response, 'Doctor Consultation')

    def test_section_three_blood_collection_renders(self):
        """Section 3: Blood Collection (/blood-collection/)"""
        response = self.client.get(reverse('blood_collection:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blood_collection/booking_list.html')
        self.assertContains(response, 'Blood Collection Services')
        self.assertContains(response, 'Schedule Blood Sample Collection')

    def test_section_four_reports_renders(self):
        """Section 4: Reports (/reports/)"""
        response = self.client.get(reverse('reports:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/report_list.html')
        self.assertContains(response, 'Laboratory &amp; Diagnostic Reports')
        self.assertContains(response, 'No reports are available yet.')

    def test_section_five_history_renders(self):
        """Section 5: History (/history/)"""
        response = self.client.get(reverse('history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'history/history.html')
        self.assertContains(response, 'Healthcare History &amp; Activity Log')
        self.assertContains(response, 'Patient Historical Timeline')


class DoctorConsultationBookingTests(TestCase):
    """Requirement: Doctor booking validation, slot checking, double-booking prevention, cancellation."""

    def setUp(self):
        self.client = Client()
        self.patient = UserModel.objects.create_user(
            username='patient1',
            email='p1@example.com',
            password='SecurePassword2026!'
        )
        self.client.force_login(self.patient)
        self.doctor = Doctor.objects.create(
            name='Arthur Campbell',
            qualifications='MD, FACP',
            specialty='Internal Medicine',
            consultation_mode='both'
        )

    def test_book_consultation_success(self):
        tomorrow = timezone.now().date() + timedelta(days=1)
        response = self.client.post(reverse('consultations:list'), {
            'doctor': self.doctor.id,
            'appointment_date': tomorrow.isoformat(),
            'time_slot': '09:00 AM - 09:30 AM',
            'consultation_type': 'in_person',
            'reason_for_consultation': 'Routine inflammation check',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Consultation.objects.filter(patient=self.patient, doctor=self.doctor).exists())

    def test_reject_past_appointment_date(self):
        yesterday = timezone.now().date() - timedelta(days=1)
        response = self.client.post(reverse('consultations:list'), {
            'doctor': self.doctor.id,
            'appointment_date': yesterday.isoformat(),
            'time_slot': '09:00 AM - 09:30 AM',
            'consultation_type': 'in_person',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Appointment date cannot be in the past')
        self.assertFalse(Consultation.objects.filter(appointment_date=yesterday).exists())

    def test_prevent_double_booking_same_doctor_slot(self):
        target_date = timezone.now().date() + timedelta(days=2)
        # Create first booking
        Consultation.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=target_date,
            time_slot='10:00 AM - 10:30 AM',
            status='confirmed'
        )

        # Attempt to book exact same doctor, date, and time slot
        response = self.client.post(reverse('consultations:list'), {
            'doctor': self.doctor.id,
            'appointment_date': target_date.isoformat(),
            'time_slot': '10:00 AM - 10:30 AM',
            'consultation_type': 'in_person',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already has an appointment scheduled')

    def test_cancel_eligible_consultation(self):
        future_date = timezone.now().date() + timedelta(days=3)
        consultation = Consultation.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=future_date,
            time_slot='02:00 PM - 02:30 PM',
            status='pending'
        )
        response = self.client.post(reverse('consultations:cancel', args=[consultation.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        consultation.refresh_from_db()
        self.assertEqual(consultation.status, 'cancelled')


class BloodCollectionBookingTests(TestCase):
    """Requirement: Blood collection scheduling, validation, and cancellation."""

    def setUp(self):
        self.client = Client()
        self.patient = UserModel.objects.create_user(
            username='patient2',
            email='p2@example.com',
            password='SecurePassword2026!'
        )
        self.client.force_login(self.patient)

    def test_blood_collection_booking_success(self):
        """Diagnostic center visit booking backward compatibility."""
        future_date = timezone.now().date() + timedelta(days=1)
        response = self.client.post(reverse('blood_collection:list'), {
            'patient_name': 'Patient Two',
            'contact_number': '+1 555-432-1234',
            'collection_date': future_date.isoformat(),
            'time_slot': '07:30 AM - 08:30 AM (Fasting Preferred)',
            'collection_location': 'lab_central',
            'fasting_required': 'on',
            'special_notes': 'Lipid and metabolic panel requested',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(BloodCollectionBooking.objects.filter(patient=self.patient, collection_method=BloodCollectionBooking.METHOD_CENTER).exists())

    def test_home_collection_booking_success(self):
        """Home blood sample collection booking with address validation and serviceability."""
        future_date = timezone.now().date() + timedelta(days=2)
        response = self.client.post(reverse('blood_collection:list'), {
            'collection_method': 'HOME',
            'patient_name': 'Jane Doe',
            'contact_number': '9876543210',
            'collection_date': future_date.isoformat(),
            'time_slot': '07:30 AM - 08:30 AM (Fasting Preferred)',
            'house_number': 'Flat 402, Lotus Towers',
            'street': 'Barakhamba Road',
            'area': 'Connaught Place',
            'city': 'New Delhi',
            'state': 'Delhi',
            'pin_code': '110001',
            'contact_person': 'Jane Doe',
            'contact_phone': '9876543210',
            'landmark': 'Near Rajiv Chowk Metro',
            'additional_directions': 'Tower B, 4th floor, buzzer on right',
            'fasting_required': 'on',
            'special_notes': 'Morning fasting CRP sample',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        booking = BloodCollectionBooking.objects.filter(patient=self.patient, collection_method='HOME').first()
        self.assertIsNotNone(booking)
        self.assertTrue(booking.is_home_collection)
        self.assertEqual(booking.pin_code, '110001')
        self.assertEqual(booking.city, 'New Delhi')
        self.assertIn('Flat 402', booking.full_address)
        self.assertIn('Connaught Place', booking.full_address)
        self.assertIn('110001', booking.full_address)

    def test_home_collection_unserviceable_pincode_rejected(self):
        """Reject unserviceable PIN codes with clear clinical feedback."""
        future_date = timezone.now().date() + timedelta(days=2)
        response = self.client.post(reverse('blood_collection:list'), {
            'collection_method': 'HOME',
            'patient_name': 'Jane Doe',
            'contact_number': '9876543210',
            'collection_date': future_date.isoformat(),
            'time_slot': '07:30 AM - 08:30 AM (Fasting Preferred)',
            'house_number': 'House 1',
            'street': 'Remote Road',
            'area': 'Remote Hills',
            'city': 'Remote Town',
            'state': 'Remote State',
            'pin_code': '999999',
            'contact_person': 'Jane Doe',
            'contact_phone': '9876543210',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Home collection is currently not available in PIN code 999999')
        self.assertFalse(BloodCollectionBooking.objects.filter(pin_code='999999').exists())

    def test_home_collection_missing_address_fields(self):
        """Enforce all required address components when Home Collection is chosen."""
        future_date = timezone.now().date() + timedelta(days=2)
        response = self.client.post(reverse('blood_collection:list'), {
            'collection_method': 'HOME',
            'patient_name': 'Jane Doe',
            'contact_number': '9876543210',
            'collection_date': future_date.isoformat(),
            'time_slot': '07:30 AM - 08:30 AM (Fasting Preferred)',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'House / Flat / Building number is required')
        self.assertContains(response, 'Street or Road address is required')
        self.assertContains(response, 'Area or Locality is required')
        self.assertContains(response, 'City is required')
        self.assertContains(response, 'State is required')
        self.assertContains(response, 'Six-digit postal PIN code is required')

    def test_prevent_slot_collision_same_patient(self):
        """Prevent same patient from double-booking same date and time slot."""
        future_date = timezone.now().date() + timedelta(days=3)
        slot = '10:00 AM - 11:00 AM'
        # Create initial booking
        BloodCollectionBooking.objects.create(
            patient=self.patient,
            patient_name='Jane Doe',
            contact_number='9876543210',
            collection_method='CENTER',
            collection_location='lab_central',
            collection_date=future_date,
            time_slot=slot,
            status='confirmed'
        )
        # Attempt to book another slot at same time
        response = self.client.post(reverse('blood_collection:list'), {
            'collection_method': 'CENTER',
            'patient_name': 'Jane Doe',
            'contact_number': '9876543210',
            'collection_date': future_date.isoformat(),
            'time_slot': slot,
            'collection_location': 'lab_north',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already have a blood sample collection booking scheduled for this date and time slot')

    def test_check_pincode_api_endpoint(self):
        """API endpoint /blood-collection/api/check-pincode/ validates serviceability."""
        # Serviceable PIN
        resp = self.client.get(reverse('blood_collection:check_pincode') + '?pincode=110001')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['serviceable'])
        self.assertEqual(data['pincode'], '110001')
        self.assertEqual(data['city'], 'New Delhi')

        # Unserviceable PIN
        resp_unserviceable = self.client.get(reverse('blood_collection:check_pincode') + '?pincode=999999')
        self.assertEqual(resp_unserviceable.status_code, 200)
        data_unserviceable = resp_unserviceable.json()
        self.assertFalse(data_unserviceable['serviceable'])

        # Invalid format
        resp_bad = self.client.get(reverse('blood_collection:check_pincode') + '?pincode=invalid')
        self.assertEqual(resp_bad.status_code, 400)

    def test_reject_past_collection_date(self):
        past_date = timezone.now().date() - timedelta(days=2)
        response = self.client.post(reverse('blood_collection:list'), {
            'patient_name': 'Patient Two',
            'contact_number': '+1 555-432-1234',
            'collection_date': past_date.isoformat(),
            'time_slot': '07:30 AM - 08:30 AM (Fasting Preferred)',
            'collection_location': 'lab_central',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Collection date cannot be in the past')


class ReportsAuthorizationTests(TestCase):
    """Requirement: Reports privacy and strict patient-level access control."""

    def setUp(self):
        self.client_a = Client()
        self.user_a = UserModel.objects.create_user(username='user_a', email='a@test.com', password='PasswordA123!')
        self.client_a.force_login(self.user_a)

        self.client_b = Client()
        self.user_b = UserModel.objects.create_user(username='user_b', email='b@test.com', password='PasswordB123!')
        self.client_b.force_login(self.user_b)

        # Create report owned by User A
        self.report_a = MedicalReport.objects.create(
            patient=self.user_a,
            title='Serum CRP High-Sensitivity Immunoassay',
            category='inflammation',
            issuing_lab='CRPify Reference Lab',
            report_date=timezone.now().date(),
            notes='Patient A confidential report'
        )

    def test_owner_can_view_report(self):
        response = self.client_a.get(reverse('reports:view', args=[self.report_a.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Serum CRP High-Sensitivity Immunoassay')

    def test_other_patient_cannot_view_report(self):
        """User B must be blocked with HTTP 403 Forbidden from accessing User A's report."""
        response = self.client_b.get(reverse('reports:view', args=[self.report_a.id]))
        self.assertEqual(response.status_code, 403)

    def test_other_patient_cannot_download_report(self):
        """User B must be blocked with HTTP 403 Forbidden from downloading User A's report."""
        response = self.client_b.get(reverse('reports:download', args=[self.report_a.id]))
        self.assertEqual(response.status_code, 403)


class HistoryTimelineTests(TestCase):
    """Requirement: Unified patient history timeline with category filtering."""

    def setUp(self):
        self.client = Client()
        self.patient = UserModel.objects.create_user(username='history_user', email='h@test.com', password='PasswordH123!')
        self.client.force_login(self.patient)

        self.doctor = Doctor.objects.create(name='Linda Croft', qualifications='MD', specialty='Pathology')
        self.c = Consultation.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now().date(),
            time_slot='09:00 AM - 09:30 AM'
        )
        self.b = BloodCollectionBooking.objects.create(
            patient=self.patient,
            patient_name='History Patient',
            contact_number='1234567890',
            collection_date=timezone.now().date(),
            time_slot='10:00 AM - 11:00 AM'
        )

    def test_history_all_filter(self):
        response = self.client.get(f"{reverse('history')}?filter=all")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Doctor Consultation')
        self.assertContains(response, 'Blood Collection')

    def test_history_category_filter(self):
        response = self.client.get(f"{reverse('history')}?filter=consultation")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Doctor Consultation')


class AuthenticationFlowsTests(TestCase):
    """Preserved login and signup flows."""

    def setUp(self):
        self.client = Client()
        self.user = UserModel.objects.create_user(
            username='authpatient',
            email='patient@smartsense.ai',
            password='ValidPassword2026!'
        )

    def test_login_flow(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'authpatient',
            'password': 'ValidPassword2026!',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_logout_post_required(self):
        self.client.force_login(self.user)
        # GET is rejected
        get_resp = self.client.get(reverse('accounts:logout'))
        self.assertEqual(get_resp.status_code, 405)

        # POST logs out
        post_resp = self.client.post(reverse('accounts:logout'), follow=True)
        self.assertRedirects(post_resp, reverse('accounts:login'))
        self.assertFalse(post_resp.context['user'].is_authenticated)
