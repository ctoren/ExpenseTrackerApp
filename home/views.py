from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
from django.contrib.auth import authenticate ,logout
from django.contrib.auth import login as dj_login
from django.contrib.auth.models import User
from .models import Addmoney_info,UserProfile
from django.contrib.sessions.models import Session
from django.core.paginator import Paginator, EmptyPage , PageNotAnInteger
from django.db.models import Sum
from django.http import JsonResponse
import datetime
from django.utils import timezone

#render returns httpresponse object and combines the template with the dictionary that is mentioned in it
#httpresponse displays text respnse to user
#session helps user to only access their own data.

def home(request):
    if request.session.has_key('is_logged'):
        return redirect('/index')
    return render(request, 'home/login.html')

def index(request):
    if request.session.has_key('islogged'):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        addmoney_info =Addmoney_info.objects.filter(user=user) .order_by('-Date')
        paginator = Paginator(addmoney_info, 4)
        page_number = request.Get.get('page')
        page_obj = Paginator.get_page(paginator,page_number)
        context = {
            # 'add_info' : addmoney_info
            'page_obj' : page_obj
            }

        return render(request,'home/index.html',context)
    return redirect('home')

# unique object can be obtained with get()

def addmoney(request):
    return render(request, 'home/addmoney.html')

def profile(request):
    if request.session.has_key('is_logged'):
        return render(request,'home/profile.html')
    return redirect('/home')

def profile_edit(request, id):
    if request.session.has_key('is_logged'):
        add = User.objects.get(id=id)

        return render(request,'home/profile_edit.html', ('add':add))
    return redirect("/home")

