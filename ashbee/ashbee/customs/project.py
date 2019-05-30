def project_save(doc, method):
    _update_total_varation(doc)


def _update_total_varation(doc):
    ashbee_total_variation = 0.0

    for variation in doc.ashbee_variations:
        ashbee_total_variation = ashbee_total_variation + variation.amount

    doc.ashbee_total_variation = ashbee_total_variation
