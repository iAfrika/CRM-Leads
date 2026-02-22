from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product
from .forms import ProductForm

@login_required
def product_list(request):
    products = Product.objects.filter(status='active').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page_obj = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'page_obj': page_obj,
        'app_name': 'products'
    }
    return render(request, 'products/product_list.html', context)

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    context = {
        'product': product,
        'app_name': 'products'
    }
    return render(request, 'products/product_detail.html', context)

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            messages.success(request, 'Product created successfully.')
            return redirect('products:product_detail', pk=product.pk)
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'app_name': 'products',
        'action': 'Create'
    }
    return render(request, 'products/product_form.html', context)

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            updated_product = form.save(commit=False)
            updated_product.updated_by = request.user
            updated_product.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('products:product_detail', pk=pk)
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'app_name': 'products',
        'action': 'Update'
    }
    return render(request, 'products/product_form.html', context)

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.status = 'discontinued'
        product.updated_by = request.user
        product.save()
        messages.success(request, 'Product deleted successfully.')
        return redirect('products:product_list')
    
    context = {
        'product': product,
        'app_name': 'products'
    }
    return render(request, 'products/product_confirm_delete.html', context)