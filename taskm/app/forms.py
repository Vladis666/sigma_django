from django import forms
from .models import Sale, Employee, Product

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['employee', 'product', 'quantity', 'date']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

class SalesFilterForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label="Від")
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label="До")
    employee = forms.ModelChoiceField(queryset=Employee.objects.all(), required=False, empty_label="Всі працівники")
    product = forms.ModelChoiceField(queryset=Product.objects.all(), required=False, empty_label="Всі товари")