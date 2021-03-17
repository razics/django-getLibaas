from django.shortcuts import render,HttpResponse,redirect
from django.http import JsonResponse
import json
import datetime

from .models import *
from . utils import cookieCart,cartData,guestOrder


# Create your views here.
def search(request):
    return render(request,'store/search.html')




def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
        
   
    products=Product.objects.all()
    context={'products':products,'cartItems':cartItems}
    return render(request,'store/store.html',context)
def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
        
    '''try:
            cart=json.loads(request.COOKIES['cart'])
    except:
        cart = {}
        print('Cart:',cart)
        items=[]
        order={'get_cart_total':0,'get_cart_items':0, 'shipping':False}
        cartItems=order['get_cart_items']

        for i in cart:
            try:
                cartItems += cart[i]["quantity"]


                product = Product.objects.get(id=i)
                total = (product.price * cart[i]["quantity"])
                order['get_cart_total'] += total
                order['get_cart_items'] += cart[i]["quantity"]

                item = {
                    'product':{
                        'id':product.id,
                        'name':product.name,
                        'price':product.price,
                        'imageURL':product.imageURL,
                        },
                    'quantity':cart[i]["quantity"],
                    'get_total':total
                    }
                items.append(item)

                if product.digital == False:
                    order['shipping'] = True
            except:
                pass'''


    context={'items':items,'order':order,'cartItems':cartItems}
    return render(request,'store/cart.html',context)




def checkout(request):
    
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
        
    context={'items':items,'order':order,'cartItems':cartItems}
    return render(request,'store/checkout.html',context)

def about(request):
    return render(request,'store/about.html')

def contact(request):
    return render(request,'store/contact.html')

def updateItem(request):
    data=json.loads(request.body)
    productId=data['productId']
    action=data['action']

    print('Action:',action)
    print('productId:',productId)

    customer=request.user.customer
    product=Product.objects.get(id=productId)
    order,created=Order.objects.get_or_create(customer=customer,complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order,product=product)

    if action =='add':
        orderItem.quantity=(orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity=(orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity<=0:
        orderItem.delete()

    return JsonResponse('Item was added',safe=False)

#from django.views.decorators.csrf import csrf_exempt

#@csrf_exempt

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        
    
      
    else:
        customer,order=guestOrder(request,data)

    total = float(data['form']['total'])
    order.transaction_id=transaction_id
    

    if total == float(order.get_cart_total):
        order.complete = True
        order.save()


    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    

    return JsonResponse('Payment complete!',safe=False)