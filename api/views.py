from rest_framework import generics, status
from rest_framework.response import Response
from .models import Booking,ContactUs
from .serializers import BookingSerializer,ContactSerializer
from django.core.mail import send_mail
from django.conf import settings
from datetime import date, timedelta
from rest_framework.views import APIView

class BookingListCreateAPIView(generics.ListCreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


class BookingRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        new_status = request.data.get('status')
        
        if new_status and new_status != instance.status:
            # Status is being changed
            instance.status = new_status
            instance.save()
            
            # Prepare email content
            if new_status == 'confirmed':
                subject = 'Booking Confirmed!'
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Booking Confirmed</title>
                </head>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background-color: #f8f9fa; padding: 30px; border-radius: 5px;">
                        <h1 style="color: #28a745; text-align: center;">Booking Confirmed!</h1>
                        
                        <p style="margin-bottom: 20px;">Dear {instance.name},</p>
                        
                        <p style="margin-bottom: 20px;">
                            We are pleased to inform you that your booking for <strong>{instance.get_event_type_display()}</strong>
                            from <strong>{instance.start_date}</strong> to <strong>{instance.end_date}</strong> has been confirmed!
                        </p>
                        
                        <p style="margin-bottom: 20px;">
                            Please feel free to contact us if you have any questions or need further assistance.
                        </p>
                        
                        <div style="text-align: center; margin-top: 30px;">
                            <a href="mailto:{settings.DEFAULT_FROM_EMAIL}" 
                               style="background-color: #28a745; color: white; padding: 10px 20px; 
                                      text-decoration: none; border-radius: 5px; display: inline-block;">
                                Contact Us
                            </a>
                        </div>
                        
                        <p style="margin-top: 30px; font-size: 0.9em; color: #666; text-align: center;">
                            Best regards,<br>
                            MM Function Hall Team
                        </p>
                    </div>
                </body>
                </html>
                """
            else:
                subject = 'Booking Status Update'
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Booking Update</title>
                </head>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background-color: #f8f9fa; padding: 30px; border-radius: 5px;">
                        <h1 style="color: #007bff; text-align: center;">Booking Status Update</h1>
                        
                        <p style="margin-bottom: 20px;">Dear {instance.name},</p>
                        
                        <p style="margin-bottom: 20px;">
                            Your booking request for <strong>{instance.get_event_type_display()}</strong>
                            from <strong>{instance.start_date}</strong> to <strong>{instance.end_date}</strong>
                            has been updated to: <strong style="text-transform: capitalize;">{new_status}</strong>.
                        </p>
                        
                        <p style="margin-bottom: 20px;">
                            Please contact us for more information or if you have any questions.
                        </p>
                        
                        <div style="text-align: center; margin-top: 30px;">
                            <a href="mailto:{settings.DEFAULT_FROM_EMAIL}" 
                               style="background-color: #007bff; color: white; padding: 10px 20px; 
                                      text-decoration: none; border-radius: 5px; display: inline-block;">
                                Contact Us
                            </a>
                        </div>
                        
                        <p style="margin-top: 30px; font-size: 0.9em; color: #666; text-align: center;">
                            Best regards,<br>
                            MM Function Hall Team
                        </p>
                    </div>
                </body>
                </html>
                """
            
            # Create plain text version
            plain_content = f"Dear {instance.name},\n\n"
            plain_content += f"Your booking for {instance.get_event_type_display()} "
            plain_content += f"from {instance.start_date} to {instance.end_date} "
            plain_content += f"has been {new_status}.\n\n"
            plain_content += "Please contact us if you have any questions.\n\n"
            plain_content += "Best regards,\nMM Function Hall Team"
            
            # Send email
            email = EmailMessage(
                subject,
                html_content,
                settings.DEFAULT_FROM_EMAIL,
                [instance.email],
            )
            email.content_subtype = "html"  # This makes it HTML email
            email.send(fail_silently=False)
            
            return Response(BookingSerializer(instance).data)
        
        return super().update(request, *args, **kwargs)


class BookingDatesAPIView(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        # Get all dates that are booked (including ranges)
        booked_dates = set()
        bookings = Booking.objects.filter(status='confirmed')  # Only consider confirmed bookings
        
        for booking in bookings:
            current_date = booking.start_date
            while current_date <= booking.end_date:
                booked_dates.add(current_date)
                current_date += timedelta(days=1)
        
        return Response(sorted(list(booked_dates)))

class PendingBookingsAPIView(generics.ListAPIView):
    queryset = Booking.objects.filter(status='pending')
    serializer_class = BookingSerializer

from django.core.mail import EmailMessage

class ConfirmBookingAPIView(generics.UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 'confirmed'
        instance.save()
        
        # HTML email content with inline CSS
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Booking Confirmed</title>
        </head>
        <body style="font-family: 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 0;">
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 8px;">
                <div style="text-align: center; margin-bottom: 25px;">
                    <h1 style="color: #28a745; margin: 0; font-size: 24px;">Booking Confirmed!</h1>
                    <div style="height: 3px; background-color: #28a745; width: 80px; margin: 15px auto;"></div>
                </div>
                
                <p style="margin-bottom: 20px; font-size: 16px;">Dear {instance.name},</p>
                
                <div style="background-color: white; padding: 20px; border-radius: 5px; margin-bottom: 25px; border-left: 4px solid #28a745;">
                    <p style="margin: 0 0 15px 0; font-size: 15px;">
                        We're delighted to confirm your booking for <strong style="color: #28a745;">{instance.get_event_type_display()}</strong>
                        from <strong>{instance.start_date}</strong> to <strong>{instance.end_date}</strong>.
                    </p>
                    <p style="margin: 0; font-size: 15px;">
                        Your reservation is now officially confirmed and we're preparing everything for your event.
                    </p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="mailto:{settings.DEFAULT_FROM_EMAIL}" 
                       style="background-color: #28a745; color: white; padding: 12px 25px; 
                              text-decoration: none; border-radius: 4px; display: inline-block;
                              font-weight: bold; font-size: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        Contact Our Team
                    </a>
                </div>
                
                <div style="border-top: 1px solid #eee; padding-top: 20px; text-align: center;">
                    <p style="margin: 0; font-size: 14px; color: #666;">
                        Need help? Reply to this email or call us at [Your Phone Number]
                    </p>
                    <p style="margin: 10px 0 0 0; font-size: 13px; color: #999;">
                        © {timezone.now().year} MM Function Hall. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text fallback
        plain_content = f"Dear {instance.name},\n\n"
        plain_content += f"We are pleased to inform you that your booking for {instance.get_event_type_display()} "
        plain_content += f"from {instance.start_date} to {instance.end_date} has been confirmed!\n\n"
        plain_content += "Please contact us if you have any questions.\n\n"
        plain_content += "Best regards,\nMM Function Hall Team"
        
        # Send email
        email = EmailMessage(
            'Booking Confirmed!',
            html_content,
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)
        
        return Response(BookingSerializer(instance).data)


class RejectBookingAPIView(generics.UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 'rejected'
        instance.save()
        
        # HTML email content with inline CSS
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Booking Update</title>
        </head>
        <body style="font-family: 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 0;">
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 8px;">
                <div style="text-align: center; margin-bottom: 25px;">
                    <h1 style="color: #dc3545; margin: 0; font-size: 24px;">Booking Update</h1>
                    <div style="height: 3px; background-color: #dc3545; width: 80px; margin: 15px auto;"></div>
                </div>
                
                <p style="margin-bottom: 20px; font-size: 16px;">Dear {instance.name},</p>
                
                <div style="background-color: white; padding: 20px; border-radius: 5px; margin-bottom: 25px; border-left: 4px solid #dc3545;">
                    <p style="margin: 0 0 15px 0; font-size: 15px;">
                        We regret to inform you that your booking request for <strong style="color: #dc3545;">{instance.get_event_type_display()}</strong>
                        from <strong>{instance.start_date}</strong> to <strong>{instance.end_date}</strong> has been rejected.
                    </p>
                    <p style="margin: 0; font-size: 15px;">
                        We appreciate your interest and encourage you to consider alternative dates or venues.
                    </p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="mailto:{settings.DEFAULT_FROM_EMAIL}" 
                       style="background-color: #dc3545; color: white; padding: 12px 25px; 
                              text-decoration: none; border-radius: 4px; display: inline-block;
                              font-weight: bold; font-size: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        Contact Our Team
                    </a>
                </div>
                
                <div style="border-top: 1px solid #eee; padding-top: 20px; text-align: center;">
                    <p style="margin: 0; font-size: 14px; color: #666;">
                        For more information, please reply to this email
                    </p>
                    <p style="margin: 10px 0 0 0; font-size: 13px; color: #999;">
                        © {timezone.now().year} MM Function Hall. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text fallback
        plain_content = f"Dear {instance.name},\n\n"
        plain_content += f"We regret to inform you that your booking request for {instance.get_event_type_display()} "
        plain_content += f"from {instance.start_date} to {instance.end_date} has been rejected.\n\n"
        plain_content += "Please contact us for more information.\n\n"
        plain_content += "Best regards,\nMM Function Hall Team"
        
        # Send email
        email = EmailMessage(
            'Booking Update',
            html_content,
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)
        
        return Response(BookingSerializer(instance).data)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .serializers import ContactSerializer
from django.conf import settings

class ContactView(APIView):

    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            # Get the user's email
            user_email = serializer.validated_data.get('email')
            user_name = serializer.validated_data.get('name')

            # HTML content with inline CSS
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
                <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #2c3e50;">Hello {user_name},</h2>
                    <p style="font-size: 16px; color: #34495e;">
                        Thank you for contacting us. We’ve received your message and our team will get back to you within <strong>24 hours</strong>.
                    </p>
                    <p style="font-size: 16px; color: #34495e;">Meanwhile, feel free to browse our website or check out our FAQ section.</p>
                    <br/>
                    <p style="color: #7f8c8d;">Best Regards,<br><strong>MM Function Hall Team.</strong></p>
                </div>
            </body>
            </html>
            """

            subject = "We received your contact request"
            from_email = settings.DEFAULT_FROM_EMAIL
            to = [user_email]

            # Send email
            email = EmailMultiAlternatives(subject=subject, body='', from_email=from_email, to=to)
            email.attach_alternative(html_content, "text/html")
            email.send()

            return Response({"message": "Contact request received. Email sent."}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self,request):
        contact = ContactUs.objects.all()
        serializer = ContactSerializer(contact,many=True)
        return Response(serializer.data,status=200)