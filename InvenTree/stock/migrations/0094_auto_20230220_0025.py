# Generated by Django 3.2.18 on 2023-02-20 00:25

import logging

from django.core.exceptions import FieldError
from django.db import migrations

logger = logging.getLogger('inventree')


def fix_purchase_price(apps, schema_editor):
    """Data migration for fixing historical issue with StockItem.purchase_price field.

    Ref: https://github.com/inventree/InvenTree/pull/4373

    Due to an existing bug, if a PurchaseOrderLineItem was received,
    which had:

    a) A SupplierPart with a non-unity pack size
    b) A defined purchase_price

    then the StockItem.purchase_price was not calculated correctly!

    Specifically, the purchase_price was not divided through by the pack_size attribute.

    This migration fixes this by looking through all stock items which:

    - Is linked to a purchase order
    - Have a purchase_price field
    - Are linked to a supplier_part
    - We can determine correctly that the calculation was misapplied
    """

    StockItem = apps.get_model('stock', 'stockitem')

    items = StockItem.objects.exclude(
        purchase_order=None
    ).exclude(
        supplier_part=None
    ).exclude(
        purchase_price=None
    )

    try:
        items = items.exclude(supplier_part__pack_size=1)
    except FieldError:
        pass

    n_updated = 0

    for item in items:
        # Grab a reference to the associated PurchaseOrder
        # Trying to find an absolute match between this StockItem and an associated PurchaseOrderLineItem
        po = item.purchase_order
        for line in po.lines.all():
            # SupplierPart match
            if line.part == item.supplier_part:
                # Unit price matches original PurchaseOrder (and is thus incorrect)
                if item.purchase_price == line.purchase_price:
                    item.purchase_price /= item.supplier_part.pack_size
                    item.save()

                    n_updated += 1

    if n_updated > 0:
        logger.info(f"Corrected purchase_price field for {n_updated} stock items.")


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0093_auto_20230217_2140'),
    ]

    operations = [
        migrations.RunPython(
            fix_purchase_price,
            reverse_code=migrations.RunPython.noop,
            elidable=True,
        )
    ]
