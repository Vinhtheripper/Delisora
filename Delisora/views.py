from django.contrib.admindocs.utils import named_group_matcher
from django.shortcuts import render,redirect
from .models import *
from django.http import JsonResponse
import json
from .models import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout



def product_detail(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        order = {'get_cart_items': order.get_cart_items, 'get_cart_total': order.get_cart_total}
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']
    categories = Category.objects.filter(is_sub=False)
    id=request.GET.get('id','')
    if id:
        products=Product.objects.filter(id=id)
    else:
        products=Product.objects.none()

    context = {'items': items, 'order': order,'user': request.user,'cartItems':cartItems,'categories':categories,'products':products}
    return render(request, 'app/detail.html', context)


def category(request):
    categories = Category.objects.filter(is_sub=False)
    active_category = request.GET.get('category','')
    if active_category:
        products = Product.objects.filter(category__slug=active_category)
    context = {'categories':categories,'active_category':active_category,'products':products}
    return render(request, 'app/category.html', context)

def search(request):
    searched = ""
    keys = Product.objects.all()

    if request.method == "POST":
        searched = request.POST.get("searched", "").strip()


        if searched:
            keys = Product.objects.filter(name__icontains=searched) if searched else Product.objects.all()# Tìm kiếm không phân biệt chữ hoa/thường

    # Xử lý giỏ hàng
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']


    return render(request, 'app/search.html', {
        "searched": searched,
        "keys": keys,
        "products": Product.objects.all(),
        "user": request.user,
        "cartItems": cartItems,
    })


def register(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully!")
            return redirect('login')
    context = {'form': form}
    return render(request,'app/register.html',context)


def loginPage(request):
    # Kiểm tra nếu người dùng đã đăng nhập
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        print(request.POST)
        identifier = request.POST.get('identifier')  # Email hoặc Username
        password = request.POST.get('password')
        if not identifier or not password:
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin.')
            return render(request, 'app/login.html')

        username = None

        # Xác định xem identifier là email hay username
        if '@' in identifier:  # Nếu là email
            try:
                user_obj = User.objects.get(email=identifier)
                username = user_obj.username
            except User.DoesNotExist:
                messages.error(request, 'Email không tồn tại.')
        else:
            username = identifier  # Nếu là username

        # Xác thực user

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Sai tên đăng nhập/email hoặc mật khẩu.')

    return render(request, 'app/login.html')

def logoutPage(request):
    logout(request)
    return redirect('login')

def home(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']
    categories = Category.objects.filter(is_sub=False)
    products = Product.objects.all()
    context = {'products': products,'user': request.user,'cartItems':cartItems,'categories':categories}
    return render(request, 'app/home.html', context)



def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        order = {'get_cart_items': order.get_cart_items, 'get_cart_total': order.get_cart_total}
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']
    categories = Category.objects.filter(is_sub=False)

    context = {'items': items, 'order': order,'user': request.user,'cartItems':cartItems,'categories':categories}
    return render(request, 'app/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        order = {'get_cart_items': order.get_cart_items, 'get_cart_total': order.get_cart_total}

    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']
    categories = Category.objects.filter(is_sub=False)

    context = {'items': items, 'order': order,'user': request.user,'cartItems':cartItems,'categories':categories}
    return render(request, 'app/checkout.html', context)




def updateItem(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Request data:", data)

            productId = data.get('productId')
            action = data.get('action')

            if not productId or not action:
                return JsonResponse({'error': 'Invalid data'}, status=400)

            if request.user.is_authenticated:
                customer = request.user
            else:
                return JsonResponse({'error': 'User not authenticated'}, status=401)

            try:
                product = Product.objects.get(id=productId)
            except Product.DoesNotExist:
                return JsonResponse({'error': 'Product not found'}, status=404)

            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

            if action == 'add':
                orderItem.quantity += 1
                orderItem.save()
            elif action == 'remove':
                orderItem.quantity -= 1
                orderItem.save()
                if orderItem.quantity <= 0:
                    orderItem.delete()
            elif action == 'delete':
                orderItem.delete()

            return JsonResponse({'message': 'Item was updated', 'quantity': orderItem.quantity if action != 'delete' else 0}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
