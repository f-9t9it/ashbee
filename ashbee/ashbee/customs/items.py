

def item_save(doc, d):
	doc.weight_per_unit = 0.0
	if doc.ashbee_bar:
		doc.weight_per_unit = doc.ashbee_weight