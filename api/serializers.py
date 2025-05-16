from rest_framework import serializers
from .models import Booking,ContactUs
from django.conf import settings


from django.utils import timezone
from django.core.mail import send_mail

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('status', 'created_at', 'updated_at', 'days')

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("End date must be after start date")
        return data

    def create(self, validated_data):
        booking = Booking.objects.create(**validated_data)
        
        # Current year for footer
        current_year = timezone.now().year
        
        # User Confirmation Email (HTML)
        user_html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Booking Request Received</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
            <div style="background: #f8f9fa; padding: 30px; border-radius: 8px;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <h1 style="color: #17a2b8; margin: 0;">Booking Request Received</h1>
                    <div style="height: 3px; background: #17a2b8; width: 80px; margin: 15px auto;"></div>
                </div>
                
                <p style="margin-bottom: 20px;">Dear {booking.name},</p>
                
                <div style="background: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; border-left: 4px solid #17a2b8;">
                    <p style="margin: 0 0 15px 0;">
                        Thank you for your booking request for <strong style="color: #17a2b8;">{booking.get_event_type_display()}</strong>
                        from <strong>{booking.start_date}</strong> to <strong>{booking.end_date}</strong>.
                    </p>
                    <p style="margin: 0;">Our team will review your request shortly.</p>
                </div>
                
                <div style="text-align: center; margin: 25px 0;">
                    <a href="mailto:{settings.DEFAULT_FROM_EMAIL}" 
                       style="background: #17a2b8; color: white; padding: 12px 25px; 
                              text-decoration: none; border-radius: 4px; display: inline-block;">
                        Contact Us
                    </a>
                </div>
                
                <div style="border-top: 1px solid #eee; padding-top: 20px; text-align: center; font-size: 14px; color: #666;">
                    <p style="margin: 0;">© {current_year} MM Function Hall. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # User Confirmation Plain Text
        user_plain_content = f"""Dear {booking.name},

Thank you for your booking request for {booking.get_event_type_display()} 
from {booking.start_date} to {booking.end_date}.

Our team will review your request and get back to you shortly.

Best regards,
MM Function Hall Team
"""
        
        # Admin Notification Email (HTML)
        admin_html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>New Booking Request</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
            <div style="background: #f8f9fa; padding: 30px; border-radius: 8px;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <h1 style="color: #6c757d; margin: 0;">New Booking Request</h1>
                    <div style="height: 3px; background: #6c757d; width: 80px; margin: 15px auto;"></div>
                </div>
                
                <div style="background: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; border-left: 4px solid #6c757d;">
                    <h3 style="margin-top: 0; color: #495057;">Booking Details:</h3>
                    <table style="width: 100%;">
                        <tr><td style="padding: 5px 0; font-weight: bold;">Name:</td><td style="padding: 5px 0;">{booking.name}</td></tr>
                        <tr><td style="padding: 5px 0; font-weight: bold;">Event:</td><td style="padding: 5px 0;">{booking.get_event_type_display()}</td></tr>
                        <tr><td style="padding: 5px 0; font-weight: bold;">Dates:</td><td style="padding: 5px 0;">{booking.start_date} to {booking.end_date}</td></tr>
                        <tr><td style="padding: 5px 0; font-weight: bold;">Guests:</td><td style="padding: 5px 0;">{booking.guests}</td></tr>
                        <tr><td style="padding: 5px 0; font-weight: bold;">Phone:</td><td style="padding: 5px 0;">{booking.phone}</td></tr>
                        <tr><td style="padding: 5px 0; font-weight: bold;">Email:</td><td style="padding: 5px 0;">{booking.email}</td></tr>
                    </table>
                </div>
                
                <div style="text-align: center; margin: 25px 0;">
                    <a href="{settings.ADMIN_URL}/admin/bookings/booking/{booking.id}/change/" 
                       style="background: #6c757d; color: white; padding: 12px 25px; 
                              text-decoration: none; border-radius: 4px; display: inline-block;">
                        View in Admin Panel
                    </a>
                </div>
                
                <div style="border-top: 1px solid #eee; padding-top: 20px; text-align: center; font-size: 14px; color: #666;">
                    <p style="margin: 0;">MM Function Hall Booking System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Admin Notification Plain Text
        admin_plain_content = f"""New booking request:

Name: {booking.name}
Event: {booking.get_event_type_display()}
Dates: {booking.start_date} to {booking.end_date}
Guests: {booking.guests}
Phone: {booking.phone}
Email: {booking.email}

View in admin panel: {settings.ADMIN_URL}/admin/bookings/booking/{booking.id}/change/
"""
        
        # Send user confirmation
        send_mail(
            'Booking Request Received',
            user_plain_content,
            settings.DEFAULT_FROM_EMAIL,
            [booking.email],
            html_message=user_html_content,
            fail_silently=False
        )
        
        # Send admin notification
        send_mail(
            'New Booking Request',
            admin_plain_content,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            html_message=admin_html_content,
            fail_silently=False
        )
        
        return booking
    

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = '__all__'