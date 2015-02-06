from django.forms import ModelForm, BaseInlineFormSet
from django.forms.models import inlineformset_factory

from .models import (
    Organization,
    TaxRate,
    Estimate,
    EstimateLine,
    Invoice,
    InvoiceLine,
    Bill,
    BillLine,
    Payment)
from .utils import organization_manager
from accounting.apps.people.models import Client
from accounting.apps.people.forms import (
    UserChoices,
    UserMultipleChoices)

from django_select2.fields import (
    AutoModelSelect2Field,
    AutoModelSelect2MultipleField)


class RequiredFirstInlineFormSet(BaseInlineFormSet):
    """
    Used to make empty formset forms required
    See http://stackoverflow.com/questions/2406537/django-formsets-\
        make-first-required/4951032#4951032
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(self.forms) > 0:
            first_form = self.forms[0]
            first_form.empty_permitted = False


class ClientForOrganizationChoices(AutoModelSelect2Field):
    queryset = Client.objects.all()
    search_fields = (
        'name__icontains',
    )

    def get_results(self, request, *args, **kwargs):
        self.__request = request
        return super().get_results(request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)

        # build the restriction
        # NB: we are forced to build the logic here because of the way
        #     django-select2 fields are made... sadely
        request = self.__request
        orga = organization_manager.get_selected_organization(request)
        del self.__request
        qs = qs.filter(organization=orga)

        return qs


class OrganizationForm(ModelForm):
    members = UserMultipleChoices(required=False)

    class Meta:
        model = Organization
        fields = (
            "display_name",
            "legal_name",
            "members",
        )


class TaxRateForm(ModelForm):
    class Meta:
        model = TaxRate
        fields = (
            "name",
            "rate",
        )


class RestrictLineFormToOrganizationMixin(object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance:
            if isinstance(instance, InvoiceLine):
                organization = instance.invoice.organization
            elif isinstance(instance, BillLine):
                organization = instance.bill.organization
            else:
                raise NotImplementedError("The mixin has been applied to a "
                                          "form model that is not supported")
            self.fields['tax_rate'].queryset = organization.tax_rates.all()


class EstimateForm(ModelForm):
    client = ClientForOrganizationChoices()

    class Meta:
        model = Estimate
        fields = (
            "number",
            "client",

            "draft",
            "sent",
            "paid",
            "date_issued",
            "date_dued",
        )


class EstimateLineForm(RestrictLineFormToOrganizationMixin,
                       ModelForm):
    class Meta:
        model = EstimateLine
        fields = (
            "label",
            "description",
            "unit_price_excl_tax",
            "quantity",
            "tax_rate",
        )


EstimateLineFormSet = inlineformset_factory(Estimate,
                                            EstimateLine,
                                            form=EstimateLineForm,
                                            formset=RequiredFirstInlineFormSet,
                                            min_num=1,
                                            extra=0)


class InvoiceForm(ModelForm):
    client = ClientForOrganizationChoices()

    class Meta:
        model = Invoice
        fields = (
            "number",
            "client",

            "draft",
            "sent",
            "paid",
            "date_issued",
            "date_dued",
        )


class InvoiceLineForm(RestrictLineFormToOrganizationMixin,
                      ModelForm):
    class Meta:
        model = InvoiceLine
        fields = (
            "label",
            "description",
            "unit_price_excl_tax",
            "quantity",
            "tax_rate",
        )


InvoiceLineFormSet = inlineformset_factory(Invoice,
                                           InvoiceLine,
                                           form=InvoiceLineForm,
                                           formset=RequiredFirstInlineFormSet,
                                           min_num=1,
                                           extra=0)


class BillForm(ModelForm):
    client = ClientForOrganizationChoices()

    class Meta:
        model = Bill
        fields = (
            "number",
            "client",

            "draft",
            "sent",
            "paid",
            "date_issued",
            "date_dued",
        )


class BillLineForm(RestrictLineFormToOrganizationMixin,
                   ModelForm):
    class Meta:
        model = BillLine
        fields = (
            "label",
            "description",
            "unit_price_excl_tax",
            "quantity",
            "tax_rate",
        )


BillLineFormSet = inlineformset_factory(Bill,
                                        BillLine,
                                        form=BillLineForm,
                                        formset=RequiredFirstInlineFormSet,
                                        min_num=1,
                                        extra=0)


class PaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = (
            "amount",
            "reference",
            "detail",
            "date_paid",
        )
