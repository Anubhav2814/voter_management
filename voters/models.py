from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import re


class VoterField(models.Model):
    FIELD_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('datetime', 'DateTime'),
        ('boolean', 'Boolean'),
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('select', 'Select'),
    ]

    name = models.CharField(max_length=255, unique=True)
    field_type = models.CharField(max_length=50, choices=FIELD_TYPES, default='text')
    is_required = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)  # Changed from auto_now_add
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'voters_voterfield'
        verbose_name = 'Voter Field'
        verbose_name_plural = 'Voter Fields'
        ordering = ['name']

    def __str__(self):
        return self.name


class Voter(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]

    VERIFY_STATUS_CHOICES = [
        ('Verified', 'Verified'),
        ('Pending', 'Pending'),
        ('Rejected', 'Rejected')
    ]

    # Required fields
    mlc_constituncy = models.CharField('MLC CONSTITUNCY', max_length=255, null=True, blank=True)
    assembly = models.CharField('ASSEMBLY', max_length=255)
    mandal = models.CharField('MANDAL', max_length=255)
    sno = models.CharField('SNO', max_length=50)
    mobile_no = models.CharField('MOBILE NO', max_length=15)

    # Optional fields (add null=True, blank=True)
    town = models.CharField('TOWN', max_length=255, null=True, blank=True)
    village = models.CharField('VILLAGE', max_length=255, null=True, blank=True)
    psno = models.CharField('PSNO', max_length=50, null=True, blank=True)
    location = models.CharField('LOCATION', max_length=255, null=True, blank=True)
    ps_address = models.TextField('PS ADDRESS', null=True, blank=True)
    street = models.CharField('STREET', max_length=255, null=True, blank=True)
    hno = models.CharField('HNO', max_length=50, null=True, blank=True)
    card_no = models.CharField('CARD NO', max_length=50, null=True, blank=True)
    voter_name = models.CharField('VOTER NAME', max_length=255, null=True, blank=True)
    age = models.IntegerField('AGE', null=True, blank=True)
    gender = models.CharField('GENDER', max_length=1, null=True, blank=True)
    rel_name = models.CharField('REL NAME', max_length=255, null=True, blank=True)
    relation = models.CharField('RELATION', max_length=255, null=True, blank=True)
    voter_status = models.CharField('VOTER STATUS', max_length=50, null=True, blank=True)
    party = models.CharField('PARTY', max_length=100, null=True, blank=True)
    caste = models.CharField('CASTE', max_length=100, null=True, blank=True)
    category = models.CharField('CATEGORY', max_length=100, null=True, blank=True)
    verify_status = models.CharField('VERIFY STATUS', max_length=20, null=True, blank=True)

    # Keep the data field temporarily for migration
    data = models.JSONField(default=dict, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        # Validate mobile number
        if self.mobile_no:
            # Remove any non-digit characters
            clean_number = re.sub(r'\D', '', self.mobile_no)
            # Check if it's a valid Indian mobile number
            if len(clean_number) < 10 or len(clean_number) > 12:
                raise ValidationError({
                    'mobile_no': 'Invalid mobile number length. Must be 10 digits.'
                })
            # Format the number if needed
            if len(clean_number) == 12 and clean_number.startswith('91'):
                self.mobile_no = clean_number[2:]
            elif len(clean_number) == 11 and clean_number.startswith('0'):
                self.mobile_no = clean_number[1:]

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def get_mlc_constituncy(self):
        return self.data.get('MLC CONSTITUNCY', '') if self.data else self.mlc_constituncy

    class Meta:
        db_table = 'voters_voter'
        verbose_name = 'Voter'
        verbose_name_plural = 'Voters'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.voter_name} - {self.card_no}"