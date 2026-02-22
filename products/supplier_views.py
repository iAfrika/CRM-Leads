from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Supplier
from .forms import SupplierForm

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'products/supplier_list.html', {'suppliers': suppliers})

@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    return render(request, 'products/supplier_detail.html', {'supplier': supplier})

@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, 'Supplier created successfully.')
            return redirect('products:supplier_detail', pk=supplier.pk)
    else:
        form = SupplierForm()
    return render(request, 'products/supplier_form.html', {'form': form, 'action': 'Create'})

@login_required
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, 'Supplier updated successfully.')
            return redirect('products:supplier_detail', pk=supplier.pk)
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'products/supplier_form.html', {'form': form, 'action': 'Update'})

@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Supplier deleted successfully.')
        return redirect('products:supplier_list')
    return render(request, 'products/supplier_confirm_delete.html', {'supplier': supplier})