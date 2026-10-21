"""
Models for Blood Collection module in CRPify Patient Portal.
Supports both Home Blood Sample Collection and Visit Diagnostic Center.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import re

UserModel = get_user_model()


class ServiceablePincode(models.Model):
    """
    Configurable repository of serviceable postal PIN codes for home blood collection.
    Managed by administrators to define verified coverage zones.
    """
    pincode = models.CharField(max_length=10, unique=True, db_index=True, help_text="6-digit postal PIN code")
    area_name = models.CharField(max_length=150, blank=True, help_text="e.g., Connaught Place, Indiranagar, Bandra")
    city = models.CharField(max_length=100, blank=True, default="Metropolitan Area")
    state = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True, help_text="Whether home collection phlebotomy dispatch is active")
    max_slots_per_day = models.PositiveIntegerField(default=10, help_text="Maximum home bookings allowed per day")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['pincode']
        verbose_name = "Serviceable PIN Code"
        verbose_name_plural = "Serviceable PIN Codes"

    def __str__(self):
        area_str = f" ({self.area_name}, {self.city})" if self.area_name else ""
        status_str = "Active" if self.is_active else "Inactive"
        return f"{self.pincode}{area_str} [{status_str}]"


# Default list of major metropolitan coverage PIN codes for initial seeding / fallback
DEFAULT_SERVICEABLE_PINCODES = [
    # Delhi NCR
    {"pincode": "110001", "area_name": "Connaught Place / Central", "city": "New Delhi", "state": "Delhi"},
    {"pincode": "110002", "area_name": "Daryaganj / Old Delhi", "city": "New Delhi", "state": "Delhi"},
    {"pincode": "110003", "area_name": "Aliganj / Lodhi Road", "city": "New Delhi", "state": "Delhi"},
    {"pincode": "110016", "area_name": "Hauz Khas / Green Park", "city": "New Delhi", "state": "Delhi"},
    {"pincode": "110020", "area_name": "Okhla Phase I-III", "city": "New Delhi", "state": "Delhi"},
    {"pincode": "110025", "area_name": "Jamia Nagar / New Friends Colony", "city": "New Delhi", "state": "Delhi"},
    {"pincode": "110085", "area_name": "Rohini Sector 1-15", "city": "New Delhi", "state": "Delhi"},
    {"pincode": "122001", "area_name": "Gurugram Central", "city": "Gurugram", "state": "Haryana"},
    {"pincode": "122002", "area_name": "DLF Phase 1 & 2", "city": "Gurugram", "state": "Haryana"},
    {"pincode": "201301", "area_name": "Noida Sector 1-20", "city": "Noida", "state": "Uttar Pradesh"},
    # Mumbai
    {"pincode": "400001", "area_name": "Fort / Colaba", "city": "Mumbai", "state": "Maharashtra"},
    {"pincode": "400012", "area_name": "Parel / Lalbaug", "city": "Mumbai", "state": "Maharashtra"},
    {"pincode": "400050", "area_name": "Bandra West", "city": "Mumbai", "state": "Maharashtra"},
    {"pincode": "400053", "area_name": "Andheri West", "city": "Mumbai", "state": "Maharashtra"},
    {"pincode": "400076", "area_name": "Powai / Hiranandani", "city": "Mumbai", "state": "Maharashtra"},
    # Bengaluru
    {"pincode": "560001", "area_name": "MG Road / Ashok Nagar", "city": "Bengaluru", "state": "Karnataka"},
    {"pincode": "560004", "area_name": "Basavanagudi", "city": "Bengaluru", "state": "Karnataka"},
    {"pincode": "560029", "area_name": "Koramangala 1-4th Block", "city": "Bengaluru", "state": "Karnataka"},
    {"pincode": "560034", "area_name": "HSR Layout Sector 1-7", "city": "Bengaluru", "state": "Karnataka"},
    {"pincode": "560038", "area_name": "Indiranagar", "city": "Bengaluru", "state": "Karnataka"},
    {"pincode": "560066", "area_name": "Whitefield", "city": "Bengaluru", "state": "Karnataka"},
    # Hyderabad
    {"pincode": "500001", "area_name": "Abids / Koti", "city": "Hyderabad", "state": "Telangana"},
    {"pincode": "500032", "area_name": "Gachibowli / Financial Dist", "city": "Hyderabad", "state": "Telangana"},
    {"pincode": "500034", "area_name": "Banjara Hills", "city": "Hyderabad", "state": "Telangana"},
    {"pincode": "500081", "area_name": "HITEC City / Madhapur", "city": "Hyderabad", "state": "Telangana"},
    # Chennai & Kolkata
    {"pincode": "600001", "area_name": "George Town / Parrys", "city": "Chennai", "state": "Tamil Nadu"},
    {"pincode": "600028", "area_name": "R.A. Puram / Mylapore", "city": "Chennai", "state": "Tamil Nadu"},
    {"pincode": "700001", "area_name": "BBD Bagh / Central", "city": "Kolkata", "state": "West Bengal"},
    {"pincode": "700091", "area_name": "Salt Lake Sector V", "city": "Kolkata", "state": "West Bengal"},
]


def check_pincode_serviceability(pin_code: str):
    """
    Checks whether a 6-digit postal PIN code is currently serviceable for home blood sample collection.
    Returns: (is_serviceable: bool, message: str, details: dict or None)
    """
    pin_clean = re.sub(r'\s+', '', str(pin_code or '').strip())
    if not re.match(r'^\d{6}$', pin_clean):
        return False, "PIN code must be exactly 6 digits.", None

    # Check database records
    qs = ServiceablePincode.objects.filter(pincode=pin_clean)
    if qs.exists():
        entry = qs.first()
        if entry.is_active:
            return True, f"Home blood collection is available in {entry.area_name or entry.city}.", {
                'pincode': entry.pincode,
                'area_name': entry.area_name,
                'city': entry.city,
                'state': entry.state
            }
        else:
            return False, f"Home collection service for PIN {pin_clean} ({entry.area_name or entry.city}) is temporarily suspended.", None

    # Fallback to default in-memory list if database has not yet been seeded
    for item in DEFAULT_SERVICEABLE_PINCODES:
        if item["pincode"] == pin_clean:
            return True, f"Home blood collection is available in {item['area_name']} ({item['city']}).", item

    return False, f"Home collection is currently not available in PIN code {pin_clean}. Please choose 'Visit Diagnostic Center' or select another serviceable location.", None


class BloodCollectionBooking(models.Model):
    """
    Blood sample collection booking for laboratory pathology analysis.
    Supports both Home Blood Sample Collection and On-Site Diagnostic Center visits.
    """
    METHOD_HOME = 'HOME'
    METHOD_CENTER = 'CENTER'
    METHOD_CHOICES = [
        (METHOD_HOME, 'Home Blood Collection'),
        (METHOD_CENTER, 'Visit Diagnostic Center'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed Scheduled'),
        ('completed', 'Sample Collected'),
        ('cancelled', 'Cancelled'),
    ]

    CENTER_CHOICES = [
        ('lab_central', 'CRPify Diagnostic Center — Central Lab (Suite 201)'),
        ('lab_north', 'CRPify Diagnostic Center — North Pathology Wing'),
    ]

    LOCATION_CHOICES = CENTER_CHOICES + [
        ('home_collection', 'Home Blood Collection (Designated Address)'),
    ]

    patient = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='blood_bookings')
    patient_name = models.CharField(max_length=150, verbose_name="Patient Full Name")
    contact_number = models.CharField(max_length=30, verbose_name="Contact Telephone Number")
    collection_date = models.DateField(verbose_name="Requested Collection Date")
    time_slot = models.CharField(max_length=50, verbose_name="Collection Time Slot")

    # 1. Collection Method
    collection_method = models.CharField(
        max_length=10,
        choices=METHOD_CHOICES,
        default=METHOD_HOME,
        verbose_name="Collection Method"
    )

    # 2. Diagnostic Center (Required when collection_method == 'CENTER')
    collection_location = models.CharField(
        max_length=255,
        choices=LOCATION_CHOICES,
        default='lab_central',
        blank=True,
        verbose_name="Designated Collection Center"
    )

    # 3. Conditional Home Address Details (Required when collection_method == 'HOME')
    house_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="House / Flat / Building Number"
    )
    street = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Street / Road"
    )
    area = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Area / Locality"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        default="Metropolitan Area",
        verbose_name="City"
    )
    state = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="State"
    )
    pin_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Six-digit PIN Code"
    )
    contact_person = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Contact Person Name"
    )
    contact_phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Contact Phone Number"
    )
    landmark = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Landmark (Optional)"
    )
    additional_directions = models.TextField(
        blank=True,
        verbose_name="Additional Directions (Optional)"
    )

    # 4. Clinical Protocols & Administrative
    fasting_required = models.BooleanField(
        default=True,
        help_text="Standard 8-10 hour fasting recommended for metabolic and lipid accuracy."
    )
    special_notes = models.TextField(
        blank=True,
        help_text="Optional notes, accessibility needs, or prescription refs"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-collection_date', '-created_at']

    def __str__(self):
        method_str = "Home" if self.collection_method == self.METHOD_HOME else "Center"
        return f"[{method_str}] Blood Collection for {self.patient_name} on {self.collection_date} ({self.status})"

    @property
    def is_home_collection(self):
        return self.collection_method == self.METHOD_HOME

    @property
    def full_address(self):
        """Returns the formatted full home address for phlebotomist dispatch, or the diagnostic center label."""
        if self.is_home_collection:
            parts = [
                self.house_number,
                self.street,
                self.area,
                f"Near {self.landmark}" if self.landmark else "",
                self.city,
                f"{self.state} - {self.pin_code}" if (self.state and self.pin_code) else (self.state or self.pin_code),
            ]
            cleaned = [p.strip() for p in parts if p and p.strip()]
            return ", ".join(cleaned) if cleaned else "Home Address Provided"
        return self.get_collection_location_display()

    @property
    def destination_summary(self):
        """Returns a concise summary of the booking location / dispatch point."""
        if self.is_home_collection:
            area_city = f"{self.area}, {self.city}" if (self.area and self.city) else (self.area or self.city or "Home Address")
            return f"Home Dispatch: {area_city} ({self.pin_code})" if self.pin_code else f"Home Dispatch: {area_city}"
        return self.get_collection_location_display()

    @property
    def can_cancel(self):
        """Allows cancellation of upcoming pending or confirmed collections."""
        return self.status in ['pending', 'confirmed'] and self.collection_date >= timezone.now().date()