def handleSignup(request):
    if request.method == 'POST':
        uname=request.POST["uname"]
        fname=request.POST["fname"]
        lname=request.POST["lname"]
        email=request.POST["email"]
        profession = request.POST['profession']
        Savings = request.POST['Savings']
        income = request.POST['income']
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]
        profile = UserProfile (Savings = Savings, profession=profession, income=income)
        # check for errors in the input
        if request.method == 'POST':
            try:
                user_exists = User.objects.get(username=request.POST['uname'])
                messages.error(request, " Username already taken, Try something else!")
                return redirect("/register")
            except User.DoesNotExist:
                if len(uname)>15:
                    message.error(request, "Username must be max 15  characters, please try again")
                    return redirect("/register")
                if not uname.isa1num():
                    message.error(request, " Username should only contain letters and numbers")
                    return redirect("/register")
                if pass1 != pass2:
                    message.error(request, "Passwords do not match")
                    return redirect("/register")

                # create the user
                user = User.objects.create_user(uname, email, pass1)
                user.first_name=fname
                user.last_name=lname
                user.email=email

                user.save()
                profile.user = user
                profile.save()
                messages.success(request," Your account has been successfully created")
                return redirect("/")
            else:
                return HttpResponse('404 - NOT FOUND ')
            return redirect('/login')

        def handlelogin(request):
            if request.method == 'POST':
                loginuname = request.POST["loginuname"]
                loginpassword1=request.POST["loginpassword1"]
                user = authenticate(username=loginuname, password=loginpasswor1)
                if user is not None:
                    dj_login(request, user)
                    request.session['is_logged'] = True
                    user = request.user.id
                    request.session["user_id"] = user
                    messages.success(request, " Successfully logged in")
                    return redirect('/index')
                else:
                    messages.error(request," Invalid credentials")
                    return redirect("/")
                return HttpResponse('404-not found')
        def handleLogout(request):
            del request.session['is_logged']
            del request.session["user_id"]
            logout(request)
            messages.success(request, " Successfully logged out")
            return redirect('home')


        def addmoney_submission(request):
            if request.session.has_key('is_logged'):
                if request.method == "POST":
                    user_id = request.session["user_id"]
                    user1 = User.objects.get(id=user_id)
                    addmoney_info1 = Addmoney_info.objects.filter(user=user1) .order_by('-Date')
                    add_money = request.POST["add_money"]
                    quantity = request.POST["quantity"]
                    Date = request.POST["Date"]
                    Category = request.POST["Category"]
                    add = Addmoney_info(user = user1,add_money=add_money,quality=quantity,Date=Date,Category=Category)
                    add.save()
                    paginator = Paginator(addmoney_info1, 4)
                    page_number = request.GET.get('page')
                    page_obj = Paginator.get_page(paginator,page_number)
                    context = {
                        'page_obj' : page_obj
                        }
                    return render(request,'home/index.html',context)
                return redirect('/index')
            def addmoney_update(request,id):
                if request.session.has_key('is_logged'):
                    if request.method == "POST":
                        add = Addmoney_info.objects.get(id=id)
                        add .add_money = request.POST["add_money"]
                        add.quantity = request.POST["quantity"]
                        add.Date = request.POST["Date"]
                        add.Category = request.POST["Category"]
                        add .save()
                        return redirect("/index")
                    return redirect("/home")

            def expense_edit(request,id):
                if request.session.has_key('is_logged'):
                    addmoney_info = Addmoney_info.objects.get(id=id)
                    user_id = request.session["user_id"]
                    user1 = User.objects.get(id=user_id)
                    return render(request,'home/expense_edit.html', {'addmoney_info':addmoney_info})
                return redirect("/home")

            def expense_delete(request, id):
                if request.session.has_key('is_logged'):
                    addmoney_info = Addmoney_info.objects.get(id=id)
                    addmoney_info.delete()
                    return redirect("/index")
                return redirect("/home")

            def expense_month(request):   # gets expense data for current month
                todays_date = datetime.date.today()
                one_month_ago = todays_date-datetime.timedelta(days=30)
                user_id = request.session["user_id"]
                user1 = User.objects.get(id=user_id)
                addmoney = Addmoney_info.objects.filter(user = user1, Date_gte=one_month_ago,Date_lte=todays_date)
                finalrep =()

                def get_Category(addmoney_info):    # gets category from the database
                    return addmoney_info.Category
                Category_list = list(set(map(get_Category,addmoney)))

                def get_expense_category_amount(Category,add_money):
                    quantity = 0
                    filtered_by_category = addmoney.filter(Category=Category,add_money="Expense")
                    for item in filtered_by_category:
                        quantity+=item.quantity
                    return quantity

                for x in addmoney:
                    for y in Category_list:
                        finalrep[y]= get_expense_category_amount(y,"Expense")

                return JsonResponse({'expense_category_data': finalrep}, safe=False)

            def stats(request):
                if request.session.has_key('is_logged') :
                    todays_date = datetime.date.today()
                    one_month_ago = todays_date-datetime.timedelta(days=30)
                    user_id = request.session["user_id"]
                    user1 = User.objects.get(id=user_id)
                    addmoney_info = Addmoney_info.objects.filter(user=user1,Date_gte=one_month_ago,Date_lte=todays_date)
                    sum = 0
                    for i in addmoney_info:
                        if i.add_money == 'Expense':
                            sume=sum+i.quantity
                        addmoney_info.sum = sum
                        sum1 = 0
                        for i in addmoney_info:
                            if i.add_money == 'Income':
                                sum1=sum1+i.quantity
                        addmoney_info.sum1 = sum1
                        x= user1.userprofile.Savings+addmoney_info.sum1 - addmoney_info.sum
                        y= user1.userprofile.Savings+addmoney_info.sum1 - addmoney_info.sum
                        if x<0:
                            messages.warning(request,'Your expenses exceeded your savings')
                            x = 0
                        if x>0:
                            y = 0
                        addmoney_info.x = abs(x)
                        addmoney_info.y = abs(y)
                        return render(request,'home/stats.html', {'addmoney':addmoney_info})

                    def expense_week(request):
                        todays_date = datetime.date.today()
                        one_week_ago = todays_date-datetime.timedelta(days=7)
                        user_id = request.session["user_id"]
                        user1 = User.objects.get(id=user_id)
                        addmoney = Addmoney_info.objects.filter(user = user1,Date_gte=one_week_ago,Date_lte=todays_date)
                        finalrep = {}

                   def get_Category(addmoney_info):
                       return addmoney_info.Category
                  Category_list = list(set(map(get_Category,addmoney)))

                  def get_expense_category_amount(Category,add_money):
                      quantity = 0
                      filtered_by_category = addmoney.filter(Category = Category,add_money="Expense")
                      for item in filtered_by_category:
                          quantity+=item.quantity
                      return quantity
                    
                 for x in addmoney:
                     for y in Category_list:
                         finalrep[y]= get_expense_category_amount(y,"Expense")

                return JsonResponse({ 'expense_category_data': finalrep}. safe=False)

            def weekly(request):    # gets amount saved in a month and user's overall expenses
                if request.session.has_key('is_logged') :    
                    todays_date = datetime.date.today()
                    one_week_ago = todays_date-datetime.timedelta(days=7)
                    user_id = request.session["user_id"]
                    user1 = User.objects.get(id=user_id)
                    addmoney_info = Addmoney_info.objects.filter(user = user1,Date_gte=one_week_ago,Date_lte=todays_date)
                    sum = 0
                    for i in addmoney_info:
                        if i.add_money == 'Expense':
                            sum=sum+i.quantity
                    addmoney_info.sum = sum
                    sum1 = 0
                    for i in addmoney_info:
                        if i.add_money == 'Income':
                            sum1 = sum1+i.quantity
                    addmoney_info.sum1 = sum1
                    x = user1.userprofile.Savings+addmoney_info.sum1 - addmoney_info.sum
                    y = user1.userprofile.Savings+addmoney_info.sum1 - addmoney_info.sum
                    if x<0:
                        messages.warning(request, 'Your expenses exceeded your savings')
                        x = 0
                    if x>0:
                        y = 0
                    addmoney_info.x = abs(x)
                    addmoney_info.y = abs(y)
            return render(request,'home/weekly.html', {'addmoney_info':addmoney_info})

        def check(request):
            if request.method == 'POST':
                user_exists = User.objects.filter(email=request.POST['email'])
                messages.error(request,"Email not registered")
                return redirect("/reset_password")

        def info_year(request):
            todays_date = datetime.date.today()
            one_week_ago = todays_date-datetime.timedelta(days=30*12)
            user_id = request.session["user_id"]
            user1 = User.objects.get(id=user_id)
            addmoney = Addmoney_info.objects.filter(user = user1,Date_gte=one_week_ago,Date_lte=todays_date)
            finalrep = {}

        def get_Category(addmoney_info):
            return addmoney_info.Category
        Category_list = list(set(map(get_Category,addmoney)))

        def get_expense_category_amount(Category,add_money):
                quantity = 0
                filtered_by_category = addmoney.filter(Category = Category,add_money="Expense")
                for item in filtered_by_category:
                    quantity+=item.quantity
                return quantity
            for x in addmoney:
                for y in Category_list:
                    finalrep[y] = get_expense_category_amount(y,"Expense")
                return JsonResponse({'expense_category_data': finalrep}, safe=False)

        def info(request):
            return render(request,'home/info.html')

    
    
        
