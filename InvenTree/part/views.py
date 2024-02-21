"""Django views for interacting with Part app."""

from decimal import Decimal

from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from common.models import InvenTreeSetting
from InvenTree.helpers import str2bool
from InvenTree.views import AjaxView

from . import forms as part_forms
from .bom import ExportBom, IsValidBOMFormat, MakeBomTemplate
from .models import Part


class BomUploadTemplate(AjaxView):
    """Provide a BOM upload template file for download.

    - Generates a template file in the provided format e.g. ?format=csv
    """

    def get(self, request, *args, **kwargs):
        """Perform a GET request to download the 'BOM upload' template."""
        export_format = request.GET.get('format', 'csv')

        return MakeBomTemplate(export_format)


class BomDownload(AjaxView):
    """Provide raw download of a BOM file.

    - File format should be passed as a query param e.g. ?format=csv
    """

    role_required = 'part.view'

    model = Part

    def get(self, request, *args, **kwargs):
        """Perform GET request to download BOM data."""
        part = get_object_or_404(Part, pk=self.kwargs['pk'])

        export_format = request.GET.get('format', 'csv')

        cascade = str2bool(request.GET.get('cascade', False))

        parameter_data = str2bool(request.GET.get('parameter_data', False))

        substitute_part_data = str2bool(request.GET.get('substitute_part_data', False))

        stock_data = str2bool(request.GET.get('stock_data', False))

        supplier_data = str2bool(request.GET.get('supplier_data', False))

        manufacturer_data = str2bool(request.GET.get('manufacturer_data', False))

        pricing_data = str2bool(request.GET.get('pricing_data', False))

        levels = request.GET.get('levels', None)

        if levels is not None:
            try:
                levels = int(levels)

                if levels <= 0:
                    levels = None

            except ValueError:
                levels = None

        if not IsValidBOMFormat(export_format):
            export_format = 'csv'

        return ExportBom(
            part,
            fmt=export_format,
            cascade=cascade,
            max_levels=levels,
            parameter_data=parameter_data,
            stock_data=stock_data,
            supplier_data=supplier_data,
            manufacturer_data=manufacturer_data,
            pricing_data=pricing_data,
            substitute_part_data=substitute_part_data,
        )

    def get_data(self):
        """Return a custom message."""
        return {'info': 'Exported BOM'}


class PartPricing(AjaxView):
    """View for inspecting part pricing information."""

    model = Part
    ajax_template_name = 'part/part_pricing.html'
    ajax_form_title = _('Part Pricing')
    form_class = part_forms.PartPriceForm

    role_required = ['sales_order.view', 'part.view']

    def get_quantity(self):
        """Return set quantity in decimal format."""
        return Decimal(self.request.POST.get('quantity', 1))

    def get_part(self):
        """Return the Part instance associated with this view."""
        try:
            return Part.objects.get(id=self.kwargs['pk'])
        except Part.DoesNotExist:
            return None

    def get_pricing(self, quantity=1, currency=None):
        """Returns context with pricing information."""
        if quantity <= 0:
            quantity = 1

        # TODO - Capacity for price comparison in different currencies
        currency = None

        # Currency scaler
        scaler = Decimal(1.0)

        part = self.get_part()

        ctx = {'part': part, 'quantity': quantity, 'currency': currency}

        if part is None:
            return ctx

        # Supplier pricing information
        if part.supplier_count > 0:
            buy_price = part.get_supplier_price_range(quantity)

            if buy_price is not None:
                min_buy_price, max_buy_price = buy_price

                min_buy_price /= scaler
                max_buy_price /= scaler

                min_unit_buy_price = round(min_buy_price / quantity, 3)
                max_unit_buy_price = round(max_buy_price / quantity, 3)

                min_buy_price = round(min_buy_price, 3)
                max_buy_price = round(max_buy_price, 3)

                if min_buy_price:
                    ctx['min_total_buy_price'] = min_buy_price
                    ctx['min_unit_buy_price'] = min_unit_buy_price

                if max_buy_price:
                    ctx['max_total_buy_price'] = max_buy_price
                    ctx['max_unit_buy_price'] = max_unit_buy_price

        # BOM pricing information
        if part.bom_count > 0:
            use_internal = InvenTreeSetting.get_setting(
                'PART_BOM_USE_INTERNAL_PRICE', False
            )
            bom_price = part.get_bom_price_range(quantity, internal=use_internal)
            purchase_price = part.get_bom_price_range(quantity, purchase=True)

            if bom_price is not None:
                min_bom_price, max_bom_price = bom_price

                min_bom_price /= scaler
                max_bom_price /= scaler

                if min_bom_price:
                    ctx['min_total_bom_price'] = round(min_bom_price, 3)
                    ctx['min_unit_bom_price'] = round(min_bom_price / quantity, 3)

                if max_bom_price:
                    ctx['max_total_bom_price'] = round(max_bom_price, 3)
                    ctx['max_unit_bom_price'] = round(max_bom_price / quantity, 3)

            if purchase_price is not None:
                min_bom_purchase_price, max_bom_purchase_price = purchase_price

                min_bom_purchase_price /= scaler
                max_bom_purchase_price /= scaler
                if min_bom_purchase_price:
                    ctx['min_total_bom_purchase_price'] = round(
                        min_bom_purchase_price, 3
                    )
                    ctx['min_unit_bom_purchase_price'] = round(
                        min_bom_purchase_price / quantity, 3
                    )

                if max_bom_purchase_price:
                    ctx['max_total_bom_purchase_price'] = round(
                        max_bom_purchase_price, 3
                    )
                    ctx['max_unit_bom_purchase_price'] = round(
                        max_bom_purchase_price / quantity, 3
                    )

        # internal part pricing information
        internal_part_price = part.get_internal_price(quantity)
        if internal_part_price is not None:
            ctx['total_internal_part_price'] = round(internal_part_price, 3)
            ctx['unit_internal_part_price'] = round(internal_part_price / quantity, 3)

        # part pricing information
        part_price = part.get_price(quantity)
        if part_price is not None:
            ctx['total_part_price'] = round(part_price, 3)
            ctx['unit_part_price'] = round(part_price / quantity, 3)

        return ctx

    def get_initials(self):
        """Returns initials for form."""
        return {'quantity': self.get_quantity()}

    def get(self, request, *args, **kwargs):
        """Perform custom GET action for this view."""
        init = self.get_initials()
        qty = self.get_quantity()

        return self.renderJsonResponse(
            request, self.form_class(initial=init), context=self.get_pricing(qty)
        )

    def post(self, request, *args, **kwargs):
        """Perform custom POST action for this view."""
        currency = None

        quantity = self.get_quantity()

        # Retain quantity value set by user
        form = self.form_class(initial=self.get_initials())

        # TODO - How to handle pricing in different currencies?
        currency = None

        # check if data is set
        try:
            data = self.data
        except AttributeError:
            data = {}

        # Always mark the form as 'invalid' (the user may wish to keep getting pricing data)
        data['form_valid'] = False

        return self.renderJsonResponse(
            request, form, data=data, context=self.get_pricing(quantity, currency)
        )
