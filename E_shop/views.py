from django.shortcuts import render, redirect
from store_app.models import Product,Categories,Filter_Price,Color,Brand,Contact_us,Order,OrderItem
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from cart.cart import Cart
import razorpay
from django.views.decorators.csrf import csrf_exempt

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECERET))

def BASE(request):
    return render(request,'main/base.html')

def HOME(request):
    product = Product.objects.filter()

    context = {
        'product':product,

    }
    return render(request,'main/index.html',context)

def ABOUT(request):
    return render(request,'main/about.html')

def PRODUCT(request):
    product = Product.objects.all()
    categories = Categories.objects.all()
    filter_price = Filter_Price.objects.all()
    color = Color.objects.all()
    brand = Brand.objects.all()
    CATID = request.GET.get('categories')
    fid = request.GET.get('filter_price')
    colid = request.GET.get('color')
    bid = request.GET.get('brand')
    ATOZID = request.GET.get('ATOZ')  
    ZTOAID = request.GET.get('ZTOA')
    P_LOWTOHIGHID = request.GET.get('P_LOWTOHIGH')
    P_HIGHTOLOWID = request.GET.get('P_HIGHTOLOW')
    NTOOID = request.GET.get('NTOO')
    OTONID = request.GET.get('OTON')

    if CATID:
        product = Product.objects.filter(categories=CATID,status='Publish')
    elif fid:
        product = Product.objects.filter(filter_price=fid,status='Publish')
    elif colid:
        product = Product.objects.filter(color=colid,status='Publish')
    elif bid:
        product = Product.objects.filter(brand=bid,status='Publish')
    elif ATOZID:
        product = Product.objects.all().order_by('name')       
    elif ZTOAID:
        product = Product.objects.all().order_by('-name')
    elif P_LOWTOHIGHID:
        product = Product.objects.all().order_by('price')
    elif P_HIGHTOLOWID:
        product = Product.objects.all().order_by('-price')
    elif NTOOID:
        product = Product.objects.all().order_by('condition')
    elif OTONID:
        product = Product.objects.all().order_by('-condition')
    else:
        product = Product.objects.all()
        
     

    context = {
        'product':product,
        'categories':categories,
        'filter_price':filter_price,
        'color':color,
        'brand':brand,
    }

    return render(request,'main/product.html',context)

def SEARCH(request):
    query = request.GET.get('query')
    product = Product.objects.filter(name__icontains=query)
    context = {
        'product':product,
    }

    return render(request,'main/search.html',context)

def PRODUCT_DETAILS(request,id):
    prod = Product.objects.filter(id=id).first()
    context = {
        'prod':prod,
    }
    return render(request,'main/product_single.html',context)

def CONTACT(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        contact = Contact_us(
            name=name,
            email=email,
            subject=subject,
            message=message,
        )
        subject = subject
        message = message
        email_from = settings.EMAIL_HOST_USER
        
        try:
            send_mail(subject,message,email_from,['nagarhrishabh@gmail.com'])
            contact.save()
            return redirect('home')
        except:
            return redirect('contact')

    return render(request,'main/Contact.html')

def HandleRegister(request):
    if request.method == "POST":
        username = request.POST.get('username')
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        email=request.POST.get('email')
        pass1=request.POST.get('pass1')
        pass2=request.POST.get('pass2')

        customer = User.objects.create_user(username,email,pass1)
        customer.first_name = first_name
        customer.last_name = last_name
        customer.save()
        return redirect('home')
    return render(request,'Registration/auth.html')

def HandleLogin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            return redirect('login')

    return render(request,'Registration/auth.html')

def HandleLogout(request):
    logout(request)
    return redirect('home')


# For cart

@login_required(login_url="/login/")
def cart_add(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("home")


@login_required(login_url="/login/")
def item_clear(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.remove(product)
    return redirect("cart_detail")


@login_required(login_url="/login/")
def item_increment(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("cart_detail")


@login_required(login_url="/login/")
def item_decrement(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.decrement(product=product)
    return redirect("cart_detail")


@login_required(login_url="/login/")
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("cart_detail")


@login_required(login_url="/login/")
def cart_detail(request):
    return render(request, 'Cart/cart_details.html')

def Check_out(request):
    amount_str = request.POST.get('amount')
    amount = float(amount_str)
    payment = client.order.create({
        "amount":amount,
        "currency":"INR",
        "payment_capture":"1"
    })
    order_id = payment['id']
    context = {
        'order_id':order_id,
        'payment':payment
    }
    return render(request,'Cart/checkout.html',context)

def PLACE_ORDER(request):
    if request.method == "POST":
        uid = request.session.get('_auth_user_id')
        user = User.objects.get(id=uid)
        cart = request.session.get('cart')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        country = request.POST.get('country')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postcode = request.POST.get('postcode')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        order_id = request.POST.get('order_id')
        amount = request.POST.get('amount')
        payment = request.POST.get('payment')
        
        context = {
            'order_id':order_id,
        }

        order = Order(
            user=user,
            firstname=firstname,
            lastname=lastname,
            country=country,
            city=city,
            address=address,
            state=state,
            postcode=postcode,
            phone=phone,
            email = email,
            payment_id=order_id,
            amount=amount,
        )
        order.save()
        for i in cart:
            a = (int(cart[i]['price']))
            b = cart[i]['quantity']
            total = a*b
            

            item = OrderItem(
                user = user,
                order = order,
                product = cart[i]['name'],
                image = cart[i]['image'],
                quantity = cart[i]['quantity'],
                price = cart[i]['price'],
                total = total,
            )
            item.save()
        
        return render(request,'Cart/placeorder.html',context)
    
@csrf_exempt
def success(request):
    if request.method == "POST":
        a = request.POST
        order_id = ""
        for key,val in a.items():
            if key == 'razorpay_order_id':
                order_id = val
                break
        
        user = Order.objects.filter(payment_id=order_id).first()
        user.paid = True
        user.save()
    return render(request,'Cart/thankyou.html')

def Your_Order(request):
    uid = request.session.get('_auth_user_id')
    user = User.objects.get(id=uid)
    order = OrderItem.objects.filter(user=user)
    context = {
        'order':order,
    }
    return render(request,'main/your_order.html',context)

def NotFound(request):
    return render(request,'main/404.html')

def account(request):
    
    u = request.user
    userid = u.id
    order = Order.objects.filter(id=u.id)
    context = {
        'order':order,
        'userid':userid,
    }
    return render(request,'Registration/account.html',context)