from django.http import HttpResponse
from .models import Guest
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate, login, logout
from .models import *
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
import os
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Billing, Booking, Guest
from .forms import FeedbackForm

# Create your views here.

def home(request):
    return render(request,"homePage.html")

def register(request):
    if request.method == 'POST':
        # Extract data from the form submission
        first_name = request.POST.get('FirstName')
        last_name = request.POST.get('LastName')
        email = request.POST.get('Email')

        cnic = request.POST.get('CNIC')
        password = request.POST.get('Password')
        address = request.POST.get('Address')
        confirm_password = request.POST.get('ConfirmPassword')
        contact_no = request.POST.get('ContactNo')
        
        myUser=User.objects.create_user(first_name,email,password)
        myUser.first_name=first_name
        myUser.last_name=last_name
        myUser.username=email
        myUser.save()
        # Create a new Guest object and save it to the database
        new_guest = Guest(
            FirstName=first_name,
            LastName=last_name,
            Email=email,
            CNIC=cnic,
            Password=password,
            Address=address,
            ConfirmPassword=confirm_password,
            ContactNo=contact_no
        )
        new_guest.save()

        return redirect('regComplete')
    else:
        return render(request, 'registration.html')   

def booking_page(request):
    # Retrieve room types from the database
    room_types = RoomType.objects.all()  # Fetch all room types (this could be more specific as needed)
    # Pass room types data to the template as context
    return render(request, 'booking.html', {'room_types': room_types})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate using email as username
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # Log in the user
            login(request, user)
            # Redirect to the booking page or any desired URL
            return redirect('dashboard')
        else:
            # Invalid login, display an error message
            return redirect('incorrectDetails') 

    return render(request, 'login.html')
 
def incorrectDetails(request):
    return render(request,"incorrectDetails.html")


def about(request):
    return render(request, 'aboutUs.html')

#def contact_us(request):
    return HttpResponse("Contact page placeholder")

def detail_page(request, selected_room_type):
    available_rooms = Room.objects.filter(room_type__room_type=selected_room_type)

    context = {
        'selected_room_type': selected_room_type,
        'available_rooms': available_rooms,
    }

    return render(request, 'roomDetails.html', context)

def service_selection(request):
    services = Service.objects.all()
    return render(request, 'serviceSelection.html', {'services': services})



def billing_page(request):
    return render(request, 'billing.html') 

def after_login(request):
    return render(request, 'afterlogin.html') 

def confirm_booking(request):
    return render(request, 'booking_confirmation.html')



from django.shortcuts import render
from .models import Guest

def dashboard(request):
    if request.user.is_authenticated:
        try:
            # Fetch all Guest instances associated with the logged-in user's email
            guest_instances = Guest.objects.filter(Email=request.user.email)
            
            if guest_instances.exists():
                # Assuming you want to use the first Guest instance found
                guest_instance = guest_instances.first()
                user_bookings = guest_instance.booking_set.all()  # Access bookings using related name
                
                return render(request, "dashboard.html", {'bookings': user_bookings})
            else:
                return HttpResponse("Guest information not found.")
        except Guest.DoesNotExist:
            return HttpResponse("Guest information not found.")
    else:
        return HttpResponse("Please log in to view the dashboard.")


def profileChange(request):
    guest = Guest.objects.get(Email=request.user.email) #left side guest is variable, right side Guest is model name

    if request.method == "POST":
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        user = request.user
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        # Update voter information
        guest.First_Name = request.POST.get('first_name')
        guest.Last_Name = request.POST.get('last_name')
        guest.Email = request.POST.get('email')
        guest.CNIC = request.POST.get('cnicNum')
        guest.Address = request.POST.get('address')
        guest.Phone_Number = request.POST.get('phone')
        guest.save()

        return redirect('dashboard')
    else:
        return render(request, "changeProfile.html", {'guest': guest})
          
def logoutview(request):
    logout(request)
    return redirect('home')


#########################################################################################


from django.contrib.auth.decorators import login_required

@login_required
def confirm_room(request):
    if request.method == 'POST':
        room_number = request.POST.get('room_number')
        check_in_date = request.POST.get('check_in_date')
        check_out_date = request.POST.get('check_out_date')

        try:
            room = Room.objects.get(room_number=room_number)
            room.room_status = 'booked'
            room.save()

            # Check if a Guest object exists for the logged-in user
            guest, created = Guest.objects.get_or_create(pk=request.user.id)

            booking = Booking.objects.create(
                guest=guest,
                room=room,
                check_in_date=check_in_date,
                check_out_date=check_out_date
            )

            return redirect("book_service", booking_id=booking.id)  # Redirect to billing page with booking_id

        except Room.DoesNotExist:
            return HttpResponse("Room does not exist!")
        except Exception as e:
            return HttpResponse(f"Booking failed. Error: {e}")

    return HttpResponse("Invalid request")




