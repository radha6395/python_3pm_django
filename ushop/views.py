from django.shortcuts import render,HttpResponse,redirect

# Create your views here.
from django.contrib.auth.hashers import make_password,check_password

from .models import *


def index(request):

    if request.method == 'POST':
        product_id = request.POST.get('productid')
        remove = request.POST.get('remove')
        print("product_id ---------",product_id)
        cart_id = request.session.get('cart')
        print("cart_id-------",cart_id)
        if cart_id:
            quantity = cart_id.get(product_id)
            if quantity:
                if remove:
                    if quantity <= 1:
                        cart_id.pop(product_id)
                    else:
                        cart_id[product_id] = quantity - 1
                else:            
                    cart_id[product_id] = quantity + 1
            else:
                cart_id[product_id] = 1
        else:
            cart_id = {}
            cart_id[product_id] = 1
            print("cart_id-------",cart_id)
        print(cart_id)    
        request.session['cart'] = cart_id

    category_id = request.GET.get('category_id')
    
    Category_obj = Category.objects.all()
    
    if category_id:
        product_obj = Product.objects.filter(product_category=category_id)
    else:
        product_obj = Product.objects.all()
    context = {
        'category_obj' : Category_obj,
        'product_obj' : product_obj
    }

    return render(request,'home.html',context=context)


def signup(request):
    if request.method == 'POST':
        f_name = request.POST.get("fname")
        l_name = request.POST.get("lname")
        email = request.POST.get("email")
        password = request.POST.get("pwd")
        mobile = request.POST.get("mbl")
        gender = request.POST.get("gender")

        reg_obj = Registration(
            first_name = f_name,
            last_name = l_name,
            email = email,
            password = make_password(password),
            mobile = mobile,
            gender = gender
        )
        reg_obj.save()

        return HttpResponse("Data saved successfully")
    

def login(request):
    if request.method == 'POST':
        email_id = request.POST.get("email")
        password = request.POST.get("password")


        try:
            email_obj = Registration.objects.get(email = email_id)
            if email_obj:
                request.session['name'] = email_obj.first_name
                request.session['customer_id'] = email_obj.id
                return redirect("home")
            
            else:
                return HttpResponse("Wrong password")
        
        except:
            return HttpResponse("email does not exist")
        

def logout(request):
    request.session.clear()
    return redirect("home")        

def cart_details(request):
    
    cart = list(request.session.get('cart').keys())
    product_obj = Product.objects.filter(id__in=cart)
    context = {
        'product_details' : product_obj
    }

    return render(request,'cart.html',context=context)   

def checkout_details(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')

        customer_id = request.session.get('customer_id')

        if not customer_id:
            return HttpResponse("please login")   
        
        cart = request.session.get('cart')
        product_obj = Product.objects.filter(id__in=list(cart.keys()))

        for i in product_obj:
            order_obj = Order(
                address = address,
                mobile = mobile,
                customer = Registration(id = customer_id),
                price = i.product_price,
                quantity = cart.get(str(i.id)),
                product = i
            )

            order_obj.save()
        return redirect('order')

def order(request):

    customer_id = request.session.get('customer_id')

    order_obj = Order.objects.filter(customer=customer_id)

    tp =0
    for i in order_obj:
        tp = tp + (i.price * i.quantity)

    context = {
        'order_obj' : order_obj,
        'tp' : tp
    }
    return render(request,'order.html',context=context)  
   
from rest_framework import viewsets
from .serializers import RegistrationSerializer

class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer