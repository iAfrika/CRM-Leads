from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category
from .forms import CategoryForm

@login_required
def category_list(request):
    categories = Category.objects.filter(is_active=True)
    context = {
        'categories': categories,
        'app_name': 'products'
    }
    return render(request, 'products/category_list.html', context)

@login_required
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    products = category.products.filter(status=True)
    context = {
        'category': category,
        'products': products,
        'app_name': 'products'
    }
    return render(request, 'products/category_detail.html', context)

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('products:category_detail', pk=category.pk)
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'app_name': 'products',
        'action': 'Create'
    }
    return render(request, 'products/category_form.html', context)

@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('products:category_detail', pk=pk)
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
        'app_name': 'products',
        'action': 'Update'
    }
    return render(request, 'products/category_form.html', context)

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.is_active = False
        category.save()
        messages.success(request, 'Category deleted successfully.')
        return redirect('products:category_list')
    
    context = {
        'category': category,
        'app_name': 'products'
    }
    return render(request, 'products/category_confirm_delete.html', context)