def book_service(request, booking_id):
    if request.method == 'GET':
        booking = get_object_or_404(Booking, pk=booking_id)
        available_services = Service.objects.all()  # Fetch all available services

        return render(request, 'serviceSelection.html', {'booking': booking, 'services': available_services})

    elif request.method == 'POST':
        selected_services = request.POST.getlist('selected_services')
      
        
        try:
            booking = Booking.objects.get(pk=booking_id)
            services = Service.objects.filter(pk__in=selected_services)
            
            
            booking.services.set(services)  # Set the selected services for the booking

            return redirect("billing_page", booking_id=booking.id)

        except Booking.DoesNotExist:
            return HttpResponse("Booking does not exist!")
        except Exception as e:
            return HttpResponse(f"Service booking failed. Error: {e}")

    return HttpResponse("Invalid request")

def billing_page(request, booking_id):
    try:
        booking = get_object_or_404(Booking, pk=booking_id)
        total_amount = booking.calculate_total()

        if request.method == 'POST':
            try:
                # Create Billing instance (cash payment assumed)
                billing = Billing.objects.create(booking=booking, total_amount=total_amount, payment_method='Cash')

                return redirect('receipt', booking_id=booking.id)
            except Exception as e:
                return HttpResponse(f"Failed to process payment. Error: {e}")

        return render(request, 'billing.html', {'total_amount': total_amount, 'booking': booking})

    except Booking.DoesNotExist:
        return HttpResponse("Booking does not exist!")
    except Exception as e:
        return HttpResponse(f"Error: {e}")

def receipt(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    guest = booking.guest  # Assuming Booking model has a foreign key to Guest
    
    # Fetch the guest details
    guest_first_name = guest.FirstName
    guest_last_name = guest.LastName
    room_number = booking.room.room_number
    check_in_date = booking.check_in_date
    check_out_date = booking.check_out_date
    total_amount = booking.calculate_total()  # Assuming you have a method to calculate the total

    # Get the HTML content for the receipt
    template = get_template('receipt_pdf.html')  # Your HTML template for receipt
    html = template.render({
        'guest_first_name': guest_first_name,
        'guest_last_name': guest_last_name,
        'room_number': room_number,
        'check_in_date': check_in_date,
        'check_out_date': check_out_date,
        'total_amount': total_amount,
    })

    # Create a PDF from the HTML content
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{booking_id}.pdf"'

    # Use xhtml2pdf to convert HTML to PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def download_receipt(request, billing_id):
    try:
        # Retrieve the billing instance based on the provided ID
        billing = Billing.objects.get(id=billing_id)
        
        # Load the template for the PDF (make sure the path is correct)
        template = get_template('homepage/billing_pdf.html')
        html = template.render({'billing': billing})

        # Create an HTTP response to return the PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_{billing_id}.pdf"'

        # Generate the PDF from HTML content
        pisa_status = pisa.CreatePDF(html, dest=response)
        
        if pisa_status.err:
            return HttpResponse(f'We had some errors while generating the PDF: {pisa_status.err}')
        return response

    except Billing.DoesNotExist:
        return HttpResponse("Billing not found.")
    except Exception as e:
        return HttpResponse(f"An error occurred: {e}") 

def create_checkout_session(request, booking_id):
    try:
        booking = Booking.objects.get(pk=booking_id)
        total_amount = booking.calculate_total()

        # Create a new Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Room and Services',
                        },
                        'unit_amount': int(total_amount * 100),  # Convert to cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='http://127.0.0.1:8000/success',
            cancel_url='http://127.0.0.1:8000/cancel',
        )

        return redirect(session.url)

    except Booking.DoesNotExist:
        return HttpResponse("Booking does not exist!")
    except Exception as e:
        return HttpResponse(f"Failed to create checkout session. Error: {e}")

def success(request):
    return render(request, 'success.html')

def cancel(request):
    return render(request, 'cancel.html')


def regComplete(request):
    return render(request,"regComplete.html")

def staff_viewer(request):
    # Fetch all staff members from the database
    all_staff = Staff.objects.all()  # Replace 'Staff' with your actual model name
    
    # Pass the staff data to the template for rendering
    context = {
        'all_staff': all_staff,
    }
    return render(request, 'staff_viewer.html', context)

def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('feedback_thankyou')
    else:
        form = FeedbackForm()
    return render(request, 'feedback.html', {'form': form})
def feedback_thankyou(request):
    return render(request, 'thankyou.html', {'message': 'Thank you for your feedback!'})
